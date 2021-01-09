"""
Manage Configuration AppMap recorder for Python.
"""

import logging
import os
import sys
from contextlib import contextmanager
from functools import wraps

import yaml

from . import env
from . import event
from .recording import Recorder, Filter
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


def wrap(fn, isstatic):
    """return a wrapped function"""
    logger.info('hooking %s', '.'.join(split_function_name(fn)))

    make_call_event = event.CallEvent.make(fn, isstatic)
    make_receiver = event.CallEvent.make_receiver(fn, isstatic)

    @wraps(fn)
    def run(*args, **kwargs):
        if not Recorder().enabled or is_instrumentation_disabled():
            return fn(*args, **kwargs)

        with recording_disabled():
            call_event = make_call_event(receiver=make_receiver(args, kwargs),
                                         parameters=[])
        call_event_id = call_event.id
        Recorder().add_event(call_event)
        try:
            logger.debug('%s args %s kwargs %s', fn, args, kwargs)
            ret = fn(*args, **kwargs)

            return_event = event.ReturnEvent(parent_id=call_event_id)
            Recorder().add_event(return_event)
            return ret
        except Exception:  # noqa: E722
            Recorder().add_event(event.ExceptionEvent(parent_id=call_event_id,
                                                      exc_info=sys.exc_info()))
            raise
    setattr(run, '_appmap_wrapped', True)
    return run


def in_set(name, which):
    return any(filter(name.startswith, which))


def function_in_set(fn, which):
    class_name, fn_name = split_function_name(fn)
    if class_name is None:
        # fn isn't in a class, ignore it.
        return False

    class_name += '.'
    logger.debug(('class_name %s'
                  ' fnname %s'
                  ' which %s'),
                 class_name,
                 fn_name,
                 which)
    return (in_set(class_name, which)
            or in_set(f'{class_name}{fn_name}', which))


class ConfigFilter(Filter):
    """
    During initialization, the ConfigFilter class reads the `package`
    entries from the config file.  Based on these entries, it creates
    a set of paths that should be included, and another set of paths
    that should be excluded.

    When checking to see if a function should be included,
    ConfigFilter looks for the function in both sets.  If the function
    is found in the included set, it's wrapped for instrumentation.
    If it's found in the excluded set, it's used without modification.
    If it isn't found in either set, ConfigFilter passes the function
    on to the next Filter.

    To determine whether a function is in one of the sets, the
    fully-qualified name of the function is considered, including the
    packages(s), module, and class that contain it.  As an example,
    consider a function named `pkg1.pkg2.mod1.Class1.func`.  Any of
    `pkg1`, `pkg1.pkg2.`, `pkg1.pkg2.mod1`, `pkg1.pkg2.mod1.Class1`,
    or `pkg1.pkg2.mod1.Class1.func` will match this function (causing
    it to be included or excluded, as appropriate).  Note that only
    full names will match.  (This is achieved in the code by appending
    `.` to the name retrieved from the config file.)
    """
    def __init__(self, *args):
        super().__init__(*args)
        if not env.enabled():
            return

        # Store entries from the config file. Each entry has '.'
        # appended to it, to ensure that only full names are matched.
        self.includes = set()
        self.excludes = set()

        config_file = os.getenv("APPMAP_CONFIG", "appmap.yml")
        with open(config_file) as file:
            config = yaml.load(file, Loader=yaml.BaseLoader)
            logger.debug('config %s', config)

        for package in config['packages']:
            path = package['path']
            self.includes.add(path + '.')
            if 'exclude' in package:
                if not isinstance(package['exclude'], list):
                    raise RuntimeError('Excludes for package'
                                       f' "{path}" must be a list')
                excludes = [f'{path}.{e}.' for e in package['exclude']]
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

    def wrap(self, fn, isstatic):
        if self.excluded(fn):
            return fn
        if self.included(fn):
            if getattr(fn, '_appmap_wrapped', None) is None:
                return wrap(fn, isstatic)
        return self.next_filter.wrap(fn, isstatic)


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

    def wrap(self, fn, isstatic):
        if self.included(fn):
            return wrap(fn, isstatic)
        return self.next_filter.wrap(fn, isstatic)


def initialize():
    Recorder().use_filter(BuiltinFilter)
    Recorder().use_filter(ConfigFilter)


initialize()
