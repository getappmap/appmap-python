"""Initialize from the environment"""
import logging
import logging.config
import os


def enabled():
    return os.getenv("APPMAP", "false") == "true"


def initialize():
    log_level = os.getenv("APPMAP_LOG_LEVEL", "warning").upper()
    logging.basicConfig(level=getattr(logging, log_level))

    log_config = os.getenv("APPMAP_LOG_CONFIG")
    if log_config is not None:
        name, level = log_config.split('=', 2)
        logging.config.dictConfig({
            "version": 1,
            "incremental": True,
            "loggers": {
                name: {
                    "level": level
                }
            }
        })
    logging.info('appmap enabled: %s', enabled())
