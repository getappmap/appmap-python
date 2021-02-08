"""
Test event functionality
"""
import inspect
import os
import sys
from functools import partial, wraps
from queue import Queue
from threading import Thread

import pytest

from .appmap_test_base import AppMapTestBase
from .helpers import FIXTURE_DIR

import appmap
import appmap._implementation
from appmap._implementation.event import _EventIds, CallEvent
from appmap._implementation.utils import FnType


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


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'appmap.yml'),
    os.path.join(FIXTURE_DIR, 'example_class.py'),
)
def test_recursion_protection(monkeypatch, datafiles):
    monkeypatch.setenv("APPMAP", "true")
    monkeypatch.setenv("APPMAP_CONFIG", os.path.join(datafiles, 'appmap.yml'))
    monkeypatch.setenv("APPMAP_LOG_LEVEL", "debug")

    sys.path.append(str(datafiles))
    appmap._implementation.initialize()  # pylint: disable=protected-access
    r = appmap.Recording()
    with r:
        from example_class import ExampleClass  # pylint: disable=import-error
        ExampleClass().instance_method()

    # If we get here, recursion protection for rendering the receiver
    # is working
    assert True


@pytest.fixture
def provide_datafiles(datafiles):
    sys.path.append(str(datafiles))


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'params.py'),
)
@pytest.mark.usefixtures('provide_datafiles')
class TestParameters(AppMapTestBase):
    def prepare(self, fn, fntype):
        if fntype in FnType.STATIC | FnType.CLASS:
            fn = fn.__func__
        make_call_event = CallEvent.make(fn, fntype)
        make_params = CallEvent.make_params(CallEvent.make_param_defs(fn))

        @wraps(fn)
        def wrapped_fn(*args, **kwargs):
            return make_call_event(parameters=make_params(args, kwargs))
        return wrapped_fn

    def check_result(self, result, expected, present):
        assert result
        for k in expected.keys():
            assert result[k] == expected[k]
        for k in present:
            assert result[k]

    @pytest.mark.parametrize('fnname,call,value,count,expected,present', [
        (
            'zero', 'C().zero()', 'evt.receiver', 0,
            {
                'name': 'self',
                'class': 'params.C',
                'kind': 'req'
            },
            {'value'}
        ),
        (
            'one', 'C().one("world")', 'evt.parameters[0]', 1,
            {
                'name': 'p',
                'class': 'builtins.str',
                'kind': 'req',
                'value': 'world'
            },
            set()
        ),
        (
            'static', 'C.static("static")', 'evt.parameters[0]', 1,
            {
                'name': 'p',
                'class': 'builtins.str',
                'kind': 'req',
                'value': 'static'
            },
            set()
        ),
        (
            'cls', 'C.cls("cls")', 'evt.receiver', 1,
            {
                'name': 'cls',
                'class': 'builtins.type',
                'kind': 'req',
                'value': "<class 'params.C'>"
            },
            set()
        ),
        (
            'cls', 'C.cls("cls")', 'evt.parameters[0]', 1,
            {
                'name': 'p',
                'class': 'builtins.str',
                'kind': 'req',
                'value': 'cls'
            },
            set()
        )
    ])
    def test_parameters(self, fnname, call, value, count, expected, present):
        from params import C
        fn = inspect.getattr_static(C, fnname)
        fntype = FnType.classify(fn)
        wrapped = self.prepare(fn, fntype)
        if fntype & FnType.STATIC:
            wrapped = staticmethod(wrapped)
        elif fntype & FnType.CLASS:
            wrapped = classmethod(wrapped)
        setattr(C, fnname, wrapped)

        evt = eval(call)  # noqa: F841
        assert len(evt.parameters) == count
        self.check_result(eval(value),
                          expected,
                          present | {'object_id'}  # all values have object_id
                          )

    def test_static_no_receiver(self):
        from params import C
        fn = inspect.getattr_static(C, 'static')
        setattr(C, 'static', self.prepare(fn, FnType.STATIC))
        evt = C.static('param')
        assert not getattr(evt, 'receiver', None)
