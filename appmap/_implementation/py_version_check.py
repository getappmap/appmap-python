import platform
import sys


class AppMapPyVerException(Exception):
    pass


def check_py_version():
    MIN_PY_VERSION = (3, 9)
    if sys.version_info < MIN_PY_VERSION:
        raise AppMapPyVerException(f'Minimum Python version supported is {MIN_PY_VERSION}, found {platform.python_version()}')
