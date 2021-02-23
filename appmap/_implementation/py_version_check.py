import platform
import sys


class AppMapPyVerException(Exception):
    pass


def check_py_version():
    MIN_PY_VERSION = (3, 5)
    if sys.version_info < MIN_PY_VERSION:
        raise AppMapPyVerException(
            'Minimum Python version supported is %s, found %s' %
            (MIN_PY_VERSION, platform.python_version())
        )
