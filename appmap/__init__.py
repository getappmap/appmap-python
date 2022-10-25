"""AppMap recorder for Python"""
from ._implementation import generation  # noqa: F401
from ._implementation.env import Env  # noqa: F401
from ._implementation.importer import instrument_module  # noqa: F401
from ._implementation.labels import labels  # noqa: F401
from ._implementation.recording import Recording  # noqa: F401

try:
    from . import django  # noqa: F401
except ImportError:
    # not using django
    pass

try:
    from . import flask  # noqa: F401
except ImportError:
    # not using flask
    pass


def enabled():
    return Env.current.enabled
