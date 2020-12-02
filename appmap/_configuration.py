"""Manage Configuration AppMap recorder for Python"""
import os
import yaml


class Configuration:
    """Load appmap-python configuration from appmap.yml"""

    @staticmethod
    def enabled():
        """Return true if recording is enabled"""
        return os.getenv("APPMAP", "false") == "true"

    def __init__(self):
        if not Configuration.enabled:
            return

        with open("appmap.yml") as file:
            config = yaml.load(file, Loader=yaml.BaseLoader)
            print(f'config {config}')

        self._includes = set()
        self._excludes = set()
        for package in config['packages']:
            path = package['path']
            self._includes.add(path)
            if package.get('exclude'):
                excludes = [f'{path}.{e}' for e in package['exclude']]
                self._excludes.update(excludes)

        print(f'self._includes {self._includes} self._excludes {self._excludes}')

    def includes(self, elt):
        """
        Return True if the given element (package, class, or function)
        is included by the configuration, False otherwise
        """
        return elt in self._includes and elt not in self._excludes
