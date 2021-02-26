import pytest

import appmap.unittest
from appmap._implementation import testing_framework


@pytest.hookimpl
def pytest_runtestloop(session):
    # Use the same session for unittest in case there are any unittest.TestCases.
    appmap.unittest.session = session.appmap = testing_framework.session(name='pytest', version=pytest.__version__)


# Note: don't use pytest_runtest_call as this will catch unittest tests.
# They are recorded separately by appmap.unittest instead.
@pytest.hookimpl(hookwrapper=True)
def pytest_pyfunc_call(pyfuncitem):
    with pyfuncitem.session.appmap.record(pyfuncitem.cls, pyfuncitem.name, method_id=pyfuncitem.originalname):
        yield
