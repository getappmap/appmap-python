"""
Manage Configuration AppMap recorder for Python.
"""

import importlib_metadata
from functools import lru_cache
import inspect
import logging

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

    @property
    @lru_cache(maxsize=None)
    def _config(self):
        config_file = Env.current.get("APPMAP_CONFIG", "appmap.yml")
        with open(config_file) as file:
            ret = yaml.safe_load(file)
            logger.info('config: %s', ret)
            return ret

def startswith(prefix, sequence):
    """
    Check if a sequence starts with the prefix.
    """
    return len(prefix) <= len(sequence) and all(a == b for a, b in zip(sequence, prefix))


class PathMatcher:
    def __init__(self, prefix, excludes=None, shallow=False):
        excludes = excludes or []
        self.prefix = []
        if prefix:
            self.prefix = prefix.split('.')
        self.excludes = [x.split('.') for x in excludes]
        self.shallow = shallow

    def matches(self, filterable):
        fqname = name = filterable.fqname.split('.')
        if startswith(self.prefix, name):
            name = name[len(self.prefix):]
            result = not any(startswith(x, name) for x in self.excludes)
        else:
            result = False
        logger.debug('%r.matches(%r) -> %r', self, fqname, result)
        return result

    def __repr__(self):
        return 'PathMatcher(%r, %r, shallow=%r)' % (
            '.'.join(self.prefix),
            ['.'.join(ex) for ex in self.excludes],
            self.shallow
        )


class DistMatcher(PathMatcher):
    def __init__(self, dist, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dist = dist
        self.files = [str(pp.locate()) for pp in importlib_metadata.files(dist)]

    def matches(self, filterable):
        try:
            obj = filterable.obj
            logger.debug('%r.matches(%r): %s in %r', self, obj, inspect.getfile(obj), self.files)
            if inspect.getfile(obj) not in self.files:
                return False
        except TypeError:
            # builtins don't have file associated
            return False
        return super().matches(filterable)

    def __repr__(self):
        return 'DistMatcher(%r, %r, %r, shallow=%r)' % (
            self.dist,
            '.'.join(self.prefix),
            ['.'.join(ex) for ex in self.excludes],
            self.shallow
        )


class MatcherFilter(Filter):
    def __init__(self, matchers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matchers = matchers

    def filter(self, filterable):
        result = any(m.matches(filterable) for m in self.matchers) or self.next_filter.filter(filterable)
        logger.debug('ConfigFilter.filter(%r) -> %r', filterable.fqname, result)
        return result

    def wrap(self, filterable):
        rule = self.match(filterable)
        if rule:
            wrapped = getattr(filterable.obj, '_appmap_wrapped', None)
            if wrapped is None:
                logger.debug('  wrapping %s', filterable.fqname)
                ret = instrument(filterable)
                if rule.shallow:
                    setattr(ret, '_appmap_shallow', rule)
            else:
                logger.debug('  already wrapped %s', filterable.fqname)
                ret = filterable.obj
            return ret

        return self.next_filter.wrap(filterable)

    def match(self, filterable):
        return next((m for m in self.matchers if m.matches(filterable)), None)


def matcher_of_config(package):
    dist = package.get('dist', None)
    if dist:
        return DistMatcher(
            dist,
            package.get('path', None),
            package.get('exclude', []),
            shallow=package.get('shallow', True)
        )
    return PathMatcher(
        package['path'],
        package.get('exclude', []),
        shallow=package.get('shallow', False)
    )


class ConfigFilter(MatcherFilter):
    def __init__(self, *args, **kwargs):
        matchers = []
        if Env.current.enabled:
            matchers = [matcher_of_config(p) for p in Config().packages]
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
