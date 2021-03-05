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
        if not Recorder().enabled or is_instrumentation_disabled():
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
