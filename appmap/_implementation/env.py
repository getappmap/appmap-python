"""Initialize from the environment"""
import logging
import logging.config
import os


def enabled():
    return os.getenv("APPMAP", "false") == "true"


def _configure_logging():
    log_level = os.getenv("APPMAP_LOG_LEVEL", "warning").upper()

    log_config = os.getenv("APPMAP_LOG_CONFIG")
    log_stream = os.getenv("APPMAP_LOG_STREAM", "stderr")
    log_stream = f'ext://sys.{log_stream}'
    config_dict = {
        "version": 1,
        'formatters': {
            'default': {
                'class': 'logging.Formatter',
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        "handlers": {
            "appmap_log_handler": {
                "class": "logging.StreamHandler",
                "stream": log_stream,
                "formatter": "default"
            }
        },
        "root": {
            "handlers": ["appmap_log_handler"],
            "level": getattr(logging, log_level)
        }
    }
    if log_config is not None:
        name, level = log_config.split('=', 2)
        config_dict.update({
            "loggers": {
                name: {
                    "level": level,
                    "handlers": ["appmap_log_handler"]
                }
            }
        })
    logging.config.dictConfig(config_dict)


def initialize():
    _configure_logging()
    logging.info('appmap enabled: %s', enabled())
