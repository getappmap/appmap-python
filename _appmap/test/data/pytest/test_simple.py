import os

import pytest


def test_hello_world():
    import simple

    os.chdir("/tmp")
    s = simple.Simple()
    assert s.hello_world() == "Hello world!"

    h = s.get_json_unserializable()
    assert len(h) > 0


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
