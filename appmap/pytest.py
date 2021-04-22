import pytest

import appmap
import appmap.wrapt as wrapt

from appmap._implementation import testing_framework

class recorded_testcase:
    def __init__(self, item):
        self.item = item

    @wrapt.decorator
    def __call__(self, wrapped, _, args, kwargs):
        item = self.item
        with item.session.appmap.record(
                item.cls,
                item.name,
                method_id=item.originalname,
                location=item.location):
            return wrapped(*args, **kwargs)


if appmap.enabled():
    @pytest.hookimpl
    def pytest_sessionstart(session):
        session.appmap = testing_framework.session(name='pytest', version=pytest.__version__)

    @pytest.hookimpl
    def pytest_runtest_call(item):
        # The presence of a `_testcase` attribute on an item indicates
        # that it was created from a `unittest.TestCase`. An item
        # created from a TestCase has an `_obj` attribute, assigned
        # during in setup, which holds the actual test
        # function. Wrapping that function will capture the recording
        # we want. `_obj` gets unset during teardown, so there's no
        # chance of rewrapping it.
        #
        # However, depending on the user's configuration, `item._obj`
        # may have been already instrumented for recording. In this
        # case, it will be a `wrapt` class, rather than just a
        # function. This is fine: the decorator we apply here will be
        # called first, starting the recording. Next, the
        # instrumentation decorator will be called, recording the
        # `call` event. Finally, the original function will be called,
        # running the test case. (This nesting of function calls is
        # verified by the expected appmap in the test for a unittest
        # TestCase run by pytest.)
        if hasattr(item, '_testcase'):
            item.obj = recorded_testcase(item)(item.obj)

    # Note: don't use pytest_runtest_call as this will catch unittest tests.
    # They are recorded separately by appmap.unittest instead.
    @pytest.hookimpl(hookwrapper=True)
    def pytest_pyfunc_call(pyfuncitem):
        with pyfuncitem.session.appmap.record(
                pyfuncitem.cls,
                pyfuncitem.name,
                method_id=pyfuncitem.originalname,
                location=pyfuncitem.location):
            yield
