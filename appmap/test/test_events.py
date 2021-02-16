"""
Test event functionality
"""
import os
import sys
from functools import partial
from queue import Queue
from threading import Thread

import appmap
import appmap._implementation
from appmap._implementation.event import _EventIds


def test_per_thread_id():
    """ thread ids should be constant for a  thread """
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


def test_recursion_protection(data_dir, monkeypatch):
    monkeypatch.setenv("APPMAP", "true")
    monkeypatch.setenv("APPMAP_CONFIG", os.path.join(data_dir, 'appmap.yml'))
    monkeypatch.setenv("APPMAP_LOG_LEVEL", "debug")

    sys.path.append(data_dir)
    appmap._implementation.initialize()  # pylint: disable=protected-access
    r = appmap.Recording()
    with r:
        from example_class import ExampleClass  # pylint: disable=import-error
        ExampleClass().instance_method()

    # If we get here, recursion protection for rendering the receiver
    # is working
    assert True
