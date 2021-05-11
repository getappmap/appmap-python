import sys

import json
import pytest

from .normalize import normalize_appmap

def test_unittest_runner(testdir):
    testdir.run(sys.executable, '-m', 'unittest', '-vv')

    assert len(list(testdir.output().iterdir())) == 5
    verify_expected_appmap(testdir)


def test_appmap_unittest_runner(testdir):
    testdir.run(sys.executable, '-m', 'appmap.unittest', '-vv')

    verify_expected_appmap(testdir)


def test_pytest_runner_unittests(testdir):
    testdir.test_type = 'pytest'
    result = testdir.runpytest('-svv')
    result.assert_outcomes(passed=2, failed=2, xfailed=1)

    # unittest cases run by pytest should get recorded as pytest tests
    assert len(list(testdir.output().iterdir())) == 5
    assert len(list(testdir.path.glob('tmp/appmap/unittest/*'))) == 0

    verify_expected_appmap(testdir)


@pytest.mark.example_dir('pytest')
def test_pytest_runner_pytest(testdir):
    result = testdir.runpytest('-vv')
    result.assert_outcomes(passed=1, failed=1, xpassed=1, xfailed=1)

    assert len(list(testdir.output().iterdir())) == 4
    verify_expected_appmap(testdir)


@pytest.mark.example_dir('pytest')
def test_overwrites_existing(testdir):
    appmap_json = testdir.output() / 'test_hello_world.appmap.json'
    appmap_json.parent.mkdir(parents=True, exist_ok=True)
    appmap_json.touch()

    result = testdir.runpytest('-vv', '-k', 'test_hello_world')
    result.assert_outcomes(passed=1)
    verify_expected_appmap(testdir)


@pytest.mark.example_dir('trial')
def test_pytest_trial(testdir):
    testdir.test_type = 'pytest'
    result = testdir.runpytest('-svv')

    # The single test for trial has been written so that it will xfail
    # if all the testing machinery is working correctly. If we've
    # somehow borked it up (e.g. by failing to return the Deferred
    # from the test case), it won't show as an expected failure. It
    # will either pass, or it will error out because the reactor is
    # unclean.
    result.assert_outcomes(xfailed=1)
    verify_expected_appmap(testdir)


@pytest.fixture(name='testdir')
def fixture_runner_testdir(request, data_dir, pytester, monkeypatch):
    # The init subdirectory contains a sitecustomize.py file that
    # imports the appmap module. This simulates the way a real
    # installation works, performing the same function as the the
    # appmap.pth file that gets put in site-packages.
    monkeypatch.setenv('PYTHONPATH', 'init')

    monkeypatch.setenv('APPMAP', 'true')

    marker = request.node.get_closest_marker('example_dir')
    test_type = 'unittest' if marker is None else marker.args[0]
    pytester.copy_example(test_type)

    pytester.expected = data_dir / test_type / 'expected'
    pytester.test_type = test_type

    # this is so test_type can be overriden in test cases
    def output_dir():
        return pytester.path / 'tmp' / 'appmap' / pytester.test_type
    pytester.output = output_dir

    return pytester


def verify_expected_appmap(testdir):
    appmap_json = list(testdir.output().glob('*test_hello_world.appmap.json'))
    assert len(appmap_json) == 1 # sanity check
    generated_appmap = normalize_appmap(appmap_json[0].read_text())

    appmap_json = testdir.expected / (f'{testdir.test_type}.appmap.json')
    expected_appmap = json.loads(appmap_json.read_text())

    assert generated_appmap == expected_appmap
