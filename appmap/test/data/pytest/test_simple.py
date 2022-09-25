import os

import pytest


def test_hello_world():
    import simple

    os.chdir("/tmp")
    assert simple.Simple().hello_world() == "Hello world!"


def test_status_failed():
    assert False


@pytest.mark.xfail
def test_status_xfailed():
    assert False


@pytest.mark.xfail
def test_status_xsucceeded():
    assert True


def test_status_errored():
    raise RuntimeError("test error")
