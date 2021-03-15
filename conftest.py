import os.path
import sys

import pytest

collect_ignore = [os.path.join('appmap', 'test', 'data')]
pytest_plugins = ['pytester']


@pytest.fixture
def data_dir(pytestconfig):
    dir = str(os.path.join(str(pytestconfig.rootpath),
                           'appmap', 'test', 'data'))
    added = False
    if dir not in sys.path:
        sys.path.append(dir)
        added = True

    yield dir

    if added:
        sys.path.remove(dir)


@pytest.fixture
def appmap_enabled(monkeypatch):
    monkeypatch.setenv("APPMAP", "true")
    monkeypatch.setenv("APPMAP_LOG_LEVEL", "debug")

    yield monkeypatch
