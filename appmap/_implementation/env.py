"""Initialize from the environment"""
import logging
import logging.config
import os

_log_level = os.getenv("APPMAP_LOG_LEVEL", "warning").upper()
logging.basicConfig(level=getattr(logging, _log_level))

_log_config = os.getenv("APPMAP_LOG_CONFIG")
if _log_config is not None:
    name, level = _log_config.split('=', 2)
    logging.config.dictConfig({
        "version": 1,
        "incremental": True,
        "loggers": {
            name: {
                "level": level
            }
        }
    })


def enabled():
    is_enabled = os.getenv("APPMAP", "false") == "true"
    return is_enabled

logging.info('appmap enabled: %s', enabled())
