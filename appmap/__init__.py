"""AppMap recorder for Python"""

from ._implementation.recording import Recording  # noqa: F401
from ._implementation import generation  # noqa: F401

from ._implementation.py_version_check import check_py_version
check_py_version()
