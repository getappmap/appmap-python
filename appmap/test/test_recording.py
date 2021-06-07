"""Test recording functions called and defined in various ways."""
# pylint: disable=missing-function-docstring

import json
import os
import sys

import pytest

import appmap

from appmap._implementation.recording import Recorder, wrap_exec_module
from .normalize import normalize_appmap, remove_line_numbers


@pytest.mark.appmap_enabled
@pytest.mark.usefixtures('with_data_dir')
class TestRecordingWhenEnabled:
    def test_recording_works(self, with_data_dir):
        with open(os.path.join(with_data_dir, 'expected.appmap.json')) as f:
            expected_appmap = json.load(f)

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
            ExampleClass.call_yaml()

        generated_appmap = normalize_appmap(appmap.generation.dump(r))
        assert remove_line_numbers(generated_appmap) == expected_appmap

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

    def test_recording_shallow(self):
        from example_class import ExampleClass  # pylint: disable=import-error
        rec = appmap.Recording()
        with rec:
            ExampleClass.class_method()
            ExampleClass().instance_method()
            ExampleClass.class_method()
            ExampleClass().instance_method()

        assert len(rec.events) == 8

    def test_recording_wrapped(self):
        from example_class import ExampleClass  # pylint: disable=import-error
        rec = appmap.Recording()
        with rec:
            ExampleClass.wrapped_class_method()
            ExampleClass.wrapped_static_method()
            ExampleClass().wrapped_instance_method()

        assert len(rec.events) == 6

        evt = rec.events[-2]
        assert evt.event == 'call'
        assert evt.method_id == 'wrapped_instance_method'

    def test_cant_start_twice(self):
        rec = appmap.Recording()
        rec.start()
        with pytest.raises(RuntimeError):
            rec.start()

def test_exec_module_protection(monkeypatch):
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


@pytest.mark.appmap_enabled
@pytest.mark.usefixtures('with_data_dir')
def test_static_cached(events):
    from example_class import ExampleClass  # pylint: disable=import-outside-toplevel
    ExampleClass.static_cached(42)
    assert events[0].parameters[0].items() >= {
        'name': 'value',
        'class': 'builtins.int',
        'value': '42'
    }.items()
