"""Test cases dealing with various test framework runners and cases."""

# pylint: disable=missing-function-docstring

import json
import re
import sys
import types
from abc import ABC, abstractmethod
from pathlib import Path

import pytest

from _appmap import recording

from .helpers import DictIncluding, check_call_stack, package_version
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
        monkeypatch.setenv("_APPMAP", "false")

        self.run_tests(testdir)

        assert not testdir.output().exists()

    def test_disabled(self, testdir, monkeypatch):
        monkeypatch.setenv("APPMAP_RECORD_TESTS", "false")

        self.run_tests(testdir)
        assert not testdir.output().exists()

    def test_disabled_for_process(self, testdir, monkeypatch):
        monkeypatch.setenv("APPMAP_RECORD_PROCESS", "true")

        self.run_tests(testdir)
        assert (testdir.path / "tmp" / "appmap" / "process").exists()
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

    def test_enabled_no_test_cases(self, testdir, monkeypatch):
        monkeypatch.setenv("APPMAP_CONFIG", "appmap-no-test-cases.yml")

        self.run_tests(testdir)

        assert len(list(testdir.output().iterdir())) == 7
        verify_expected_appmap(testdir, "-no-test-cases")
        verify_expected_metadata(testdir)

class TestPytestRunnerUnittest(_TestTestRunner):
    @classmethod
    def setup_class(cls):
        cls._test_type = "pytest"

    def run_tests(self, testdir):
        testdir.test_type = "pytest"
        result = testdir.runpytest("-svv")
        result.assert_outcomes(passed=5, failed=3, xfailed=1)

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
        result = testdir.runpytest("-svv")
        result.assert_outcomes(passed=4, failed=2, xpassed=1, xfailed=1)

    def test_enabled(self, testdir):
        self.run_tests(testdir)
        assert len(list(testdir.output().iterdir())) == 6
        numpy_version = package_version("numpy")
        verify_expected_appmap(testdir, f"-numpy{numpy_version.major}")
        verify_expected_metadata(testdir)

    def test_enabled_no_test_cases(self, testdir, monkeypatch):
        monkeypatch.setenv("APPMAP_CONFIG", "appmap-no-test-cases.yml")

        self.run_tests(testdir)
        assert len(list(testdir.output().iterdir())) == 6
        numpy_version = package_version("numpy")
        verify_expected_appmap(testdir, f"-numpy{numpy_version.major}-no-test-cases")
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

    def test_enabled(self, testdir):
        self.run_tests(testdir)
        verify_expected_appmap(testdir)

    def test_enabled_no_test_cases(self, testdir, monkeypatch):
        monkeypatch.setenv("APPMAP_CONFIG", "appmap-no-test-cases.yml")
        self.run_tests(testdir)
        verify_expected_appmap(testdir, "-no-test-cases")


EMPTY_APPMAP = types.SimpleNamespace(events=[])

RECORDER_TYPE = "test"


@pytest.fixture(name="recorder_outdir")
def _recorder_outdir(tmp_path) -> Path:
    ret = tmp_path / RECORDER_TYPE
    ret.mkdir(parents=True)
    return ret


def test_overwrites_existing(recorder_outdir):
    foo_file = recorder_outdir / "foo.appmap.json"
    foo_file.write_text("existing")
    recording.write_appmap(EMPTY_APPMAP, "foo", RECORDER_TYPE, None, recorder_outdir.parent)
    assert foo_file.read_text().startswith('{"version"')


def test_write_appmap(recorder_outdir):
    recording.write_appmap(EMPTY_APPMAP, "foo", RECORDER_TYPE, None, recorder_outdir.parent)
    assert (recorder_outdir / "foo.appmap.json").read_text().startswith('{"version"')

    longname = "-".join(["testing"] * 42)
    recording.write_appmap(EMPTY_APPMAP, longname, RECORDER_TYPE, None, recorder_outdir.parent)
    expected_shortname = longname[:235] + "-5d6e10d.appmap.json"
    assert (recorder_outdir / expected_shortname).read_text().startswith('{"version"')

@pytest.mark.example_dir("pytest-instrumented")
@pytest.mark.appmap_enabled
def test_pytest_instrumented(testdir):
    result = testdir.runpytest("-svv", "-p", "pytester", "test_instrumented.py")
    result.assert_outcomes(passed=1)
    appmap_file = testdir.path / "tmp" / "appmap" / "pytest" / "test_skipped.appmap.json"
    appmap = json.load(appmap_file.open())
    events = appmap["events"]
    assert len(events) > 0
    check_call_stack(events)


def verify_expected_appmap(testdir, suffix=""):
    appmap_json = list(testdir.output().glob("*test_hello_world.appmap.json"))
    assert len(appmap_json) == 1  # sanity check
    generated_appmap = normalize_appmap(appmap_json[0].read_text())

    appmap_json = testdir.expected / (f"{testdir.test_type}{suffix}.appmap.json")
    expected_appmap = json.loads(appmap_json.read_text())

    assert generated_appmap == expected_appmap, (
        f"expected appmap file {appmap_json}\n"
        + f"generated appmap: {json.dumps(generated_appmap, indent=2)}"
    )


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
        assert metadata == DictIncluding(
            json.loads(expected.read_text())
        ), f"expected appmap: {file}"
