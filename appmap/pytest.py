import pytest

import appmap
import appmap.wrapt as wrapt
from appmap._implementation import testing_framework
from appmap._implementation.detect_enabled import DetectEnabled


class recorded_testcase:
    def __init__(self, item):
        self.item = item

    @wrapt.decorator
    def __call__(self, wrapped, _, args, kwargs):
        item = self.item
        with item.session.appmap.record(
            item.cls, item.name, method_id=item.originalname, location=item.location
        ) as metadata:
            with testing_framework.collect_result_metadata(metadata):
                return wrapped(*args, **kwargs)


if not DetectEnabled.is_appmap_repo() and DetectEnabled.should_enable("pytest"):

    @pytest.hookimpl
    def pytest_sessionstart(session):
        session.appmap = testing_framework.session(
            name="pytest", recorder_type="tests", version=pytest.__version__
        )

    @pytest.hookimpl
    def pytest_runtest_call(item):
        # The presence of a `_testcase` attribute on an item indicates
        # that it was created from a `unittest.TestCase`. An item
        # created from a TestCase has an `obj` attribute, assigned
        # during in setup, which holds the actual test
        # function. Wrapping that function will capture the recording
        # we want. `obj` gets unset during teardown, so there's no
        # chance of rewrapping it.
        #
        # However, depending on the user's configuration, `item.obj`
        # may have been already instrumented for recording. In this
        # case, it will be a `wrapt` class, rather than just a
        # function. This is fine: the decorator we apply here will be
        # called first, starting the recording. Next, the
        # instrumentation decorator will be called, recording the
        # `call` event. Finally, the original function will be called,
        # running the test case. (This nesting of function calls is
        # verified by the expected appmap in the test for a unittest
        # TestCase run by pytest.)
        if hasattr(item, "_testcase"):
            setattr(
                item._testcase, "_appmap_pytest_recording", True
            )  # pylint: disable=protected-access
            item.obj = recorded_testcase(item)(item.obj)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_pyfunc_call(pyfuncitem):
        # There definitely shouldn't be a `_testcase` attribute on a
        # pytest test.
        assert not hasattr(pyfuncitem, "_testcase")

        with pyfuncitem.session.appmap.record(
            pyfuncitem.cls,
            pyfuncitem.name,
            method_id=pyfuncitem.originalname,
            location=pyfuncitem.location,
        ) as metadata:
            result = yield
            try:
                with testing_framework.collect_result_metadata(metadata):
                    result.get_result()
            except:  # pylint: disable=bare-except
                pass  # exception got recorded in metadata
