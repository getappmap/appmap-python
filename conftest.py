import os.path

import pytest

collect_ignore = [os.path.join('appmap', 'test', 'data')]
pytest_plugins = ['pytester']

@pytest.fixture
def data_dir(pytestconfig):
    yield str(os.path.join(pytestconfig.rootpath,
                           'appmap', 'test', 'data'))
