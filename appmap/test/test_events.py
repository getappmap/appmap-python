"""
Test event functionality
"""
import re
from functools import partial
from queue import Queue
from threading import Thread

import pytest

import appmap
import appmap._implementation
from appmap._implementation.env import Env
from appmap._implementation.event import _EventIds, describe_value


# pylint: disable=import-error
def test_per_thread_id():
    """thread ids should be constant for a  thread"""
    assert _EventIds.get_thread_id() == _EventIds.get_thread_id()


def test_thread_ids():
    """thread ids should be different per thread"""

    tids = Queue()

    def add_thread_id(q):
        tid = _EventIds.get_thread_id()
        q.put(tid)

    t = partial(add_thread_id, tids)
    threads = [Thread(target=t) for _ in range(5)]
    list(map(Thread.start, threads))
    list(map(Thread.join, threads))

    assert not tids.empty()

    all_tids = [tids.get() for _ in range(tids.qsize())]
    assert len(set(all_tids)) == len(all_tids)  # Should all be unique

def test_describe_value_does_not_call_class():
    """describe_value should not call __class__
    __class__ could be overloaded in the value and
    could cause side effects."""
    class WithOverloadedClass:
        # pylint: disable=missing-class-docstring,too-few-public-methods
        @property
        def __class__(self):
            raise Exception("__class__ called")

    describe_value(WithOverloadedClass())

@pytest.mark.appmap_enabled
@pytest.mark.usefixtures("with_data_dir")
class TestEvents:
    def test_recursion_protection(self):
        r = appmap.Recording()
        with r:
            from example_class import ExampleClass

            ExampleClass().instance_method()

        # If we get here, recursion protection for rendering the receiver
        # is working
        assert True

    def test_when_str_raises(self, mocker):
        r = appmap.Recording()
        with r:
            from example_class import ExampleClass

            param = mocker.Mock()
            param.__str__ = mocker.Mock(side_effect=Exception)
            param.__repr__ = mocker.Mock(return_value="param.__repr__")

            ExampleClass().instance_with_param(param)

        assert len(r.events) > 0
        expected_value = "param.__repr__"
        actual_value = r.events[0].parameters[0]["value"]
        assert expected_value == actual_value

    def test_when_both_raise(self, mocker):
        r = appmap.Recording()
        with r:
            from example_class import ExampleClass

            param = mocker.Mock()
            param.__str__ = mocker.Mock(side_effect=Exception)
            param.__repr__ = mocker.Mock(side_effect=Exception)

            ExampleClass().instance_with_param(param)

        expected_re = r"<.*? object at .*?>"
        actual_value = r.events[0].parameters[0]["value"]
        assert re.fullmatch(expected_re, actual_value)

    def test_when_display_disabled(self, mocker):
        Env.current.set("APPMAP_DISPLAY_PARAMS", "false")
        r = appmap.Recording()
        with r:
            from example_class import ExampleClass

            param = mocker.MagicMock()

            # unittest.mock.MagicMock doesn't mock __repr__ by default
            param.__repr__ = mocker.Mock()

            ExampleClass().instance_with_param(param)

            param.__str__.assert_not_called()

            # The reason MagicMock doesn't mock __repr__ is because it
            # uses it. If APPMAP_DISPLAY_PARAMS is functioning
            # correctly, __repr__ will only be called once, by
            # MagicMock. (If it's broken, we may not get here at all,
            # because the assertion above may fail.)
            param.__repr__.assert_called_once_with()
