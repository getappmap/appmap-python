import platform
import sys


class AppMapPyVerException(Exception):
    pass


# Library code uses these, so provide intermediate
# functions that can be stubbed when testing.
def _get_py_version():
    return sys.version_info


def _get_platform_version():
    return platform.python_version()


def check_py_version():
    req = (3, 6)
    actual = _get_platform_version()
    if _get_py_version() < req:
        raise AppMapPyVerException(
            f"Minimum Python version supported is {req[0]}.{req[1]}, found {actual}"
        )
