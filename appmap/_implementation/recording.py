"""Capture recordings of python code"""

import builtins
from functools import partial, WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES
import inspect
import logging
import orjson

from .event import serialize_event
from .filters import NullFilter, BuiltinFilter, ConfigFilter
from . import metadata


class Recorder:
    """ Singleton Recorder class """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logging.debug('Creating the Recorder object')
            cls._instance = super(Recorder, cls).__new__(cls)

            # Put any __init__ here.
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if self.__getattribute__('_initialized'):  # keep pylint happy
            return
        self._initialized = True
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


class Recording:
    def __init__(self):
        self.recorder = Recorder()
        self.recorder.add_filter(BuiltinFilter.load_config())
        self.recorder.add_filter(ConfigFilter.load_config())

        self.events = []
        self.old_import = None

    def __enter__(self):
        self.old_import = builtins.__import__
        builtins.__import__ = partial(Recorder.do_import, self.recorder, self.old_import)

        for attr in WRAPPER_ASSIGNMENTS:
            try:
                value = getattr(self.old_import, attr)
            except AttributeError:
                pass
            else:
                setattr(builtins.__import__, attr, value)
        for attr in WRAPPER_UPDATES:
            getattr(builtins.__import__, attr).update(getattr(self.old_import, attr, {}))

        self.recorder.start_recording()

    def __exit__(self, exc_type, exc_value, traceback):
        self.events = self.recorder.stop_recording()
        builtins.__import__ = self.old_import
        return False

    def dumps(self):
        return orjson.dumps(
            {
                'metadata': metadata.Metadata.dump(),
                'events': self.events
            },
            default=serialize_event
        )
