"""
Manage Configuration AppMap recorder for Python
"""

import logging
import os
import sys
from functools import wraps

import yaml

from . import env
from . import event
from . import utils
from .recording import recorder, Filter

logger = logging.getLogger(__name__)


def wrap(fn_attr, fn):
    """return a wrapped function"""
    logger.info('hooking %s', fn)

    make_call_event = event.CallEvent.make(fn_attr, fn)
    make_receiver = event.CallEvent.make_receiver(fn_attr, fn)

    @wraps(fn)
    def run(*args, **kwargs):
        if not recorder.enabled:
            return fn(*args, **kwargs)
        call_event = make_call_event(receiver=make_receiver(args, kwargs),
                                     parameters=[])
        call_event_id = call_event.id
        recorder.add_event(call_event)
        try:
            logger.info('%s args %s kwargs %s', fn, args, kwargs)
            ret = fn(*args, **kwargs)

            return_event = event.ReturnEvent(parent_id=call_event_id)
            recorder.add_event(return_event)
            return ret
        except Exception:  # noqa: E722
            recorder.add_event(event.ExceptionEvent(parent_id=call_event_id,
                                                    exc_info=sys.exc_info()))
            raise
    return run


def in_set(name, which):
    return any(filter(name.startswith, which))


def function_in_set(fn, which):
    class_name, fn_name = utils.split_function_name(fn)
    logger.debug(('  class_name %s'
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
            logger.debug('config %s', config)

        for package in config['packages']:
            path = package['path']
            self.includes.add(path)
            if 'exclude' in package:
                excludes = [f'{path}.{e}' for e in package['exclude']]
                self.excludes.update(excludes)
        logger.debug('ConfigFilter, includes %s', self.includes)
        logger.debug('ConfigFilter, excludes %s', self.excludes)

    def excluded(self, fn):
        ret = function_in_set(fn, self.excludes)
        logger.debug('ConfigFilter, %s excluded? %s', fn, ret)
        return ret

    def included(self, fn):
        ret = function_in_set(fn, self.includes)
        logger.debug('ConfigFilter, %s included? %s', fn, ret)
        return ret

    def filter(self, class_):
        name = f'{class_.__module__}.{class_.__name__}'
        logger.debug('ConfigFilter.filter, name %s', name)
        if in_set(name, self.excludes):
            logger.debug('  excluded')
            return False
        if in_set(name, self.includes):
            logger.debug('  included')
            return True

        logger.debug('  undecided')
        return self.next_filter.filter(class_)

    def wrap(self, fn_attr, fn):
        if self.excluded(fn):
            return fn
        if self.included(fn):
            return wrap(fn_attr, fn)
        return self.next_filter.wrap(fn_attr, fn)


class BuiltinFilter(Filter):
    def __init__(self, *args):
        super().__init__(*args)
        if not env.enabled():
            return

        self.includes = {'os.read', 'os.write'}

    def included(self, fn):
        return function_in_set(fn, self.includes)

    def filter(self, class_):
        name = class_.__name__
        if in_set(name, self.includes):
            return True
        return self.next_filter.filter(class_)

    def wrap(self, fn_attr, fn):
        if self.included(fn):
            return wrap(fn_attr, fn)
        return self.next_filter.wrap(fn_attr, fn)


recorder.use_filter(BuiltinFilter)
recorder.use_filter(ConfigFilter)
