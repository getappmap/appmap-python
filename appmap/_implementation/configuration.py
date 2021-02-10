"""
Manage Configuration AppMap recorder for Python.
"""

import logging
import os
import sys
from contextlib import contextmanager
from functools import wraps, cached_property
import time

import yaml

from . import env
from . import event
from .recording import Recorder, Filter
from .utils import appmap_tls, split_function_name, fqname

logger = logging.getLogger(__name__)


class Config:
    """ Singleton Config class """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.debug('Creating the Config object')
            cls._instance = super(Config, cls).__new__(cls)

            # If we're not enabled, no more initialization needs to be
            # done.
            cls._instance._initialized = not env.enabled()

        return cls._instance

    def __init__(self):
        if self.__getattribute__('_initialized'):  # keep pylint happy
            return

        config_file = os.getenv("APPMAP_CONFIG", "appmap.yml")
        with open(config_file) as file:
            self._config = yaml.load(file, Loader=yaml.BaseLoader)
            logger.debug('self._config %s', self._config)

        self._initialized = True

    @classmethod
    def initialize(cls):
        cls._instance = None

    @cached_property
    def output_dir(self):
        return os.getenv("APPMAP_OUTPUT_DIR",
                         os.path.join('tmp', 'appmap'))

    @cached_property
    def name(self):
        return self._config['name']

    @cached_property
    def packages(self):
        return self._config['packages']


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
    logger.debug('hooking %s', '.'.join(split_function_name(fn)))

    make_call_event = event.CallEvent.make(fn, isstatic)
    make_receiver = event.CallEvent.make_receiver(fn, isstatic)

    @wraps(fn)
    def wrapped_fn(*args, **kwargs):
        if not Recorder().enabled or is_instrumentation_disabled():
            return fn(*args, **kwargs)

        with recording_disabled():
            logger.debug('%s args %s kwargs %s', fn, args, kwargs)
            call_event = make_call_event(receiver=make_receiver(args, kwargs),
                                         parameters=[])
        call_event_id = call_event.id
        Recorder().add_event(call_event)
        start_time = time.time()
        try:
            ret = fn(*args, **kwargs)
            elapsed_time = time.time() - start_time

            return_event = event.ReturnEvent(parent_id=call_event_id, elapsed=elapsed_time)
            Recorder().add_event(return_event)
            return ret
        except Exception:  # noqa: E722
            elapsed_time = time.time() - start_time
            Recorder().add_event(event.ExceptionEvent(parent_id=call_event_id,
                                                      elapsed=elapsed_time,
                                                      exc_info=sys.exc_info()))
            raise
    setattr(wrapped_fn, '_appmap_wrapped', True)
    return wrapped_fn


def name_in_set(name, which):
    return any(filter(lambda n: name.startswith(n + '.') or name == n,
                      which))


def class_in_set(class_name, which):
    return name_in_set(class_name + '.', which)


def function_in_set(fn, which):
    class_name, fn_name = split_function_name(fn)
    if class_name is None:
        # fn isn't in a class, ignore it.
        return False

    ret = (class_in_set(class_name, which)
           or name_in_set(f'{class_name}.{fn_name}', which))

    logger.debug(('function_in_set, class_name %s'
                  ' fnname %s'
                  ' which %s'
                  ' ret %s'),
                 class_name,
                 fn_name,
                 which,
                 ret)
    return ret


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._includes = set()
        self._excludes = set()

        if not env.enabled():
            return

        for package in Config().packages:
            path = package['path']
            self._includes.add(path)
            if 'exclude' in package:
                if not isinstance(package['exclude'], list):
                    raise RuntimeError('Excludes for package'
                                       f' "{path}" must be a list')
                excludes = [f'{path}.{e}' for e in package['exclude']]
                self._excludes.update(excludes)
        logger.info('ConfigFilter, includes %s', self._includes)
        logger.info('ConfigFilter, excludes %s', self._excludes)

    def excluded(self, fn):
        ret = function_in_set(fn, self._excludes)
        logger.debug('ConfigFilter, %s excluded? %s', fn, ret)
        return ret

    def included(self, fn):
        ret = function_in_set(fn, self._includes)
        logger.debug('ConfigFilter, %s included? %s', fn, ret)
        return ret

    def filter(self, class_):
        name = fqname(class_)
        if class_in_set(name, self._excludes):
            logger.info('excluded class %s', name)
            return False
        if class_in_set(name, self._includes):
            logger.info('included class %s', name)
            return True

        logger.debug('  undecided')
        return self.next_filter.filter(class_)

    def wrap(self, fn, isstatic):
        logger.debug('ConfigFilter.wrap, fn %s', fn)

        fn_name = '.'.join(split_function_name(fn))
        if self.excluded(fn):
            logger.info('excluded function %s', fn_name)
            return fn

        if self.included(fn):
            logger.info('included function %s', fn_name)
            wrapped = getattr(fn, '_appmap_wrapped', None)
            logger.debug('  wrapped %s', wrapped)
            if wrapped is None:
                logger.debug('  wrapping %s', fn)
                ret = wrap(fn, isstatic)
            else:
                logger.debug('  already wrapped %s', fn)
                ret = fn
            return ret

        return self.next_filter.wrap(fn, isstatic)


class BuiltinFilter(Filter):
    def __init__(self, *args):
        super().__init__(*args)
        if not env.enabled():
            self._includes = set()
            return

        self._includes = {'os.read', 'os.write'}

    def included(self, fn):
        return function_in_set(fn, self._includes)

    def filter(self, class_):
        name = class_.__name__
        if class_in_set(name, self._includes):
            return True
        return self.next_filter.filter(class_)

    def wrap(self, fn, isstatic):
        if self.included(fn):
            return wrap(fn, isstatic)
        return self.next_filter.wrap(fn, isstatic)


def initialize():
    Config().initialize()
    Recorder().use_filter(BuiltinFilter)
    Recorder().use_filter(ConfigFilter)


initialize()
