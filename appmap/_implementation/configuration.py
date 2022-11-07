"""
Manage Configuration AppMap recorder for Python.
"""

import inspect
import logging
import re
import sys
from functools import lru_cache
from os.path import realpath
from pathlib import Path
from textwrap import dedent

import importlib_metadata
import yaml
from yaml.parser import ParserError

from appmap._implementation.detect_enabled import DetectEnabled

from ..labeling import presets as label_presets
from . import utils
from .env import Env
from .importer import Filter, Importer
from .instrument import instrument

logger = logging.getLogger(__name__)


def warn_config_missing(path):
    """Display a warning about missing config file in path."""
    name = path.resolve().parent.name
    package = re.sub(r"\W", ".", name).lower()


def default_app_name(rootdir):
    rootdir = Path(rootdir)
    if not (rootdir / ".git").exists():
        return rootdir.name

    git = utils.git(cwd=str(rootdir))
    repo_root = git("rev-parse --show-toplevel")
    return Path(repo_root).name


# Make it easy to mock sys.prefix
def _get_sys_prefix():
    return realpath(sys.prefix)


def find_top_packages(rootdir):
    """
    Scan a directory tree for packages that should appear in the
    default config file.

    Examine directories in rootdir, to see if they contains an
    __init__.py.  If it does, add it to the list of packages and don't
    scan any of its subdirectories.  If it doesn't, scan its
    subdirectories to find __init__.py.

    Some directories are automatically excluded from the search:
      * sys.prefix
      * Hidden directories (i.e. those that start with a '.')
      * node_modules

    For example, in a directory like this

        % ls -F
        LICENSE Makefile appveyor.yml docs/ src/ tests/
        MANIFEST.in README.rst blog/ setup.py tddium.yml tox.ini

    docs, src, tests, and blog will get scanned.

    Only src has a subdirectory containing an __init__.py:

        % for f in docs src tests blog; do find $f | head -5; done
        docs
        docs/index.rst
        docs/testing.rst
        docs/_templates
        docs/_templates/.gitkeep
        src
        src/wrapt
        src/wrapt/importer.py
        src/wrapt/__init__.py
        src/wrapt/wrappers.py
        tests
        tests/test_outer_classmethod.py
        tests/test_inner_classmethod.py
        tests/conftest.py
        tests/test_class.py
        blog
        blog/04-implementing-a-universal-decorator.md
        blog/03-implementing-a-factory-for-creating-decorators.md
        blog/05-decorators-which-accept-arguments.md
        blog/09-performance-overhead-of-using-decorators.md

    Thus, the list of top packages returned will be ['wrapt'].
    """

    # Use a set so we don't get duplicates, e.g. if the project's
    # build process copies its source to a subdirectory.
    packages = set()
    import os

    def excluded(dir):
        excluded = dir == "node_modules" or dir[0] == "."
        if excluded:
            logger.debug("excluding dir %s", dir)
        return excluded

    sys_prefix = _get_sys_prefix()

    for dir, dirs, files in os.walk(rootdir):
        logger.debug("dir %s dirs %s", dir, dirs)
        if realpath(dir) == sys_prefix:
            logger.debug("skipping sys.prefix %s", sys_prefix)
            dirs.clear()
            continue

        if "__init__.py" in files:
            packages.add(Path(dir).name)
            dirs.clear()
        else:
            dirs[:] = [d for d in dirs if not excluded(d)]

    return packages


class Config:
    """Singleton Config class"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.debug("Creating the Config object")
            cls._instance = super(Config, cls).__new__(cls)

            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.file_present = False
        self.file_valid = False

        self._load_config()
        self._initialized = True

    @classmethod
    def initialize(cls):
        cls._instance = None

    @property
    def name(self):
        return self._config["name"]

    @property
    def packages(self):
        return self._config["packages"]

    @property
    @lru_cache(maxsize=None)
    def labels(self):
        """The LabelSet defined in the configuration, plus any presets."""
        labels = label_presets()
        if "labels" in self._config:
            labels.append(self._config["labels"])
        return labels

    @property
    def default(self):
        return {"name": self.default_name, "packages": self.default_packages}

    @property
    def default_name(self):
        root_dir = Env.current.root_dir
        return default_app_name(root_dir)

    @property
    def default_packages(self):
        root_dir = Env.current.root_dir
        return [{"path": p} for p in find_top_packages(root_dir)]

    def _load_config(self):
        self._config = {"name": None, "packages": []}

        # Only use a default config if the user hasn't specified a
        # config.
        env_config_filename = Env.current.get("APPMAP_CONFIG")

        use_default_config = not env_config_filename
        if use_default_config:
            env_config_filename = "appmap.yml"

        path = Path(env_config_filename).resolve()
        if path.is_file():
            self.file_present = True

            should_enable = Env.current.enabled
            Env.current.enabled = False
            self.file_valid = False
            try:
                self._config = yaml.safe_load(path.read_text())
                if not self._config:
                    # It parsed, but was (effectively) empty.
                    self._config = self.default
                else:
                    # It parsed, make sure it has name and packages set.
                    if not self._config.get("name", None):
                        self._config["name"] = self.default_name
                    if not self._config.get("packages", None):
                        self._config["packages"] = self.default_packages
                self.file_valid = True
                Env.current.enabled = should_enable
            except ParserError:
                pass
            logger.debug("config: %s", self._config)
            return

        if not Env.current.enabled:
            return

        logger.warning(dedent(f'Config file "{path}" is missing.'))
        if use_default_config:
            logger.warning(
                dedent(
                    f"""
