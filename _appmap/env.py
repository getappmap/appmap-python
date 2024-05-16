"""Initialize from the environment"""

import logging
import logging.config
import os
import warnings
from contextlib import contextmanager
from datetime import datetime
from os import environ
from pathlib import Path
from typing import cast

from _appmap.singleton import SingletonMeta

from . import trace_logger

_ENABLED_BY_DEFAULT_MSG = """

The APPMAP environment variable is unset. Your code will be
instrumented and recorded according to the configuration in appmap.yml.

Starting with version 2, this behavior will change: when APPMAP is
unset, no code will be instrumented. You will need to use the
appmap-python script to run your application, or explicitly set
APPMAP.

Visit https://appmap.io/docs/reference/appmap-python.html#appmap-python-script for more
details.
"""

_cwd = Path.cwd()
_bootenv = environ.copy()


def _recording_method_key(recording_method):
    return f"APPMAP_RECORD_{recording_method.upper()}"


class Env(metaclass=SingletonMeta):
    def __init__(self, env=None, cwd=None):
        warnings.filterwarnings("once", _ENABLED_BY_DEFAULT_MSG)

        # root_dir and root_dir_len are going to be used when
        # instrumenting every function, so preprocess them as
        # much as possible.

        self._cwd = cwd or _cwd
        self._env = _bootenv.copy()
        if env:
            self._env.update(env)

        self._configure_logging()
        enabled = self._env.get("_APPMAP", None)
        self._enabled_by_default = enabled is None
        self._enabled = enabled is None or enabled.lower() != "false"

        self._root_dir = str(self._cwd) + "/"
        self._root_dir_len = len(self._root_dir)

        logger = logging.getLogger(__name__)
        # The user shouldn't set APPMAP_OUTPUT_DIR, but some tests depend on being able to use it.
        appmap_output_dir = self.get("APPMAP_OUTPUT_DIR", None)
        if appmap_output_dir is not None:
            logger.warning("Setting APPMAP_OUTPUT_DIR is not supported")
        else:
            appmap_output_dir = "tmp/appmap"

        self._output_dir = Path(appmap_output_dir).resolve()

    def set(self, name, value):
        self._env[name] = value

    def get(self, name, default=None):
        return self._env.get(name, default)

    def delete(self, name):
        del self._env[name]

    @property
    def root_dir(self):
        return self._root_dir

    @property
    def root_dir_len(self):
        return self._root_dir_len

    @property
    def output_dir(self):
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value):
        self._output_dir = value

    @property
    def enabled_by_default(self):
        return self._enabled_by_default

    def warn_enabled_by_default(self):
        if self._enabled_by_default:
            warnings.warn(_ENABLED_BY_DEFAULT_MSG, category=DeprecationWarning, stacklevel=2)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    def enables(self, recording_method, default="true"):
        if not self.enabled:
            return False

        v = self.get(_recording_method_key(recording_method), default).lower()
        return v != "false"

    @contextmanager
    def disabled(self, recording_method: str):
        key = _recording_method_key(recording_method)
        value = self.get(key)
        self.set(key, "false")
        try:
            yield
        finally:
            self.delete(key)
            if value:
                self.set(key, value)

    @property
    def is_appmap_repo(self):
        return os.path.exists("appmap/__init__.py") and os.path.exists(
            "_appmap/__init__.py"
        )

    @property
    def display_params(self):
        return self.get("APPMAP_DISPLAY_PARAMS", "true").lower() == "true"

    def getLogger(self, name) -> trace_logger.TraceLogger:
        return cast(trace_logger.TraceLogger, logging.getLogger(name))

    def _configure_logging(self):
        trace_logger.install()

        log_level = self.get("APPMAP_LOG_LEVEL", "warn").upper()
        disable_log = os.environ.get("APPMAP_DISABLE_LOG_FILE", "true").upper() != "FALSE"
        log_config = self.get("APPMAP_LOG_CONFIG")
        now = datetime.now()
        config_dict = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "style": "{",
                    "format": "[{asctime}] {levelname} {name}: {message}",
                }
            },
            "handlers": {"default": {"class": "logging.StreamHandler", "formatter": "default"}},
            "loggers": {
                "appmap": {
                    "level": log_level,
                    "handlers": ["default"],
                    "propagate": True,
                },
                "_appmap": {
                    "level": log_level,
                    "handlers": ["default"],
                    "propagate": True,
                },
            },
        }
        if not disable_log:
            # Default to being more verbose if we're logging to a file, but
            # still allow the level to be overridden.
            log_level = self.get("APPMAP_LOG_LEVEL", "info").upper()
            loggers = config_dict["loggers"]
            loggers["appmap"]["level"] = loggers["_appmap"]["level"] = log_level
            config_dict["handlers"] = {
                "default": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "filename": f"appmap-{now:%Y%m%d%H%M%S}-{os.getpid()}.log",
                }
            }

        if log_config is not None:
            name, level = log_config.split("=", 2)
            config_dict["loggers"].update(
                {
                    name: {
                        "level": level.upper(),
                        "handlers": ["default"],
                        "propagate": True,
                    }
                }
            )
        logging.config.dictConfig(config_dict)


def initialize(**kwargs):
    Env.reset(**kwargs)
    logger = logging.getLogger(__name__)
    logger.info("appmap enabled: %s", Env.current.enabled)
