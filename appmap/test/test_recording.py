"""Test recording functions called and defined in various ways."""
# pylint: disable=missing-function-docstring

import json
import os
from threading import Thread

import pytest

import appmap
from appmap._implementation.event import Event
from appmap._implementation.recorder import Recorder, ThreadRecorder

from .normalize import normalize_appmap, remove_line_numbers


@pytest.mark.appmap_enabled
@pytest.mark.usefixtures("with_data_dir")
class TestRecordingWhenEnabled:
    def test_recording_works(self, with_data_dir):
        expected_path = os.path.join(with_data_dir, "expected.appmap.json")
        with open(expected_path) as f:
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
        assert (
            remove_line_numbers(generated_appmap) == expected_appmap
        ), f"expected path {expected_path}"

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

        rec = appmap.Recording()
        with rec:
            f1 = deepcopy(modfunc)
            f1()

        evt = rec.events[-2]
        assert evt.event == "call"
        assert evt.method_id == "modfunc"


@pytest.mark.appmap_enabled
@pytest.mark.usefixtures("with_data_dir")
def test_static_cached(events):
    from example_class import (  # pyright: ignore[reportMissingImports] pylint: disable=import-outside-toplevel,import-error
        ExampleClass,
    )

    ExampleClass.static_cached(42)
    assert (
        events[0].parameters[0].items()
        >= {"name": "value", "class": "builtins.int", "value": "42"}.items()
    )


class TestRecordingPerThread:
    def test_default_thread(self):
        rec = Recorder.get_current()
        evt = Event({})
        rec.add_event(evt)
        actual = rec.events
        assert len(actual) == 1
        assert actual[0].id == 1

    def test_explicit_thread(self):
        thread_count = 100
        rec_default = Recorder.get_current()

        recorders = {}

        def add_event(name):
            r = ThreadRecorder()
            Recorder.set_current(r)
            r.add_event(Event({"name": name}))
            recorders[name] = r

        threads = [
            Thread(target=add_event, args=(f"thread{i}",)) for i in range(thread_count)
        ]
        for _, t in enumerate(threads):
            t.start()
        for _, t in enumerate(threads):
            t.join()

        # Each thread should have gotten a recorder
        assert len(recorders) == thread_count

        # All events should show up in the global recorder
        default_events = rec_default.events
        assert len(default_events) == thread_count

        # Each event should be added as the first event to the correct recorder
        for n in range(thread_count):
            events = recorders[f"thread{n}"].events
            assert len(events) == 1
            assert events[0].event["name"] == f"thread{n}"