It will be created with this configuration: 

{yaml.dump(self.default)}
            """
                )
            )
            self._config = self.default
            self.write_config_file(path, self.default)
        else:
            # disable appmap and return a dummy config
            # so the errors don't accumulate
            Env.current.enabled = False

    def write_config_file(self, filepath, config):
        # HACK: don't scribble on the repo when testing
        if DetectEnabled.is_appmap_repo():
            return
        basedir = filepath.parent
        if not basedir.exists():
            basedir.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(yaml.dump(config, sort_keys=True))


def startswith(prefix, sequence):
    """
    Check if a sequence starts with the prefix.
    """
    return len(prefix) <= len(sequence) and all(
        a == b for a, b in zip(sequence, prefix)
    )


class PathMatcher:
    def __init__(self, prefix, excludes=None, shallow=False):
        excludes = excludes or []
        self.prefix = []
        if prefix:
            self.prefix = prefix.split(".")
        self.excludes = [x.split(".") for x in excludes]
        self.shallow = shallow

    def matches(self, filterable):
        fqname = name = filterable.fqname.split(".")
        if startswith(self.prefix, name):
            name = name[len(self.prefix) :]
            result = not any(startswith(x, name) for x in self.excludes)
        else:
            result = False
        logger.debug("%r.matches(%r) -> %r", self, fqname, result)
        return result

    def __repr__(self):
        return "PathMatcher(%r, %r, shallow=%r)" % (
            ".".join(self.prefix),
            [".".join(ex) for ex in self.excludes],
            self.shallow,
        )


class DistMatcher(PathMatcher):
    def __init__(self, dist, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dist = dist
        self.files = [str(pp.locate()) for pp in importlib_metadata.files(dist)]

    def matches(self, filterable):
        try:
            obj = filterable.obj
            logger.debug(
                "%r.matches(%r): %s in %r", self, obj, inspect.getfile(obj), self.files
            )
            if inspect.getfile(obj) not in self.files:
                return False
        except TypeError:
            # builtins don't have file associated
            return False
        return super().matches(filterable)

    def __repr__(self):
        return "DistMatcher(%r, %r, %r, shallow=%r)" % (
            self.dist,
            ".".join(self.prefix),
            [".".join(ex) for ex in self.excludes],
            self.shallow,
        )


class MatcherFilter(Filter):
    def __init__(self, matchers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matchers = matchers

    def filter(self, filterable):
        result = any(
            m.matches(filterable) for m in self.matchers
        ) or self.next_filter.filter(filterable)
        logger.debug("ConfigFilter.filter(%r) -> %r", filterable.fqname, result)
        return result

    def wrap(self, filterable):
        rule = self.match(filterable)
        if rule:
            wrapped = getattr(filterable.obj, "_appmap_wrapped", None)
            if wrapped is None:
                logger.debug("  wrapping %s", filterable.fqname)
                Config().labels.apply(filterable)
                ret = instrument(filterable)
                if rule.shallow:
                    setattr(ret, "_appmap_shallow", rule)
            else:
                logger.debug("  already wrapped %s", filterable.fqname)
                ret = filterable.obj
            return ret

        return self.next_filter.wrap(filterable)

    def match(self, filterable):
        return next((m for m in self.matchers if m.matches(filterable)), None)


def matcher_of_config(package):
    dist = package.get("dist", None)
    if dist:
        return DistMatcher(
            dist,
            package.get("path", None),
            package.get("exclude", []),
            shallow=package.get("shallow", True),
        )
    return PathMatcher(
        package["path"],
        package.get("exclude", []),
        shallow=package.get("shallow", False),
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
            matchers = [PathMatcher(f) for f in {"os.read", "os.write"}]
        super().__init__(matchers, *args, **kwargs)


def initialize():
    DetectEnabled.initialize()
    Config().initialize()
    Importer.use_filter(BuiltinFilter)
    Importer.use_filter(ConfigFilter)


initialize()
