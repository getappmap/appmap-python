from _appmap import noappmap, testing_framework, wrapt
from _appmap.env import Env
from _appmap.utils import get_function_location

_session = testing_framework.session("unittest", "tests")


def _get_test_location(cls, method_name):
    fn = getattr(cls, method_name)
    return get_function_location(fn)

# We need to disable request recording in TestCase._callSetUp. This prevents creation of a request
# recording calls when requests made inside setUp method.
#
# This edge case can be observed in this test in django project:
#   $ APPMAP=TRUE ./runtests.py auth_tests.test_views.ChangelistTests.test_user_change_email
#   (ChangelistTests.setUp makes a request)
@wrapt.patch_function_wrapper("unittest.case", "TestCase._callSetUp")
def callSetUp(wrapped, _, args, kwargs):
    with Env.current.disabled("requests"):
        wrapped(*args, **kwargs)

@wrapt.patch_function_wrapper("unittest.case", "TestCase._callTestMethod")
def callTestMethod(wrapped, test_case, _, kwargs):
    already_recording = getattr(test_case, "_appmap_pytest_recording", None)

    test_method_name = test_case._testMethodName  # pylint: disable=protected-access
    test_method = getattr(test_case, test_method_name)
    if already_recording or noappmap.disables(test_method, test_case.__class__):
        wrapped(test_method, **kwargs)
        return

    method_name = test_case.id().split(".")[-1]
    location = _get_test_location(test_case.__class__, method_name)
    testing_framework.disable_test_case(test_method)
    with _session.record(test_case.__class__, method_name, location=location) as metadata:
        if metadata:
            with testing_framework.collect_result_metadata(metadata):
                wrapped(test_method, **kwargs)
