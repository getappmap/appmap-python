"""Initialize from the environment"""
import logging
import os

_log_level = os.getenv("APPMAP_LOG_LEVEL", "warning").upper()
logging.basicConfig(level=getattr(logging, _log_level))


def enabled():
    is_enabled = os.getenv("APPMAP", "false") == "true"
    logging.info('appmap enabled: %s', is_enabled)
    return is_enabled
