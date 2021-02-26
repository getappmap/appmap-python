"""Test recording context manager"""
import json
import os
import sys

from appmap._implementation.recording import Recorder, wrap_exec_module
from .appmap_test_base import AppMapTestBase


class TestRecording(AppMapTestBase):
    def test_recording_works(self, data_dir, monkeypatch):
        with open(os.path.join(data_dir, 'expected.appmap.json')) as f:
            expected_appmap = json.load(f)

        sys.path.append(data_dir)

        monkeypatch.setenv("APPMAP", "true")
        monkeypatch.setenv("APPMAP_CONFIG",
                           os.path.join(data_dir, 'appmap.yml'))

        import appmap
        # Reinitialize to pick up the environment variables just set
        appmap._implementation.initialize()  # pylint: disable=protected-access
        r = appmap.Recording()
        with r:
            from example_class import ExampleClass  # pylint: disable=import-error
            ExampleClass.static_method()
            ExampleClass.class_method()
            ExampleClass().instance_method()
            ExampleClass.what_time_is_it()
            try:
                ExampleClass().test_exception()
            except:  # pylint: disable=bare-except  # noqa: E722
                pass

        generated_appmap = self.normalize_appmap(appmap.generation.dump(r))

        assert generated_appmap == expected_appmap

    def test_exec_module_protection(self, monkeypatch):
        """
        Test that recording.wrap_exec_module properly protects against
        rewrapping a wrapped exec_module function.  Repeatedly wrap
        the function, up to the recursion limit, then call the wrapped
        function.  If wrapping protection is working properly, there
        won't be a problem.  If wrapping protection is broken, this
        test will fail with a RecursionError.
        """

        def exec_module():
            pass

        def do_import(*args, **kwargs):  # pylint: disable=unused-argument
            pass
        monkeypatch.setattr(Recorder, 'do_import', do_import)
        f = exec_module
        for _ in range(sys.getrecursionlimit()):
            f = wrap_exec_module(f)

        f()
        assert True
