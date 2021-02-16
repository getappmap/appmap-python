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
            'root': {
                'level': log_level,
                'handlers': ['default']
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
    _configure_logging()
    logging.info('appmap enabled: %s', enabled())
