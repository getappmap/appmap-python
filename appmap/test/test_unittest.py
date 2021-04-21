from pathlib import Path
import sys

import json

from .normalize import normalize_appmap

def setup_env(testdir):
    testdir.monkeypatch.setenv('APPMAP', 'true')

    # The init subdirectory contains a sitecustomize.py file that
    # imports the appmap module. This simulates the way a real
    # installation works, performing the same function as the the
    # appmap.pth file that gets put in site-packages.
    testdir.monkeypatch.setenv('PYTHONPATH', 'init')

def test_appmap_unittest_runner(data_dir, testdir):
    testdir.copy_example('unittest')
    setup_env(testdir)
    testdir.run(sys.executable, '-m', 'appmap.unittest', '-vv')

    verify_expected_appmap(data_dir, testdir, 'unittest')

def test_pytest_runner(data_dir, testdir):
    testdir.copy_example('unittest')
    setup_env(testdir)

    result = testdir.runpytest('-svv', '--setup-show')
    result.assert_outcomes(passed=2)

    # unittest cases run by pytest should get recorded as pytest
    # tests
    path = Path(str(testdir.tmpdir))
    assert len(list(path.glob('tmp/appmap/pytest/*'))) == 2
    assert len(list(path.glob('tmp/appmap/unittest/*'))) == 0

    verify_expected_appmap(data_dir, testdir, 'pytest')

def test_unittest_runner(data_dir, testdir):
    testdir.copy_example('unittest')
    setup_env(testdir)

    testdir.run(sys.executable, '-m', 'unittest', '-vv')

    verify_expected_appmap(data_dir, testdir, 'unittest')

def verify_expected_appmap(data_dir, testdir, test_type):
    out_dir = output_dir(testdir, test_type)
    appmap_json = out_dir / 'simple_test_simple_UnitTestTest_test_hello_world.appmap.json'
    generated_appmap = normalize_appmap(appmap_json.read_text())

    appmap_json = Path(data_dir) / ('unittest/expected.%s.appmap.json' % test_type)
    expected_appmap = json.loads(appmap_json.read_text())

    assert generated_appmap == expected_appmap

def output_dir(testdir, test_type):
    return Path(str(testdir)) / 'tmp/appmap' / test_type
