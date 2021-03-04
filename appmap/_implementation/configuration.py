"""
Manage Configuration AppMap recorder for Python.
"""

import logging
import os.path

import yaml

from .env import Env
from .instrument import instrument

from .recording import Recorder, Filter

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
            cls._instance._initialized = not Env.current.enabled

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

    @property
    def name(self):
        return self._config['name']

    @property
    def packages(self):
        return self._config['packages']


def splitname(obj):
    """
    Given an object that has a __module__ and __qualname__,
    return a list of name components from both.
    """
    return obj.__module__.split('.') + obj.__qualname__.split('.')


def startswith(prefix, sequence):
    """
    Check if a sequence starts with the prefix.
    """
    return len(prefix) <= len(sequence) and all(a == b for a, b in zip(sequence, prefix))


class PathMatcher:
    def __init__(self, prefix, excludes=None):
        excludes = excludes or []
        self.prefix = prefix.split('.')
        self.excludes = [x.split('.') for x in excludes]

    def matches(self, obj):
        name = splitname(obj)
        if startswith(self.prefix, name):
            name = name[len(self.prefix):]
            result = not any(startswith(x, name) for x in self.excludes)
        else:
            result = False
        logger.debug('PathMatcher.matches(%r, %r) -> %r', self, obj, result)
        return result

    def __repr__(self):
        return 'PathMatcher(%r, %r)' % ('.'.join(self.prefix), ['.'.join(ex) for ex in self.excludes])


class MatcherFilter(Filter):
    def __init__(self, matchers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matchers = matchers

    def filter(self, class_):
        result = any(m.matches(class_) for m in self.matchers) or self.next_filter.filter(class_)
        logger.debug('ConfigFilter.filter(%r) -> %r', class_, result)
        return result

    def wrap(self, fn, fntype):
        if self.included(fn):
            wrapped = getattr(fn, '_appmap_wrapped', None)
            logger.debug('  wrapped %s', wrapped)
            if wrapped is None:
                logger.debug('  wrapping %s', fn)
                ret = instrument(fn, fntype)
            else:
                logger.debug('  already wrapped %s', fn)
                ret = fn
            return ret

        return self.next_filter.wrap(fn, fntype)

    def included(self, fn):
        return any(m.matches(fn) for m in self.matchers)


class ConfigFilter(MatcherFilter):
    def __init__(self, *args, **kwargs):
        matchers = []
        if Env.current.enabled:
            matchers = [PathMatcher(p['path'], p.get('exclude', [])) for p in Config().packages]
        super().__init__(matchers, *args, **kwargs)


class BuiltinFilter(MatcherFilter):
    def __init__(self, *args, **kwargs):
        matchers = []
        if Env.current.enabled:
            matchers = [PathMatcher(f) for f in {'os.read', 'os.write'}]
        super().__init__(matchers, *args, **kwargs)


def initialize():
    Config().initialize()
    Recorder().use_filter(BuiltinFilter)
    Recorder().use_filter(ConfigFilter)


initialize()
