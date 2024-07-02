import os

import pytest


def test_hello_world():
    from simple import Simple

    os.chdir("/tmp")
    assert Simple().hello_world() == "Hello world!"

    assert len(Simple().show_numpy_dict()) > 0


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
