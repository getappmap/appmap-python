from argparse import ArgumentParser
from importlib_metadata import distribution, version, PackageNotFoundError
import json
import os
from pathlib import Path
import sys
import time

import yaml

from .helpers import has_dist
from .._implementation.configuration import Config

def _run():
    config = Config()

    can_record = has_dist('Django') or has_dist('Flask')

    properties = {
        'properties': {
            'config': {
                'app': config.name,
                'present': config.file_present,
                'valid': config.file_valid
            },
            'project': {
                'agentVersion': version('appmap'),
                'language': 'python',
                'remoteRecordingCapable': can_record,
            }
        }
    }

    test_commands = config.test_commands
    if test_commands:
        properties['test_commands'] = config.test_commands

    print(json.dumps(properties))

    return 0

def run():
    parser = ArgumentParser(description="Report project status for AppMap agent.")
    sys.exit(_run())
