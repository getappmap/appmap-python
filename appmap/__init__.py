"""AppMap recorder for Python
PYTEST_DONT_REWRITE
"""
import os

# Note that we need to guard these imports with a conditional, rather than
# putting them in a function and conditionally calling the function. If we
# execute the imports in a function, the modules all get put into the funtion's
# globals, rather than into appmap's globals.
_enabled = os.environ.get("APPMAP", None)
_recording_exported = False
if _enabled is None or _enabled.upper() == "TRUE":
    if _enabled is not None:
        # Use setdefault so tests can manage _APPMAP as necessary
        os.environ.setdefault("_APPMAP", _enabled)
        from _appmap import generation  # noqa: F401
        from _appmap.env import Env  # noqa: F401
        from _appmap.importer import instrument_module  # noqa: F401
        from _appmap.labels import labels  # noqa: F401
        from _appmap.noappmap import decorator as noappmap  # noqa: F401
        from _appmap.recording import Recording  # noqa: F401
        _recording_exported = True

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
    else:
        os.environ.pop("_APPMAP", None)
else:
    os.environ.setdefault("_APPMAP", "false")

if not _recording_exported:
    # Client code that imports appmap.Recording should run correctly
    # even when not Env.current.enabled (not APPMAP=true).
    # This prevents:
    #   ImportError: cannot import name 'Recording' from 'appmap'...
    from _appmap.recording import NoopRecording as Recording # noqa: F401
