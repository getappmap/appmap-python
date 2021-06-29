import json
import logging
import os
from pathlib import Path
import sys

import yaml

from .._implementation.configuration import Config

def _run():
    print(json.dumps({
        'configuration': {
            'filename': 'appmap.yml',
            'contents': yaml.dump(Config().default)
        }
    }))

    return 0

def run():
    sys.exit(_run())