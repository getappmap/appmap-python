from glob import glob
from pathlib import Path
import sys

import json
import pytest

from .normalize import normalize_appmap

@pytest.fixture(name='runner_testdir')
def fixture_runner_testdir(request, testdir):
    marker = request.node.get_closest_marker('example_dir')
    testdir.example_dir = 'unittest' if marker is None else marker.args[0]
    testdir.copy_example(testdir.example_dir)
    testdir.monkeypatch.setenv('APPMAP', 'true')

    # The init subdirectory contains a sitecustomize.py file that
    # imports the appmap module. This simulates the way a real
    # installation works, performing the same function as the the
    # appmap.pth file that gets put in site-packages.
    testdir.monkeypatch.setenv('PYTHONPATH', 'init')
    return testdir

def verify_expected_appmap(data_dir, testdir, test_type):
    out_dir = Path(str(testdir)) / 'tmp/appmap' / test_type
    appmap_json = glob(str(out_dir / '*_test_hello_world.appmap.json'), recursive=True)
    assert len(appmap_json) == 1 # sanity check
    generated_appmap = normalize_appmap(Path(appmap_json[0]).read_text())

    appmap_json = Path(data_dir) / testdir.example_dir / ('expected.%s.appmap.json' % test_type)
    expected_appmap = json.loads(appmap_json.read_text())

    assert generated_appmap == expected_appmap


def test_appmap_unittest_runner(data_dir, runner_testdir):
    runner_testdir.run(sys.executable, '-m', 'appmap.unittest', '-vv')

    verify_expected_appmap(data_dir, runner_testdir, 'unittest')

def test_pytest_runner(data_dir, runner_testdir):
    result = runner_testdir.runpytest('-svv')
    result.assert_outcomes(passed=2)

    # unittest cases run by pytest should get recorded as pytest
    # tests
    path = Path(str(runner_testdir.tmpdir))
    assert len(list(path.glob('tmp/appmap/pytest/*'))) == 2
    assert len(list(path.glob('tmp/appmap/unittest/*'))) == 0

    verify_expected_appmap(data_dir, runner_testdir, 'pytest')

def test_unittest_runner(data_dir, runner_testdir):
    runner_testdir.run(sys.executable, '-m', 'unittest', '-vv')

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
