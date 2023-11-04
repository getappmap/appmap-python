import sys
import unittest
from contextlib import contextmanager

from _appmap import noappmap, testing_framework, wrapt
from _appmap.utils import get_function_location

_session = testing_framework.session("unittest", "tests")


def _get_test_location(cls, method_name):
    fn = getattr(cls, method_name)
    return get_function_location(fn)


if sys.version_info[1] < 8:
    # Prior to 3.8, unittest called the test case's test method directly, which left us without an
    # opportunity to hook it. So, instead, instrument unittest.case._Outcome.testPartExecutor, a
    # method used to run test cases. `isTest` will be True when the part is the actual test method,
    # False when it's setUp or teardown.
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
        location = _get_test_location(test_case.__class__, method_name)
        with _session.record(
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

else:
    # As of 3.8, unittest.case.TestCase now calls the test's method indirectly, through
    # TestCase._callTestMethod. Hook that to manage a recording session.
    @wrapt.patch_function_wrapper("unittest.case", "TestCase._callTestMethod")
    def callTestMethod(wrapped, test_case, args, kwargs):
        already_recording = getattr(test_case, "_appmap_pytest_recording", None)
        test_method = getattr(test_case, test_case._testMethodName)
        if already_recording or noappmap.disables(test_method, test_case.__class__):
            wrapped(*args, **kwargs)
            return

        method_name = test_case.id().split(".")[-1]
        location = _get_test_location(test_case.__class__, method_name)
        with _session.record(test_case.__class__, method_name, location=location) as metadata:
            if metadata:
                with testing_framework.collect_result_metadata(metadata):
                    wrapped(*args, **kwargs)
