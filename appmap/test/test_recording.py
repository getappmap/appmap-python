"""Test recording context manager"""
import json
import os
import sys

from .appmap_test_base import AppMapTestBase


class TestRecording(AppMapTestBase):
    def test_recording_works(self, data_dir, monkeypatch):
        with open(os.path.join(data_dir, 'expected.appmap.json')) as f:
            expected_appmap = json.load(f)

        sys.path.append(data_dir)

        monkeypatch.setenv("APPMAP", "true")
        monkeypatch.setenv("APPMAP_CONFIG",
                           os.path.join(data_dir, 'appmap.yml'))
        monkeypatch.setenv("APPMAP_LOG_LEVEL", "debug")

        import appmap
        # Reinitialize to pick up the environment variables just set
        appmap._implementation.initialize()  # pylint: disable=protected-access
        r = appmap.Recording()
        with r:
            from example_class import ExampleClass  # pylint: disable=import-error
            ExampleClass.static_method()
            ExampleClass.class_method()
            ExampleClass().instance_method()
            try:
                ExampleClass().test_exception()
            except:  # pylint: disable=bare-except  # noqa: E722
                pass

        generated_appmap = self.normalize_appmap(appmap.generation.dump(r))

        assert generated_appmap == expected_appmap
