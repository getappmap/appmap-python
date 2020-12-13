from functools import partial, wraps
import inspect
import logging
import sys
from .event import Event, CallEvent, ReturnEvent, ExceptionEvent


def split_method_name(method):
    """ Split method __qualname__ into class_name, func_name """
    return ([''] * 1 + method.__qualname__.rsplit('.', 1))[-2:]


def wrap(func):
    """return a wrapped func"""
    logging.info('hooking %s', func)

    defined_class, method_id = split_method_name(func)
    path = inspect.getsourcefile(func)
    __, lineno = inspect.getsourcelines(func)
    static = False
    new_call_event = partial(CallEvent,
                             defined_class=defined_class,
                             method_id=method_id,
                             path=path,
                             lineno=lineno,
                             static=static)

    @wraps(func)
    def run(*args, **kwargs):
        from .recording import Recorder
        recorder = Recorder()
        if not recorder.enabled:
            return func(*args, **kwargs)
        call_event = new_call_event()
        if not isinstance(call_event, Event):
            raise TypeError
        call_event_id = call_event.id
        recorder.add_event(call_event)
        try:
            ret = func(*args, **kwargs)
            return_event = ReturnEvent(parent_id=call_event_id)
            if not isinstance(return_event, Event):
                raise TypeError
            recorder.add_event(return_event)
            return ret
        except:  # noqa: E722
            recorder.add_event(ExceptionEvent(parent_id=call_event_id, exc_info=sys.exc_info))
            raise
    return run


def in_set(method, which):
    class_name, func_name = split_method_name(method)
    logging.debug(('  class_name %s'
                   ' funcname %s'
                   ' which %s'),
                  class_name,
                  func_name,
                  which)
    if func_name.startswith('__'):
        return False
    return (class_name in which
            or method.__qualname__ in which)
