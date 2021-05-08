import sys

import json
import pytest

from .normalize import normalize_appmap

@pytest.fixture(name='runner_testdir')
def fixture_runner_testdir(request, pytester, monkeypatch):
    marker = request.node.get_closest_marker('example_dir')
    pytester.example_dir = 'unittest' if marker is None else marker.args[0]
    pytester.copy_example(pytester.example_dir)
    monkeypatch.setenv('APPMAP', 'true')

    # The init subdirectory contains a sitecustomize.py file that
    # imports the appmap module. This simulates the way a real
    # installation works, performing the same function as the the
    # appmap.pth file that gets put in site-packages.
    monkeypatch.setenv('PYTHONPATH', 'init')
    return pytester

def verify_expected_appmap(data_dir, testdir, test_type):
    out_dir = testdir.path / 'tmp/appmap' / test_type
    appmap_json = list(out_dir.glob('**/*_test_hello_world.appmap.json'))
    assert len(appmap_json) == 1 # sanity check
    generated_appmap = normalize_appmap(appmap_json[0].read_text())

    appmap_json = data_dir / testdir.example_dir / (f'expected.{test_type}.appmap.json')
    expected_appmap = json.loads(appmap_json.read_text())

    assert generated_appmap == expected_appmap


def test_appmap_unittest_runner(data_dir, runner_testdir):
    runner_testdir.run(sys.executable, '-m', 'appmap.unittest', '-vv')

    verify_expected_appmap(data_dir, runner_testdir, 'unittest')

def test_pytest_runner(data_dir, runner_testdir):
    result = runner_testdir.runpytest('-svv')
    result.assert_outcomes(passed=2, failed=2, xfailed=1)

    # unittest cases run by pytest should get recorded as pytest
    # tests
    path = runner_testdir.path
    assert len(list(path.glob('tmp/appmap/pytest/*'))) == 5
    assert len(list(path.glob('tmp/appmap/unittest/*'))) == 0

    verify_expected_appmap(data_dir, runner_testdir, 'pytest')

def test_unittest_runner(data_dir, runner_testdir):
    runner_testdir.run(sys.executable, '-m', 'unittest', '-vv')

    assert len(list(runner_testdir.path.glob('tmp/appmap/unittest/*'))) == 5
    verify_expected_appmap(data_dir, runner_testdir, 'unittest')

@pytest.mark.example_dir('trial')
def test_pytest_trial(data_dir, runner_testdir):
    result = runner_testdir.runpytest('-svv')

    # The single test for trial has been written so that it will xfail
    # if all the testing machinery is working correctly. If we've
    # somehow borked it up (e.g. by failing to return the Deferred
    # from the test case), it won't show as an expected failure. It
    # will either pass, or it will error out because the reactor is
    # unclean.
    result.assert_outcomes(xfailed=1)
    verify_expected_appmap(data_dir, runner_testdir, 'pytest')
