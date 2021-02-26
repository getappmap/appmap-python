from pathlib import Path
import json
import sys

from .appmap_test_base import AppMapTestBase


class TestUnitTest(AppMapTestBase):
    def test_basic_integration(self, data_dir, testdir):
        testdir.copy_example('pytest')
        testdir.monkeypatch.setenv('APPMAP', 'true')

        testdir.run(sys.executable, '-m', 'appmap.unittest')

        appmap_json = Path(str(testdir.tmpdir)) / 'tmp/appmap/unittest/test_simple_UnitTestTest_test_hello_unitworld.appmap.json'
        generated_appmap = self.normalize_appmap(appmap_json.read_text())

        appmap_json = Path(data_dir) / 'pytest/expected.unittest.appmap.json'
        expected_appmap = json.loads(appmap_json.read_text())

        assert generated_appmap == expected_appmap
