import os
import os.path

import json

from .appmap_test_base import AppMapTestBase


class TestPytest(AppMapTestBase):
    def test_basic_integration(self, data_dir, testdir):
        testdir.copy_example('pytest')
        testdir.monkeypatch.setenv('APPMAP', 'true')

        result = testdir.runpytest('-svv', '-k', 'test_hello_world')
        result.assert_outcomes(passed=1)

        appmap_json = os.path.join(
            str(testdir),
            'tmp', 'appmap', 'pytest', 'test_hello_world.appmap.json'
        )
        with open(appmap_json) as appmap:
            generated_appmap = self.normalize_appmap(appmap.read())

        appmap_json = os.path.join(data_dir, 'pytest', 'expected.appmap.json')
        with open(appmap_json) as f:
            expected_appmap = json.load(f)

        assert generated_appmap == expected_appmap
