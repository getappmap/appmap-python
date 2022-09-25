import json
import logging
import os
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import yaml
from importlib_metadata import PackageNotFoundError, distribution, version

from .._implementation.configuration import Config

logger = logging.getLogger(__name__)


def has_dist(dist):
    try:
        distribution(dist)
        return True
    except PackageNotFoundError:
        pass
    return False


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

    pytest.main(
        [
            "--collect-only",
            "--capture=no",
            "--verbosity=-2",
            "--disable-warnings",
        ],
        plugins=[collector],
    )

    logger.info("found %d pytest test(s)", len(collector.collected))
    return collector.collected


def has_pytest_tests():
    return len(discover_pytest_tests()) > 0


def has_unittest_tests():
    return False


def _run(*, discover_tests):
    config = Config()
    uses_pytest = has_dist("pytest")

    has_tests = None
    if discover_tests:
        if uses_pytest:
            has_tests = has_pytest_tests()
        else:
            has_tests = has_unittest_tests()

    if has_tests:
        test_command = {"args": [], "environment": {"APPMAP": "true"}}

        if uses_pytest:
            test_command.update({"framework": "pytest", "command": "pytest"})
        else:
            test_command.update(
                {
                    "framework": "unittest",
                    "command": "python",
                    "args": ["-m", "unittest"],
                }
            )
    else:
        test_command = None

    can_record = has_dist("Django") or has_dist("Flask")

    properties = {
        "properties": {
            "config": {
                "app": config.name,
                "present": config.file_present,
                "valid": config.file_valid,
            },
            "project": {
                "agentVersion": version("appmap"),
                "language": "python",
                "remoteRecordingCapable": can_record,
            },
        }
    }

    if has_tests is not None:
        properties["properties"]["project"]["integrationTests"] = has_tests
        if has_tests:
            properties["test_commands"] = [test_command]

    if test_command:
        properties.update({})

    print(json.dumps(properties))

    return 0


def run():
    parser = ArgumentParser(description="Report project status for AppMap agent.")
    parser.add_argument(
        "--discover-tests", action="store_true", help="Scan the project for tests"
    )
    args = parser.parse_args()
    sys.exit(_run(discover_tests=args.discover_tests))
