import logging
import sys
import time
from collections import namedtuple
from contextlib import contextmanager

from . import event
from .event import CallEvent
from .recorder import Recorder
from .utils import appmap_tls

logger = logging.getLogger(__name__)


@contextmanager
def recording_disabled():
    tls = appmap_tls()
    tls["instrumentation_disabled"] = True
    try:
        yield
    finally:
        tls["instrumentation_disabled"] = False


def is_instrumentation_disabled():
    return appmap_tls().setdefault("instrumentation_disabled", False)


def track_shallow(fn):
    """
    Check if the function should be skipped because of a shallow rule.
    If not, updates the last rule tracking and return False.

    This works by remembering last matched rule.  This is rather
    simple and the results are not always correct.  For example,
    consider execution flow where code matching another shallow rule
    repeatedly gets called from the code that's already shallow.  It's
    difficult, if at all possible, to generally ensure correctness
    without tracking all execution or analyzing the call stack on each
    call, which is probably too inefficient.

    However, in the most useful case where we're interested in the
    interaction between client code and specific third-party libraries
    while ignoring their internals, it's an effective way of limiting
    appmap size.  If you want anything more complicated and can take
    the performance hit, your best bet is to record without shallow
    and postprocess the appmap to your liking.
    """
    tls = appmap_tls()
    rule = getattr(fn, "_appmap_shallow", None)
    logger.debug("track_shallow(%r) [%r]", fn, rule)
    result = rule and tls.get("last_rule", None) == rule
    tls["last_rule"] = rule
    return result


@contextmanager
def saved_shallow_rule():
    """
    A context manager to save and reset the current shallow tracking
    rule around the call to an instrumented function.
    """
    tls = appmap_tls()
    current_rule = tls.get("last_rule", None)
    try:
        yield
    finally:
        tls["last_rule"] = current_rule


_InstrumentedFn = namedtuple(
    "_InstrumentedFn", "fn fntype instrumented_fn make_call_event params"
)


def call_instrumented(f, instance, args, kwargs):
    if (
        (not Recorder.get_enabled())
        or is_instrumentation_disabled()
        or track_shallow(f.instrumented_fn)
    ):
        return f.fn(*args, **kwargs)

    with recording_disabled():
        logger.debug("%s args %s kwargs %s", f.fn, args, kwargs)
        params = CallEvent.set_params(f.params, instance, args, kwargs)
        call_event = f.make_call_event(parameters=params)
    Recorder.add_event(call_event)
    call_event_id = call_event.id
    start_time = time.time()
    try:
        ret = f.fn(*args, **kwargs)
        elapsed_time = time.time() - start_time

        return_event = event.FuncReturnEvent(
            return_value=ret, parent_id=call_event_id, elapsed=elapsed_time
        )
        Recorder.add_event(return_event)
        return ret
    except Exception:  # noqa: E722
        elapsed_time = time.time() - start_time
        Recorder.add_event(
            event.ExceptionEvent(
                parent_id=call_event_id, elapsed=elapsed_time, exc_info=sys.exc_info()
            )
        )
        raise


def instrument(filterable):
    """return an instrumented function"""
    logger.debug("hooking %s", filterable.fqname)
    fn = filterable.obj

    make_call_event = event.CallEvent.make(fn, filterable.fntype)
    params = CallEvent.make_params(filterable)

    # django depends on being able to find the cache_clear attribute
    # on functions. (You can see this by trying to map
    # https://github.com/chicagopython/chypi.org.) Make sure it gets
    # copied from the original to the wrapped function.
    #
    # Going forward, we should consider how to make this more general.
    def instrumented_fn(wrapped, instance, args, kwargs):
        with saved_shallow_rule():
            f = _InstrumentedFn(
                wrapped, filterable.fntype, instrumented_fn, make_call_event, params
            )
            return call_instrumented(f, instance, args, kwargs)

    ret = instrumented_fn
    setattr(ret, "_appmap_wrapped", True)
    return ret
