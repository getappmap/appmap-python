import sys

import pytest


@pytest.fixture
def params(mocker):
    """
    Manage the lifecycle of the params module.  Import it before users
    of this fixture, unload it after.  This ensures that each test
    sees a pristine version of the classes it contains.
    """
    from params import C  # pylint: disable=import-error
    ret = mocker.Mock()
    ret.C = C
    yield ret
    del sys.modules['params']
