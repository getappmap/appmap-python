"""Test recording functions called and defined in various ways."""
# pylint: disable=missing-function-docstring

import json
import os
import sys

import pytest

import appmap
from appmap._implementation.event import Event
from appmap._implementation.recording import Recorder, wrap_exec_module

from .normalize import normalize_appmap, remove_line_numbers


@pytest.mark.appmap_enabled
@pytest.mark.usefixtures("with_data_dir")
class TestRecordingWhenEnabled:
    def test_recording_works(self, with_data_dir):
        with open(os.path.join(with_data_dir, "expected.appmap.json")) as f:
            expected_appmap = json.load(f)

        r = appmap.Recording()
        with r:
            from example_class import (  # pyright: ignore[reportMissingImports] pylint: disable=import-error
                ExampleClass,
            )

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
        from example_class import (  # pyright: ignore[reportMissingImports] pylint: disable=import-error
            ExampleClass,
        )

        with appmap.Recording():
            ExampleClass.static_method()

        # fresh recording shouldn't contain previous traces
        rec = appmap.Recording()
        with rec:
            ExampleClass.class_method()

        assert rec.events[0].method_id == "class_method"

        # but it can be added to
        with rec:
            ExampleClass().instance_method()

        assert rec.events[2].method_id == "instance_method"

    def test_recording_shallow(self):
        from example_class import (  # pyright: ignore[reportMissingImports] pylint: disable=import-error
            ExampleClass,
        )

        rec = appmap.Recording()
        with rec:
            ExampleClass.class_method()
            ExampleClass().instance_method()
            ExampleClass.class_method()
            ExampleClass().instance_method()

        assert len(rec.events) == 8

    def test_recording_wrapped(self):
        from example_class import (  # pyright: ignore[reportMissingImports] pylint: disable=import-error
            ExampleClass,
        )

        rec = appmap.Recording()
        with rec:
            ExampleClass.wrapped_class_method()
            ExampleClass.wrapped_static_method()
            ExampleClass().wrapped_instance_method()

        assert len(rec.events) == 6

        evt = rec.events[-2]
        assert evt.event == "call"
        assert evt.method_id == "wrapped_instance_method"

    def test_cant_start_twice(self):
        rec = appmap.Recording()
        rec.start()
        with pytest.raises(RuntimeError):
            rec.start()

    def test_can_deepcopy_function(self):
        from copy import deepcopy

        from example_class import (  # pyright: ignore[reportMissingImports] pylint: disable=import-error
            modfunc,
        )

        from appmap.wrapt import FunctionWrapper

        rec = appmap.Recording()
        with rec:
            f1 = deepcopy(modfunc)
            f1()

        evt = rec.events[-2]
        assert evt.event == "call"
        assert evt.method_id == "modfunc"


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

    monkeypatch.setattr(Recorder, "do_import", do_import)
    f = exec_module
    for _ in range(sys.getrecursionlimit()):
        f = wrap_exec_module(f)

    f()
    assert True


@pytest.mark.appmap_enabled
@pytest.mark.usefixtures("with_data_dir")
def test_static_cached(events):
    from example_class import (  # pyright: ignore[reportMissingImports] pylint: disable=import-outside-toplevel
        ExampleClass,
    )

    ExampleClass.static_cached(42)
    assert (
        events[0].parameters[0].items()
        >= {"name": "value", "class": "builtins.int", "value": "42"}.items()
    )


class TestRecordingPerThread:
    def test_default_thread(self):
        rec = Recorder()
        evt = Event({id: 1})
        rec.add_event(evt)
        actual = rec.events
        assert len(actual) == 1

    def test_explicit_thread(self):
        rec_default = Recorder()
        rec2 = Recorder(2)
        rec3 = Recorder(3)
        evt2 = Event({})
        evt2.thread_id = 2
        evt3 = Event({})
        evt3.thread_id = 3

        # Add them to the default recorder, since that's what the instrumented code does.
        rec_default.add_event(evt2)
        rec_default.add_event(evt3)

        default_events = rec_default.events
        assert len(default_events) == 2

        rec2_events = rec2.events
        assert len(rec2_events) == 1
        assert rec2_events[0].thread_id == 2

        rec3_events = rec3.events
        assert len(rec3_events) == 1
        assert rec3_events[0].thread_id == 3
