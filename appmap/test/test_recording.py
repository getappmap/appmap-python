"""Test recording context manager"""
import json
import os
import sys

import pytest

import appmap

from appmap._implementation.recording import Recorder, wrap_exec_module
from .appmap_test_base import AppMapTestBase


class TestRecording(AppMapTestBase):
    @pytest.mark.usefixtures('appmap_enabled')
    def test_recording_works(self, data_dir):
        with open(os.path.join(data_dir, 'expected.appmap.json')) as f:
            expected_appmap = json.load(f)

        import yaml
        appmap.instrument_module(yaml)

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

    @pytest.mark.usefixtures('appmap_enabled')
    def test_recording_clears(self):
        from example_class import ExampleClass  # pylint: disable=import-error

        with appmap.Recording():
            ExampleClass.static_method()

        # fresh recording shouldn't contain previous traces
        rec = appmap.Recording()
        with rec:
            ExampleClass.class_method()

        assert rec.events[0].method_id == 'class_method'

        # but it can be added to
        with rec:
            ExampleClass().instance_method()

        assert rec.events[2].method_id == 'instance_method'

    @pytest.mark.usefixtures('appmap_enabled')
    def test_recording_shallow(self):
        from example_class import ExampleClass  # pylint: disable=import-error
        rec = appmap.Recording()
        with rec:
            ExampleClass.class_method()
            ExampleClass().instance_method()
            ExampleClass.class_method()
            ExampleClass().instance_method()

        assert len(rec.events) == 8

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
