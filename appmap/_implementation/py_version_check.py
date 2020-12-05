import platform

MIN_PY_VERSION = 3.8

class AppMapPyVerException(Exception):
    pass


def check_py_version():
    cur_py_version = [int(x) for x in platform.python_version_tuple()]

    min_py_version = [int(x) for x in str(MIN_PY_VERSION).split('.')]

    if cur_py_version[0] < min_py_version[0] or cur_py_version[1] < min_py_version[1]:
        raise AppMapPyVerException(f'Minimum Python version supported is {MIN_PY_VERSION}, found {platform.python_version()}')
