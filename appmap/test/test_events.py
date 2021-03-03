"""
Test event functionality
"""
from functools import partial
from queue import Queue
from threading import Thread

import pytest

import appmap
import appmap._implementation
from appmap._implementation.event import _EventIds

from .appmap_test_base import AppMapTestBase


class TestEvents(AppMapTestBase):
    def test_per_thread_id(self):
        """ thread ids should be constant for a  thread """
        assert _EventIds.get_thread_id() == _EventIds.get_thread_id()

    def test_thread_ids(self):
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

    @pytest.mark.usefixtures('appmap_enabled')
    def test_recursion_protection(self):
        r = appmap.Recording()
        with r:
            from example_class import ExampleClass  # pylint: disable=import-error
            ExampleClass().instance_method()

        # If we get here, recursion protection for rendering the receiver
        # is working
        assert True
