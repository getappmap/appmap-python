from contextlib import contextmanager
from functools import wraps, WRAPPER_ASSIGNMENTS
import logging
import sys
import time

from . import event
from .event import CallEvent
from .recording import Recorder
from .utils import appmap_tls, split_function_name

logger = logging.getLogger(__name__)


@contextmanager
def recording_disabled():
    tls = appmap_tls()
    tls['instrumentation_disabled'] = True
    try:
        yield
    finally:
        tls['instrumentation_disabled'] = False


def is_instrumentation_disabled():
    return appmap_tls().setdefault('instrumentation_disabled', False)


def track_shallow(fn):
    """
    Check if the function should be skipped because of a shallow rule.
    If not, updates the last rule tracking and return False.

    Note this works by remembering last matched rule. This is rather simple
    and the results are not always correct. Consider for example:

        def fun1(): fun2()
        def fun2(): pass

        fun1()
        fun2()

    In this case, the first call to fun2() (from inside fun1()) should be
    skipped, but the second one should not. Since we only track last matched
    rule, we won't notice we're back at toplevel and the second fun2() call
    would be lost.

    There are more corner cases (for example consider execution flow where
    code matching another shallow rule repeatedly gets called from
    the code that's already shallow) and it's difficult, if at all possible, to
    generally ensure correctness without tracking all execution or analyzing
    the call stack on each call, which is probably too inefficient.

    However, in the most useful case where we're interested in the interaction
    between client code and specific third-party libraries while ignoring their
    internals, it's an effective way of limiting appmap size. If you want anything
    more complicated and can take the performance hit, your best bet is to
    record without shallow and postprocess the appmap to your liking.
    """
    tls = appmap_tls()
    rule = getattr(fn, '_appmap_shallow', None)
    logger.debug('track_shallow(%r) [%r]', fn, rule)
    result = rule and tls.get('last_rule', None) == rule
    tls['last_rule'] = rule
    return result


def instrument(fn, fntype):
    """return an instrumented function"""
    logger.debug('hooking %s', '.'.join(split_function_name(fn)))

    make_call_event = event.CallEvent.make(fn, fntype)
    params = CallEvent.make_params(fn)

    # django depends on being able to find the cache_clear attribute
    # on functions. Make sure it gets copied from the original to the
    # wrapped function.
    #
    # Going forward, we should consider how to make this more general.
    @wraps(fn, assigned=WRAPPER_ASSIGNMENTS + tuple(['cache_clear']))
    def instrumented_fn(*args, **kwargs):
        if (
            (not Recorder().enabled)
            or is_instrumentation_disabled()
            or track_shallow(instrumented_fn)
        ):
            return fn(*args, **kwargs)

        with recording_disabled():
            logger.debug('%s args %s kwargs %s', fn, args, kwargs)
            call_event = make_call_event(
                parameters=CallEvent.set_params(params, args, kwargs))
        call_event_id = call_event.id
        Recorder().add_event(call_event)
        start_time = time.time()
        try:
            ret = fn(*args, **kwargs)
            elapsed_time = time.time() - start_time

            return_event = event.FuncReturnEvent(return_value=ret,
                                                 parent_id=call_event_id,
                                                 elapsed=elapsed_time)
            Recorder().add_event(return_event)
            return ret
        except Exception:  # noqa: E722
            elapsed_time = time.time() - start_time
            Recorder().add_event(event.ExceptionEvent(parent_id=call_event_id,
                                                      elapsed=elapsed_time,
                                                      exc_info=sys.exc_info()))
            raise
    setattr(instrumented_fn, '_appmap_wrapped', True)
    return instrumented_fn
