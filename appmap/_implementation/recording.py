"""Capture recordings of python code"""

import builtins
import inspect
import logging
from contextlib import contextmanager
from functools import partial

class Filter:
    def __init__(self, next_filter):
        self.next_filter = next_filter


class NullFilter(Filter):
    def call(self, method):
        return method


class Recorder:

    def __init__(self):
        self.enabled = False
        self.filter_stack = [NullFilter]
        self._events = []

    def add_filter(self, filter_):
        self.filter_stack.append(filter_)

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

    def do_import(self, import_func, *args, **kwargs):
        logging.debug('do_import, filter_stack %s', self.filter_stack)
        filter_chain = self.filter_stack[0](None)
        for filter_ in self.filter_stack[1:]:
            filter_chain = filter_(filter_chain)
        logging.debug('  filter chain: %s', filter_chain)

        mod = import_func(*args, **kwargs)
        classes = inspect.getmembers(mod, inspect.isclass)
        for __, class_ in classes:
            logging.debug('  class_ %s dir(class_) %s', class_, dir(class_))
            functions = inspect.getmembers(
                class_,
                lambda f: inspect.isfunction(f) or inspect.ismethod(f)
            )
            logging.debug('  functions %s', functions)
            for func_name, func in functions:
                logging.debug('  func %s inspect.isfunction(func) %s',
                              func, inspect.isfunction(func))
                new_func = filter_chain.call(func)
                if new_func != func:
                    setattr(class_, func_name, new_func)
        return mod


recorder = Recorder()


@contextmanager
def _watch_imports():
    """
    context manager to give Recording access to modules as they're
    imported
    """
    old_import = builtins.__import__

    builtins.__import__ = partial(Recorder.do_import, recorder, old_import)
    try:
        yield
    finally:
        builtins.__import__ = old_import


class Recording:
    def __init__(self):
        self.events = []
        self.old_import = None

    def __enter__(self):
        self.old_import = builtins.__import__
        builtins.__import__ = partial(Recorder.do_import, recorder, self.old_import)
        recorder.start_recording()

    def __exit__(self, exc_type, exc_value, traceback):
        self.events = recorder.stop_recording()
        builtins.__import__ = self.old_import
        return False
