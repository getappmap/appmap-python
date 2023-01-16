import unittest
from contextlib import contextmanager

from _appmap import testing_framework
from _appmap.env import Env
from _appmap.utils import get_function_location
from appmap import wrapt

logger = Env.current.getLogger(__name__)


def setup_unittest():
    session = testing_framework.session("unittest", "tests")

    def get_test_location(cls, method_name):

        fn = getattr(cls, method_name)
        return get_function_location(fn)

    # unittest.case._Outcome.testPartExecutor is used by all supported
    # versions of unittest to run test cases. `isTest` will be True when
    # the part is the actual test method, False when it's setUp or
    # teardown.
    @wrapt.patch_function_wrapper("unittest.case", "_Outcome.testPartExecutor")
    @contextmanager
    def testPartExecutor(wrapped, _, args, kwargs):
        def _args(test_case, *_, isTest=False, **__):
            return (test_case, isTest)

        test_case, is_test = _args(*args, **kwargs)
        already_recording = getattr(test_case, "_appmap_pytest_recording", None)
        # fmt: off
        if (
            (not is_test)
            or isinstance(test_case, unittest.case._SubTest) # pylint: disable=protected-access
            or already_recording
        ):
        # fmt: on
            with wrapped(*args, **kwargs):
                yield
            return

        method_name = test_case.id().split(".")[-1]
        location = get_test_location(test_case.__class__, method_name)
        with session.record(
            test_case.__class__, method_name, location=location
        ) as metadata:
            if metadata:
                with wrapped(
                    *args, **kwargs
                ), testing_framework.collect_result_metadata(metadata):
                    yield
            else:
                # session.record may return None
                yield


if not Env.current.is_appmap_repo and Env.current.enables("unittest"):
    logger.debug("Test recording is enabled (unittest)")
    setup_unittest()
