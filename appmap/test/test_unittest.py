from pathlib import Path
import json
import sys

from .appmap_test_base import AppMapTestBase


class TestUnitTest(AppMapTestBase):
    def test_basic_integration(self, data_dir, testdir):
        testdir.copy_example('unittest')
        testdir.monkeypatch.setenv('APPMAP', 'true')

        testdir.run(sys.executable, '-m', 'appmap.unittest', '-vv')

        appmap_json = Path(str(testdir.tmpdir)) / 'tmp/appmap/unittest/simple_test_simple_UnitTestTest_test_hello_world.appmap.json'
        generated_appmap = self.normalize_appmap(appmap_json.read_text())

        appmap_json = Path(data_dir) / 'unittest/expected.appmap.json'
        expected_appmap = json.loads(appmap_json.read_text())

        assert generated_appmap == expected_appmap

    def test_unittest_cases(self, testdir):
        testdir.copy_example('unittest')
        testdir.monkeypatch.setenv('APPMAP', 'true')

        result = testdir.runpytest('-svv')
        result.assert_outcomes(passed=2)

        # unittest cases ran by pytest should get recorded as pytest tests
        path = Path(str(testdir.tmpdir))
        assert len(list(path.glob('tmp/appmap/pytest/*'))) == 2
        assert len(list(path.glob('tmp/appmap/unittest/*'))) == 0
