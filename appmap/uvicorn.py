# uvicorn integration
from uvicorn.config import Config

from _appmap import wrapt
from _appmap.env import Env


def install_extension(wrapped, config, args, kwargs):
    wrapped(*args, **kwargs)
    try:
        # pylint: disable=import-outside-toplevel
        from .fastapi import FastAPIInserter

        # pylint: enable=import-outside-toplevel

        app = config.loaded_app
        if app:
            # uvicorn doc recommends running with `--reload` in development, so use
            # that to decide whether to enable remote recording
            config.loaded_app = FastAPIInserter(config.loaded_app, config.reload).run()
    except ImportError:
        # Not FastAPI
        pass


if Env.current.enabled:
    Config.load = wrapt.wrap_function_wrapper("uvicorn.config", "Config.load", install_extension)
