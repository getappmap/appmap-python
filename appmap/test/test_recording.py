"""Test recording context manager"""
import json
import os
import platform
import sys

import pytest

from .helpers import FIXTURE_DIR
from .appmap_test_base import AppMapTestBase


class TestRecording(AppMapTestBase):
    @pytest.mark.datafiles(
        os.path.join(FIXTURE_DIR, 'appmap.yml'),
        os.path.join(FIXTURE_DIR, 'example_class.py'),
        os.path.join(FIXTURE_DIR, 'expected.appmap.json')
    )
    def test_recording_works(self, datafiles, monkeypatch):
        with open(os.path.join(str(datafiles), 'expected.appmap.json')) as f:
            expected_appmap = json.load(f)

        # Setting these outside the definition of expected_appmap makes it
        # easier to update when the expected appmap changes
        py_impl = platform.python_implementation()
        py_version = platform.python_version()
        expected_appmap['metadata']['language']['engine'] = py_impl
        expected_appmap['metadata']['language']['version'] = py_version

        sys.path.append(str(datafiles))

        monkeypatch.setenv("APPMAP", "true")
        monkeypatch.setenv("APPMAP_CONFIG",
                           os.path.join(str(datafiles), 'appmap.yml'))
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
