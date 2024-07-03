import inspect
import os
import re
import shlex
import subprocess
import types
from contextlib import contextmanager
from contextvars import ContextVar
from enum import Enum, IntFlag, auto
from pathlib import Path
from typing import Any, Callable

from .env import Env


class Scope(Enum):
    MODULE = 0
    CLASS = 1


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
    # auxtypes
    GET = auto()
    SET = auto()
    DEL = auto()

    @staticmethod
    def classify(fn):
        fn_type = type(fn)
        if fn_type in (staticmethod, types.BuiltinMethodType):
            return FnType.STATIC
        if fn_type in (classmethod, types.BuiltinMethodType):
            return FnType.CLASS

        return FnType.INSTANCE


_appmap_tls = ContextVar("tls")


def appmap_tls():
    try:
        return _appmap_tls.get()
    except LookupError:
        _appmap_tls.set({})
        return _appmap_tls.get()


@contextmanager
def appmap_tls_context():
    token = _appmap_tls.set({})
    try:
        yield
    finally:
        _appmap_tls.reset(token)


def fqname(cls):
    return "%s.%s" % (cls.__module__, cls.__qualname__)

class FqFnName:
    """
    FqFnName makes it easy to reference the parts of the fully-qualified name of a callable.
    """

    def __init__(self, fn: Callable[..., Any]):

        self._modname = fn.__module__
        qualname = fn.__qualname__
        if "." in qualname:
            self._scope = Scope.CLASS
            self._class_name, self._fn_name = qualname.rsplit(".", 1)
        else:
            self._scope = Scope.MODULE
            self._class_name = None
            self._fn_name = qualname

    @property
    def scope(self) -> Scope:
        """The scope of the Callable, i.e. whether it's contained in a module or a class."""
        return self._scope

    @property
    def fqmod(self):
        return self._modname

    @property
    def fqclass(self):
        return self._modname if self._class_name is None else f"{self._modname}.{self._class_name}"

    @property
    def fqfn(self):
        return (self.fqclass, self._fn_name)

    @property
    def fn_name(self):
        return self._fn_name

FqFnName(fqname)

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


def locate_file_up(filename, start_dir=None, stop_dir=None):
    """
    Search for a file in the current directory and recursively up to the root directory.

    :param filename: The name of the file to locate.
    :param start_dir: The directory to start the search from. Defaults to the current.
    :param stop_dir: The directory to stop the search. If None search is performed until
                     the root of the file system.
    :return: The path to the directory containing the file or None if the file cannot be found.
    """

    if start_dir is None:
        start_dir = Path.cwd()
    elif isinstance(start_dir, str):
        start_dir = Path(start_dir)

    file_path = start_dir.joinpath(filename)
    if Path.exists(file_path):
        return start_dir

    for p in start_dir.parents:
        if Path.exists(p.joinpath(filename)):
            return p
        if p == stop_dir:
            return None

    return None
