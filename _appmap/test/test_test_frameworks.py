"""Test cases dealing with various test framework runners and cases."""
# pylint: disable=missing-function-docstring

import json
import re
import sys
from abc import ABC, abstractmethod

import pytest

from _appmap import web_framework

from ..test.helpers import DictIncluding
from .normalize import normalize_appmap


class _TestTestRunner(ABC):
    """
    Test-runner test cases should inherit from this class to test disabling recording.

    Note that pytest won't collect classes with __init__ methods, so initialization of _test_type
    needs to be done in setup_class.
    """

    _test_type = ""

    @abstractmethod
    def run_tests(self, testdir):
        """Run the tests."""

    def test_with_appmap_false(self, testdir, monkeypatch):
        monkeypatch.setenv("APPMAP", "false")

        self.run_tests(testdir)

        assert not testdir.output().exists()

    def test_disabled(self, testdir, monkeypatch):
        monkeypatch.setenv(f"APPMAP_RECORD_{self._test_type.upper()}", "false")

        self.run_tests(testdir)
        assert not testdir.output().exists()


class TestUnittestRunner(_TestTestRunner):
    @classmethod
    def setup_class(cls):
        cls._test_type = "unittest"

    def run_tests(self, testdir):
        testdir.run(sys.executable, "-m", "unittest", "-vv")

    def test_enabled(self, testdir):
        self.run_tests(testdir)

        assert len(list(testdir.output().iterdir())) == 7
        verify_expected_appmap(testdir)
        verify_expected_metadata(testdir)


class TestPytestRunnerUnittest(_TestTestRunner):
    @classmethod
    def setup_class(cls):
        cls._test_type = "pytest"

    def run_tests(self, testdir):
        testdir.test_type = "pytest"
        result = testdir.runpytest("-svv")
        result.assert_outcomes(passed=3, failed=3, xfailed=1)

    def test_enabled(self, testdir):
        self.run_tests(testdir)
        # unittest cases run by pytest should get recorded as pytest tests
        assert len(list(testdir.output().iterdir())) == 7
        assert len(list(testdir.path.glob("tmp/appmap/unittest/*"))) == 0

        verify_expected_appmap(testdir)
        verify_expected_metadata(testdir)


@pytest.mark.example_dir("pytest")
class TestPytestRunnerPytest(_TestTestRunner):
    @classmethod
    def setup_class(cls):
        cls._test_type = "pytest"

    def run_tests(self, testdir):
        result = testdir.runpytest("-vv")
        result.assert_outcomes(passed=1, failed=2, xpassed=1, xfailed=1)

    def test_enabled(self, testdir):
        self.run_tests(testdir)
        assert len(list(testdir.output().iterdir())) == 5
        verify_expected_appmap(testdir)
        verify_expected_metadata(testdir)


@pytest.mark.example_dir("trial")
class TestPytestRunnerTrial(_TestTestRunner):
    @classmethod
    def setup_class(cls):
        cls._test_type = "pytest"

    def run_tests(self, testdir):
        testdir.test_type = "pytest"
        result = testdir.runpytest("-svv")
        # The single test for trial has been written so that it will xfail
        # if all the testing machinery is working correctly. If we've
        # somehow borked it up (e.g. by failing to return the Deferred
        # from the test case), it won't show as an expected failure. It
        # will either pass, or it will error out because the reactor is
        # unclean.
        result.assert_outcomes(xfailed=1)

    def test_pytest_trial(self, testdir):
        self.run_tests(testdir)
        verify_expected_appmap(testdir)


def test_overwrites_existing(tmp_path):
    foo_file = tmp_path / "foo.appmap.json"
    foo_file.write_text("existing")
    web_framework.write_appmap(tmp_path, "foo", "replacement")
    assert foo_file.read_text() == "replacement"


def test_write_appmap(tmp_path):
    web_framework.write_appmap(tmp_path, "foo", "bar")
    assert (tmp_path / "foo.appmap.json").read_text() == "bar"

    longname = "-".join(["testing"] * 42)
    web_framework.write_appmap(tmp_path, longname, "bar")
    expected_shortname = longname[:235] + "-5d6e10d.appmap.json"
    assert (tmp_path / expected_shortname).read_text() == "bar"


@pytest.fixture(name="testdir")
def fixture_runner_testdir(request, data_dir, pytester, monkeypatch):
    # The init subdirectory contains a sitecustomize.py file that
    # imports the appmap module. This simulates the way a real
    # installation works, performing the same function as the the
    # appmap.pth file that gets put in site-packages.
    monkeypatch.setenv("PYTHONPATH", "init")

    # Make sure APPMAP isn't the environment, to test that recording-by-default is working as
    # expected. Individual test cases may set it as necessary.
    monkeypatch.delenv("APPMAP", raising=False)

    marker = request.node.get_closest_marker("example_dir")
    test_type = "unittest" if marker is None else marker.args[0]
    pytester.copy_example(test_type)

    pytester.expected = data_dir / test_type / "expected"
    pytester.test_type = test_type

    # this is so test_type can be overriden in test cases
    def output_dir():
        return pytester.path / "tmp" / "appmap" / pytester.test_type

    pytester.output = output_dir

    return pytester


def verify_expected_appmap(testdir):
    appmap_json = list(testdir.output().glob("*test_hello_world.appmap.json"))
    assert len(appmap_json) == 1  # sanity check
    generated_appmap = normalize_appmap(appmap_json[0].read_text())

    appmap_json = testdir.expected / (f"{testdir.test_type}.appmap.json")
    expected_appmap = json.loads(appmap_json.read_text())

    assert generated_appmap == expected_appmap, f"expected appmap file {appmap_json}"


def verify_expected_metadata(testdir):
    """Verifies if the test outputs contain the expected metadata.
    The expected metadata are JSON documents with common
    suffix to the tests:
        test_foo.appmap.json -> foo.metadata.json
    """
    pattern = re.compile(r"test_(status_.+)\.appmap\.json")
    for file in testdir.output().glob("*test_status_*.appmap.json"):
        name = pattern.search(file.name).group(1)
        metadata = json.loads(file.read_text())["metadata"]
        expected = testdir.expected / f"{name}.metadata.json"
        assert metadata == DictIncluding(json.loads(expected.read_text()))
