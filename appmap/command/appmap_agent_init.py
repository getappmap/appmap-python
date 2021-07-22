import json
import logging
import os
from pathlib import Path
import sys

import yaml

from .helpers import has_dist
from .._implementation.configuration import Config

logger = logging.getLogger(__name__)

class AgentFileCollector:
    def __init__(self):
        self.collected = set()

    def pytest_collection_modifyitems(self, items):
        for item in items:
            self.collected.add(item.fspath)
        items.clear()


def discover_pytest_tests():
    """
    Use pytest to discover all test files for the current project.
    Disables logging from pytest, but otherwise, uses pytest's default
    options.  This means that if the project has a pytest.ini, it will
    be used.
    """

    logger.info("discovering pytest tests")
    # --capture=no => don't muck with stdout/stderr
    # --verbosity=-2 => don't do any logging during collection, and don't show warning summary
    # --disable-warnings => don't show warning summary
    #
    collector = AgentFileCollector()

    import pytest
    pytest.main(['--collect-only',
                 '--capture=no', '--verbosity=-2', '--disable-warnings',
                 ], plugins=[collector])

    logger.info("found %d pytest test(s)", len(collector.collected))
    return collector.collected

def has_pytest_tests():
    return len(discover_pytest_tests()) > 0

def has_unittest_tests():
    return False


def _run():
    uses_pytest = has_dist('pytest')

    has_tests = None
    if uses_pytest:
        has_tests = has_pytest_tests()
    else:
        has_tests = has_unittest_tests()

    if has_tests:
        appmap_env = {
            "environment": {
                "APPMAP": "true"
            }
        }

        if uses_pytest:
            test_command = {
                "framework": "pytest",
                "command": {
                    "program": "pytest"
                }
            }
        else:
            test_command = {
                "framework": "unittest",
                "command": {
                    "program": "python",
                    "args": ["-m", "unittest"]
                }
            }
        test_command["command"].update(appmap_env)

    else:
        test_command = None

    config = Config().default
    if test_command is not None:
        config["test_commands"] = [test_command]

    yaml_config = yaml.dump(config)
    print(json.dumps({
        'configuration': {
            'filename': 'appmap.yml',
            'contents': yaml_config
        }
    }))

    return 0

def run():
    sys.exit(_run())
