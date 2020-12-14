"""Capture recordings of python code"""

import inspect
import logging
import sys
import types
from abc import ABC, abstractmethod
from functools import wraps

from . import env
from . import utils

class Recording:
    def __init__(self):
        self.events = []

    def start(self):

        if not env.enabled():
            return

        recorder.start_recording()

    def stop(self):
        if not env.enabled():
            return False

        self.events = recorder.stop_recording()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        return False


class Filter(ABC):
    def __init__(self, next):
        self.next = next

    @abstractmethod
    def filter(self, class_):
        """
        Determine whether the given class should have its methods
        instrumented.  Return True if it should be, False if it should
        not be, or call the next filter if this filter can't decide.
        """
        pass

    @abstractmethod
    def wrap(self, method_attr, method):
        """
        Determine whether a method should be wrapped.  method_attr is
        the original __dict__ entry for the method, method is the
        value returned by getattr.  Returns a wrapped method if
        appropriate, or the original method otherwise.
        """
        pass


class NullFilter(Filter):
    def filter(self, class_):
        return False

    def wrap(self, method):
        return method


def get_classes(module):
    return [v for __, v in module.__dict__.items() if inspect.isclass(v)]


def get_members(class_):
    """
    Get the function members of the given class.  Unlike
    inspect.getmembers, this function only calls getattr on functions,
    to avoid potential side effects.

    Returns a list of tuples of the form (key, dict_value, attr_value):
      * key is the attribute name
      * dict_value is class_.__dict__[key]
      * and attr_value is getattr(class_, key)
    """
    def is_member_func(m):
        return (inspect.isfunction(m)
                or inspect.ismethod(m)
                or utils.is_static_method(m)
                or utils.is_class_method(m))

    ret = []
    for k, v in class_.__dict__.items():
        if not is_member_func(v):
            continue
        ret.append((k, v, getattr(class_, k)))
    return ret

class Recorder:
    def __init__(self):
        self.enabled = False
        self.filter_stack = [NullFilter]
        self.filter_chain = []
        self._events = []

    def use_filter(self, filter_class):
        self.filter_stack.append(filter_class)

    def start_recording(self):
        logging.debug('Recorder.start_recording')
        self.enabled = True

    def stop_recording(self):
        logging.debug('Recorder.stop_recording')
        self.enabled = False
        return self._events

    def add_event(self, event):
        """
        Add an event to the current recording
        """
        self._events.append(event)

    def events(self):
        """
        Get the events from the current recording
        """
        return self._events

    def do_import(self, *args, **kwargs):
        mod = args[0]
        logging.debug('do_import, args %s kwargs %s', args, kwargs)
        if not self.filter_chain:
            logging.debug('  filter_stack %s', self.filter_stack)
            self.filter_chain = self.filter_stack[0](None)
            for filter_ in self.filter_stack[1:]:
                self.filter_chain = filter_(self.filter_chain)
                logging.debug('  self.filter chain: %s', self.filter_chain)

        if mod.__name__.startswith('appmap'):
            return

        classes = get_classes(mod)
        logging.debug(('  classes %s'
                       ' inspect.getmembers(mod, inspect.isclass) %s'),
                      classes,
                      inspect.getmembers(mod, inspect.isclass))
        for class_ in classes:
            logging.debug('  class_ %s', class_)
            if not self.filter_chain.filter(class_):
                continue

            logging.debug('  looking for members')
            functions = get_members(class_)
            logging.debug('  functions %s', functions)
            for func_name, func_attr, func in functions:
                logging.debug('  func %s inspect.isfunction(func) %s',
                              func, inspect.isfunction(func))
                new_func = self.filter_chain.wrap(func_attr, func)
                if new_func != func:
                    if utils.is_static_method(func_attr):
                        new_func = staticmethod(new_func)
                    setattr(class_, func_name, new_func)


recorder = Recorder()


def wrap_exec_module(exec_module):
    @wraps(exec_module)
    def wrapped_exec_module(*args, **kwargs):
        logging.debug(('exec_module %s'
                       ' exec_module.__name__ %s'
                       ' args %s'
                       ' kwargs %s'),
                      exec_module,
                      exec_module.__name__,
                      args,
                      kwargs)
        exec_module(*args, **kwargs)
        recorder.do_import(*args, **kwargs)
    return wrapped_exec_module


def wrap_find_spec(find_spec):
    @wraps(find_spec)
    def wrapped_find_spec(*args, **kwargs):
        spec = find_spec(*args, **kwargs)
        if spec is not None:
            if getattr(spec.loader, "exec_module", None) is not None:
                loader = spec.loader
                loader.exec_module = wrap_exec_module(loader.exec_module)
            else:
                logging.warning("%s doesn't have exec_module", spec.loader)
        return spec
    return wrapped_find_spec


if env.enabled():
    # import configuration so the filter stack will get initialized
    from . import configuration  # noqa: F401
    for h in sys.meta_path:
        if getattr(h, 'find_spec', None) is not None:
            logging.debug('  h.find_spec %s',  h.find_spec)
            h.find_spec = wrap_find_spec(h.find_spec)
