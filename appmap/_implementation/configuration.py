"""
Manage Configuration AppMap recorder for Python
"""

import inspect
import logging
import os
import sys
from functools import partial, wraps

import yaml

from .recording import recorder, Filter
from .event import Event, CallEvent, ReturnEvent, ExceptionEvent

logging.basicConfig(level=getattr(logging,
                                  os.getenv("APPMAP_LOG_LEVEL", "warning").upper()))


def enabled():
    return os.getenv("APPMAP", "false") == "true"


def split_method_name(method):
    qualname = method.__qualname__
    if '.' in qualname:
        class_name, func_name = qualname.rsplit('.', 1)
    else:
        class_name = ''
        func_name = qualname
    return (class_name, func_name)


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


class ConfigFilter(Filter):
    includes = set()
    excludes = set()

    @classmethod
    def load_config(cls):
        if not enabled():
            return cls

        config_file = os.getenv("APPMAP_CONFIG", "appmap.yml")
        with open(config_file) as file:
            config = yaml.load(file, Loader=yaml.BaseLoader)
            logging.debug('config %s', config)

        for package in config['packages']:
            path = package['path']
            cls.includes.add(path)
            if 'exclude' in package:
                excludes = [f'{path}.{e}' for e in package['exclude']]
                cls.excludes.update(excludes)
        logging.debug('ConfigFilter, includes %s', cls.includes)
        logging.debug('ConfigFilter, excludes %s', cls.excludes)

        return cls

    @classmethod
    def excluded(cls, method):
        ret = in_set(method, cls.excludes)
        logging.debug('ConfigFilter, %s excluded? %s', method, ret)
        return ret

    @classmethod
    def included(cls, method):
        ret = in_set(method, cls.includes)
        logging.debug('ConfigFilter, %s included? %s', method, ret)
        return ret

    def call(self, method):
        if self.excluded(method):
            return method
        if self.included(method):
            return wrap(method)
        return self.next_filter.call(method)


class BuiltinFilter(Filter):

    @classmethod
    def load_config(cls):
        if not enabled:
            return cls

        cls.includes = {'os.read', 'os.write'}
        logging.debug('BuiltinFilter, includes %s', cls.includes)
        return cls

    @classmethod
    def included(cls, method):
        ret = in_set(method, cls.includes)
        logging.debug('BuiltinFilter, %s included? %s', method, ret)

    def call(self, method):
        if self.included(method):
            return wrap(method)
        return self.next_filter.call(method)
