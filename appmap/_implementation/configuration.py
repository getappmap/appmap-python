"""
Manage Configuration AppMap recorder for Python
"""

import logging
import os
import sys
from functools import partial, wraps

import yaml

from . import env
from . import event
from . import utils
from .recording import recorder, Filter


def wrap(fn_attr, fn):
    """return a wrapped function"""
    logging.info('hooking %s', fn)

    make_call_event = event.CallEvent.make(fn_attr, fn)

    @wraps(fn)
    def run(*args, **kwargs):
        if not recorder.enabled:
            return fn(*args, **kwargs)
        call_event = make_call_event(receiver=None, parameters=None)
        if not isinstance(call_event, event.Event):
            raise TypeError
        call_event_id = call_event.id
        recorder.add_event(call_event)
        try:
            logging.info('%s args %s kwargs %s', fn, args, kwargs)
            ret = fn(*args, **kwargs)
            return_event = event.ReturnEvent(parent_id=call_event_id)
            if not isinstance(return_event, event.Event):
                raise TypeError
            recorder.add_event(return_event)
            return ret
        except:  # noqa: E722
            recorder.add_event(event.ExceptionEvent(parent_id=call_event_id,
                                                    exc_info=sys.exc_info()))
            raise
    return run


def in_set(name, which):
    return any(filter(lambda s: name.startswith(s), which))


def method_in_set(method, which):
    class_name, fn_name = utils.split_method_name(method)
    logging.debug(('  class_name %s'
                   ' fnname %s'
                   ' which %s'),
                  class_name,
                  fn_name,
                  which)
    if fn_name.startswith('__'):
        return False
    return (in_set(class_name, which)
            or in_set(f'{class_name}.{fn_name}', which))


class ConfigFilter(Filter):
    def __init__(self, *args):
        super().__init__(*args)
        if not env.enabled():
            return

        self.includes = set()
        self.excludes = set()

        config_file = os.getenv("APPMAP_CONFIG", "appmap.yml")
        with open(config_file) as file:
            config = yaml.load(file, Loader=yaml.BaseLoader)
            logging.debug('config %s', config)

        for package in config['packages']:
            path = package['path']
            self.includes.add(path)
            if 'exclude' in package:
                excludes = [f'{path}.{e}' for e in package['exclude']]
                self.excludes.update(excludes)
        logging.debug('ConfigFilter, includes %s', self.includes)
        logging.debug('ConfigFilter, excludes %s', self.excludes)

    def excluded(self, method):
        ret = method_in_set(method, self.excludes)
        logging.debug('ConfigFilter, %s excluded? %s', method, ret)
        return ret

    def included(self, method):
        ret = method_in_set(method, self.includes)
        logging.debug('ConfigFilter, %s included? %s', method, ret)
        return ret

    def filter(self, class_):
        name = f'{class_.__module__}.{class_.__name__}'
        logging.debug('ConfigFilter.filter, name %s', name)
        if in_set(name, self.excludes):
            logging.debug('  excluded')
            return False
        if in_set(name, self.includes):
            logging.debug('  included')
            return True

        logging.debug('  undecided')
        return self.next.filter(class_)

    def wrap(self, method_attr, method):
        if self.excluded(method):
            return method
        if self.included(method):
            return wrap(method_attr, method)
        return self.next.wrap(method_attr, method)


class BuiltinFilter(Filter):
    def __init__(self, *args):
        super().__init__(*args)
        if not env.enabled():
            return

        self.includes = {'os.read', 'os.write'}

    def included(self, method):
        return method_in_set(method, self.includes)

    def filter(self, class_):
        name = class_.__name__
        if in_set(name, self.includes):
            return True
        return self.next.filter(class_)

    def wrap(self, method_attr, method):
        if self.included(method):
            return wrap(method)
        return self.next.wrap(method_attr, method)


recorder.use_filter(BuiltinFilter)
recorder.use_filter(ConfigFilter)
