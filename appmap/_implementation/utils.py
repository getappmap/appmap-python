import inspect
import os
import re
import shlex
import subprocess
import threading
import types
from collections.abc import MutableMapping
from enum import IntFlag, auto

from .env import Env


def compact_dict(dictionary):
    """Return a copy of dictionary with None values filtered out."""
    return {k: v for k, v in dictionary.items() if v is not None}


def values_dict(items):
    """Given a list of (key, list) values returns a dictionary where
    single-element lists have been replaced by their sole value.
    """
    return {k: v[0] if len(v) == 1 else v for k, v in items}


class FnType(IntFlag):
    STATIC = auto()
    CLASS = auto()
    INSTANCE = auto()
    MODULE = auto()

    @staticmethod
    def classify(fn):
        fn_type = type(fn)
        if fn_type == staticmethod or fn_type == types.BuiltinMethodType:
            return FnType.STATIC
        elif fn_type == classmethod or fn_type == types.BuiltinMethodType:
            return FnType.CLASS
        else:
            return FnType.INSTANCE


class ThreadLocalDict(threading.local, MutableMapping):
    def __init__(self):
        super().__init__()
        self.values = {}

    def __getitem__(self, k):
        return self.values[k]

    def __setitem__(self, k, v):
        self.values[k] = v

    def __delitem__(self, k):
        del self.values[k]

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)


_appmap_tls = ThreadLocalDict()


def appmap_tls():
    return _appmap_tls


def fqname(cls):
    return "%s.%s" % (cls.__module__, cls.__qualname__)


def split_function_name(fn):
    """
    Given a method, return a tuple containing its fully-qualified
    class name and the method name.
    """
    qualname = fn.__qualname__
    if "." in qualname:
        class_name, fn_name = qualname.rsplit(".", 1)
        class_name = "%s.%s" % (fn.__module__, class_name)
    else:
        class_name = fn.__module__
        fn_name = qualname
    return (class_name, fn_name)


def root_relative_path(path):
    """Returns the path relative to the current root_dir.

    The path should be absolute.
    If it's not under the current root_dir, it's returned unchanged.
    """
    if path.startswith(Env.current.root_dir):
        path = path[Env.current.root_dir_len :]
    return path


def get_function_location(fn):
    fn = inspect.unwrap(fn)
    try:
        path = root_relative_path(inspect.getsourcefile(fn))
    except TypeError:
        path = "<builtin>"

    try:
        __, lineno = inspect.getsourcelines(fn)
    except (OSError, TypeError):
        lineno = 0
    return (path, lineno)


class ProcRet:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self._returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    @property
    def returncode(self):
        return self._returncode

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr


def subprocess_run(command_args, cwd=None):
    if not cwd:
        cwd = os.getcwd()
    try:
        out = subprocess.check_output(
            command_args,
            stderr=subprocess.STDOUT,
            cwd=str(cwd),
            universal_newlines=True,
        )
        return ProcRet(stdout=out, returncode=0)
    except subprocess.CalledProcessError as exc:
        return ProcRet(stderr=exc.stdout, returncode=exc.returncode)


class git:
    def __init__(self, cwd=None):
        self._cwd = cwd if cwd else os.getcwd()

    def __call__(self, cmd):
        return subprocess_run(shlex.split("git " + cmd), cwd=self._cwd).stdout.strip()

    @property
    def cwd(self):
        return self._cwd


def patch_class(cls):
    """Class decorator for monkey patching.

    Decorating a class (patch) with @patch_class(orig) will change orig, so
    that every method defined in patch will call that implementation instead
    of the one in orig.

    The methods take the original (unbound) implementation as the
    second argument after self; the rest is passed as is.

    It's the responsibility of the wrapper method to call the original
    if appropriate, with arguments it wants (self probably being
    the first one).

    Methods without an implementation in the original are copied verbatim.
    """

    def _wrap_fun(wrapper, original):
        def wrapped(self, *args, **kwargs):
            return wrapper(self, original, *args, **kwargs)

        return wrapped

    def _wrap_cls(patch):
        for func in dir(patch):
            if not func.startswith("__"):
                wrapper = getattr(patch, func)
                original = getattr(cls, func, None)
                if original:
                    setattr(cls, func, _wrap_fun(wrapper, original))
                else:
                    setattr(cls, func, wrapper)
        return patch

    return _wrap_cls


# this is different than appmap-ruby: part of its logic is in write_appmap
def scenario_filename(name, separator="_"):
    pattern = r"[^a-z0-9\-_]+"
    replacement = separator
    return re.sub(pattern, replacement, name, flags=re.IGNORECASE)
