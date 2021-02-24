import pytest

from appmap._implementation import testing_framework


@pytest.hookimpl
def pytest_runtestloop(session):
    session.appmap = testing_framework.session(name='pytest', version=pytest.__version__)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    with item.session.appmap.record(item.cls, item.name, method_id=item.originalname):
        yield
