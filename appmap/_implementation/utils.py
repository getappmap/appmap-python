import threading
import types
from collections.abc import MutableMapping
from collections import namedtuple
import shlex
import subprocess
import os

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


def is_staticmethod(m):
    return isinstance(m, (staticmethod, types.BuiltinMethodType))


def is_classmethod(m):
    return isinstance(m, (classmethod, types.BuiltinMethodType))


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


def subprocess_run(command_args, cwd=None):
    if not cwd:
        cwd = os.getcwd()
    Ret = namedtuple('Ret', ['returncode', 'stdout'])
    try:
        out = subprocess.check_output(command_args,
                                      cwd=str(cwd), universal_newlines=True)
        return Ret(stdout=out, returncode=0)
    except subprocess.CalledProcessError as exc:
        return Ret(stdout=exc.stdout, returncode=exc.returncode)

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
