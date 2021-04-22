from pathlib import Path
import json
import sys

from .normalize import normalize_appmap


def test_basic_integration(data_dir, testdir):
    testdir.copy_example('unittest')
    testdir.monkeypatch.setenv('APPMAP', 'true')

    testdir.run(sys.executable, '-m', 'appmap.unittest', '-vv')

    verify_expected_appmap(data_dir, testdir, 'unittest')

def test_unittest_cases(data_dir, testdir):
    testdir.copy_example('unittest')
    testdir.monkeypatch.setenv('APPMAP', 'true')

    result = testdir.runpytest('-svv')
    result.assert_outcomes(passed=2)

    # unittest cases run by pytest should get recorded as pytest
    # tests
    path = Path(str(testdir.tmpdir))
    assert len(list(path.glob('tmp/appmap/pytest/*'))) == 2
    assert len(list(path.glob('tmp/appmap/unittest/*'))) == 0

    verify_expected_appmap(data_dir, testdir, 'pytest')

def verify_expected_appmap(data_dir, testdir, test_type):
    out_dir = output_dir(testdir, test_type)
    appmap_json = out_dir / 'simple_test_simple_UnitTestTest_test_hello_world.appmap.json'
    generated_appmap = normalize_appmap(appmap_json.read_text())

    appmap_json = Path(data_dir) / ('unittest/expected.%s.appmap.json' % test_type)
    expected_appmap = json.loads(appmap_json.read_text())

    assert generated_appmap == expected_appmap

def output_dir(testdir, test_type):
    return Path(str(testdir.tmpdir)) / 'tmp/appmap' / test_type
