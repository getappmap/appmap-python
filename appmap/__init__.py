"""AppMap recorder for Python"""
import os

# Note that we need to guard these imports with a conditional, rather than
# putting them in a function and conditionally calling the function. If we
# execute the imports in a function, the modules all get put into the funtion's
# globals, rather than into appmap's globals.
if os.environ.get("APPMAP", "true").upper() == "TRUE":
    from _appmap import generation  # noqa: F401
    from _appmap.env import Env  # noqa: F401
    from _appmap.importer import instrument_module  # noqa: F401
    from _appmap.labels import labels  # noqa: F401
    from _appmap.noappmap import decorator as noappmap  # noqa: F401
    from _appmap.recording import Recording  # noqa: F401

    try:
        from . import django  # noqa: F401
    except ImportError:
        pass

    try:
        from . import flask  # noqa: F401
    except ImportError:
        pass

    try:
        from . import fastapi  # noqa: F401
    except ImportError:
        pass

    try:
        from . import uvicorn  # noqa: F401
    except ImportError:
        pass

    # Note: pytest integration is configured as a pytest plugin, so it doesn't
    # need to be imported here

    # unittest is part of the standard library, so it should always be
    # importable (and therefore doesn't need to be in a try .. except block)
    from . import unittest  # noqa: F401

    def enabled():
        return Env.current.enabled
