"""Initialize from the environment"""
import logging
import logging.config
import os


class _EnvMeta(type):
    def __init__(cls, *args, **kwargs):
        type.__init__(cls, *args, **kwargs)
        cls._instance = None

    @property
    def current(cls):
        if not cls._instance:
            cls._instance = Env()

        return cls._instance

    def reset(cls):
        cls._instance = None


class Env(metaclass=_EnvMeta):
    def __init__(self):
        # root_dir and root_dir_len are going to be used when
        # instrumenting every function, so preprocess them as
        # much as possible.
        self._root_dir = str(os.path.join(os.getcwd()) + '/')
        self._root_dir_len = len(self._root_dir)

        output_dir = os.getenv("APPMAP_OUTPUT_DIR",
                               os.path.join('tmp', 'appmap'))
        self._output_dir = os.path.abspath(output_dir)

        _configure_logging()

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
        # There are currently tests that depend on being able to
        # toggle the state of enabled by changing the value of APPMAP
        # in environment. So, don't cache it for now.
        return os.getenv("APPMAP", "false") == "true"


def _configure_logging():
    log_level = os.getenv("APPMAP_LOG_LEVEL", "warning").upper()

    log_config = os.getenv("APPMAP_LOG_CONFIG")
    log_stream = os.getenv("APPMAP_LOG_STREAM", "stderr")
    log_stream = 'ext://sys.%s' % (log_stream)
    config_dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'style': '{',
                'format': '[{asctime}] {levelname} {name}: {message}'
            }
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            }
        },
        'loggers': {
            'appmap': {
                'level': log_level,
                'handlers': ['default'],
                'propagate': False
            }
        }
    }
    if log_config is not None:
        name, level = log_config.split('=', 2)
        config_dict['loggers'].update({
            name: {
                'level': level.upper(),
                'handlers': ['default'],
                'propagate': False
            }
        })
    logging.config.dictConfig(config_dict)


def initialize():
    Env.reset()
    logging.info('appmap enabled: %s', Env.current.enabled)
