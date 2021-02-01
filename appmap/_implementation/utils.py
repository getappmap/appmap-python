import threading
import types
from collections.abc import MutableMapping
import subprocess


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
    return f'{cls.__module__}.{cls.__qualname__}'


def split_function_name(fn):
    """
    Given a method, return a tuple containing its fully-qualified
    class name and the method name.
    """
    qualname = fn.__qualname__
    if '.' in qualname:
        class_name, fn_name = qualname.rsplit('.', 1)
        class_name = f'{fn.__module__}.{class_name}'
    else:
        class_name = fn.__module__
        fn_name = qualname
    return (class_name, fn_name)


def subprocess_run(command_args):
    return subprocess.run(command_args, capture_output=True, text=True, check=False)
