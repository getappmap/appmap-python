"""Initialize from the environment"""

import logging
import logging.config
from os import environ
from pathlib import Path

from .detect_enabled import DetectEnabled

_cwd = Path.cwd()
_bootenv = environ.copy()


class _EnvMeta(type):
    def __init__(cls, *args, **kwargs):
        type.__init__(cls, *args, **kwargs)
        cls._instance = None

    @property
    def current(cls):
        if not cls._instance:
            cls._instance = Env()

        return cls._instance

    def reset(cls, **kwargs):
        cls._instance = Env(**kwargs)


class Env(metaclass=_EnvMeta):
    def __init__(self, env=None, cwd=None):
        # root_dir and root_dir_len are going to be used when
        # instrumenting every function, so preprocess them as
        # much as possible.
        self._cwd = cwd or _cwd
        self._env = _bootenv.copy()
        if env:
            self._env.update(env)

        self._configure_logging()
        self._enabled = DetectEnabled.any_enabled()

        self._root_dir = str(self._cwd) + "/"
        self._root_dir_len = len(self._root_dir)

        output_dir = Path(self.get("APPMAP_OUTPUT_DIR", "tmp/appmap"))
        self._output_dir = output_dir.resolve()

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

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    @property
    def display_params(self):
        return self.get("APPMAP_DISPLAY_PARAMS", "true").lower() == "true"

    def _configure_logging(self):
        log_level = self.get("APPMAP_LOG_LEVEL", "info").upper()

        log_config = self.get("APPMAP_LOG_CONFIG")
        log_stream = self.get("APPMAP_LOG_STREAM", "stderr")
        log_stream = "ext://sys.%s" % (log_stream)
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
                "default": {"class": "logging.StreamHandler", "formatter": "default"}
            },
            "loggers": {
                "appmap": {
                    "level": log_level,
                    "handlers": ["default"],
                    "propagate": True,
                }
            },
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
    DetectEnabled.initialize()
    Env.reset(**kwargs)
    logging.info("appmap enabled: %s", Env.current.enabled)
