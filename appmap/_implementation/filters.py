""" Various filters """

import logging
from .configuration import appmap_enabled, appmap_config
from .utils import wrap, in_set


class Filter:
    def __init__(self, next_filter):
        self.next_filter = next_filter


class NullFilter(Filter):
    def call(self, method):
        return method


class ConfigFilter(Filter):
    includes = set()
    excludes = set()

    @classmethod
    def load_config(cls):
        if not appmap_enabled():
            return cls

        config = appmap_config()

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
        if not appmap_enabled():
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
