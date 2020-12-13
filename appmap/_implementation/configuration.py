"""
Manage Configuration AppMap recorder for Python
"""

import logging
import os
import yaml


logging.basicConfig(level=getattr(logging, os.getenv("APPMAP_LOG_LEVEL", "warning").upper()))


def appmap_enabled():
    return os.getenv("APPMAP", "false") == "true"


def appmap_config():
    config_file = os.getenv("APPMAP_CONFIG", "appmap.yml")
    with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.BaseLoader)
        logging.debug('config %s', config)

    return config
