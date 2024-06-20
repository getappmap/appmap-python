"""Initialize from the environment"""

import logging
import logging.config
import os
from contextlib import contextmanager
from os import environ
from pathlib import Path
from typing import cast

from _appmap.singleton import SingletonMeta

from . import trace_logger

_cwd = Path.cwd()
_bootenv = environ.copy()


def _recording_method_key(recording_method):
    return f"APPMAP_RECORD_{recording_method.upper()}"


class Env(metaclass=SingletonMeta):
    RECORD_PROCESS_DEFAULT = "false"

    def __init__(self, env=None, cwd=None):
        # root_dir and root_dir_len are going to be used when
        # instrumenting every function, so preprocess them as
        # much as possible.

        self._cwd = cwd or _cwd
        self._env = _bootenv.copy()
        if env:
            for k, v in env.items():
                if v is not None:
                    self._env[k] = v
                else:
                    self._env.pop(k, None)

        self.log_file_creation_failed = False
        self._configure_logging()
        enabled = self._env.get("_APPMAP", "false")
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

    def setdefault(self, name, default_value):
        self._env.setdefault(name, default_value)

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
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    def enables(self, recording_method, default="true"):
        if not self.enabled:
            return False

        process_enabled = self._enables("process", self.RECORD_PROCESS_DEFAULT)
        if recording_method == "process":
            return process_enabled

        # If process recording is enabled, others should be disabled
        if process_enabled:
            return False

        # Otherwise, check the environment variable
        return self._enables(recording_method, default)

    def _enables(self, recording_method, default):
        return self.get(_recording_method_key(recording_method), default).lower() != "false"

    @contextmanager
    def disabled(self, recording_method: str):
        key = _recording_method_key(recording_method)
        value = self.get(key)
        self.setdefault(key, "false")
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

    def determine_log_file(self):
        log_file = "appmap.log"

        # Try creating the log file in the current directory
        try:
            with open(log_file, 'a', encoding='UTF8'):
                pass
        except IOError:
            # The circumstances in which creation is going to fail
            # are also those in which the user doesn't care whether
            # there's a log file (e.g. when starting a REPL).
            return None
        return log_file


    def _configure_logging(self):
        trace_logger.install()

        log_level = self.get("APPMAP_LOG_LEVEL", "warn").upper()
        disable_log = os.environ.get("APPMAP_DISABLE_LOG_FILE", "false").upper() != "FALSE"
        log_config = self.get("APPMAP_LOG_CONFIG")
        config_dict = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "style": "{",
                    "format": "[{asctime}] {levelname} {name}: {message}",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "stderr": {
                    "class": "logging.StreamHandler",
                    "level": "WARNING",
                    "formatter": "default",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "appmap": {
                    "level": log_level,
                    "handlers": ["default", "stderr"],
                    "propagate": True,
                },
                "_appmap": {
                    "level": log_level,
                    "handlers": ["default", "stderr"],
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

            log_file = self.determine_log_file()
            # Use NullHandler if log_file is None to avoid complicating the configuration
            # with the absence of the "default" handler.
            config_dict["handlers"] = {
                "default": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "default",
                    "filename": log_file,
                    "maxBytes": 50 * 1024 * 1024,
                    "backupCount": 1,
                } if log_file is not None else {
                    "class": "logging.NullHandler"
                },
                "stderr": {
                    "class": "logging.StreamHandler",
                    "level": "WARNING",
                    "formatter": "default",
                    "stream": "ext://sys.stderr",
                },
            }
            self.log_file_creation_failed = log_file is None

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
    if Env.current.log_file_creation_failed:
        # Writing to stderr makes the REPL fail in vscode-python.
        # https://github.com/microsoft/vscode-python/blob/c71c85ebf3749d5fac76899feefb21ee321a4b5b/src/client/common/process/rawProcessApis.ts#L268-L269
        logger.info("appmap.log cannot be created")
