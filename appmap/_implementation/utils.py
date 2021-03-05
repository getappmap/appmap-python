import threading
import types
from collections.abc import MutableMapping
import shlex
import subprocess
import os

from ._intflag import _IntFlag


# FnType can inherit from IntFlag instead once we drop support for 3.5
class FnType(_IntFlag):
    STATIC = 1
    CLASS = 2
    INSTANCE = 4

    # Don't use these. They're only here so we don't have to implement
    # something like enum.IntFlag._create_pseudo_member_.
    _zero = 0
    _three = STATIC | CLASS
    _six = CLASS | INSTANCE

    @staticmethod
    def classify(fn):
        if isinstance(fn, (staticmethod, types.BuiltinMethodType)):
            return FnType.STATIC
        elif isinstance(fn, (classmethod, types.BuiltinMethodType)):
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
    return '%s.%s' % (cls.__module__, cls.__qualname__)


def split_function_name(fn):
    """
    Given a method, return a tuple containing its fully-qualified
    class name and the method name.
    """
    qualname = fn.__qualname__
    if '.' in qualname:
        class_name, fn_name = qualname.rsplit('.', 1)
        class_name = '%s.%s' % (fn.__module__, class_name)
    else:
        class_name = fn.__module__
        fn_name = qualname
    return (class_name, fn_name)


class ProcRet:
    def __init__(self, returncode=0, stdout='', stderr=''):
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
        out = subprocess.check_output(command_args,
                                      stderr=subprocess.STDOUT,
                                      cwd=str(cwd), universal_newlines=True)
        return ProcRet(stdout=out, returncode=0)
    except subprocess.CalledProcessError as exc:
        return ProcRet(stderr=exc.stdout, returncode=exc.returncode)


class git:
    def __init__(self, cwd=None):
        self._cwd = cwd if cwd else os.getcwd()

    def __call__(self, cmd):
        return subprocess_run(
            shlex.split('git ' + cmd),
            cwd=self._cwd
        ).stdout.strip()

    @property
    def cwd(self):
        return self._cwd
