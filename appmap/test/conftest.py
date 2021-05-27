import importlib
import pytest
import yaml

import appmap._implementation
from appmap._implementation.env import Env
from appmap._implementation.recording import Recorder

def _data_dir(pytestconfig):
    return pytestconfig.rootpath / 'appmap' / 'test' / 'data'

@pytest.fixture(name='data_dir')
def fixture_data_dir(pytestconfig):
    return _data_dir(pytestconfig)

@pytest.fixture(name='with_data_dir')
def fixture_with_data_dir(data_dir, monkeypatch):
    monkeypatch.syspath_prepend(data_dir)
    return data_dir

@pytest.fixture
def events():
    rec = Recorder()
    rec.clear()
    rec.enabled = True
    yield rec.events
    rec.enabled = False
    rec.clear()

@pytest.hookimpl
def pytest_runtest_setup(item):
    mark = item.get_closest_marker('appmap_enabled')
    env = {}
    if mark:
        appmap_yml = mark.kwargs.get('config', 'appmap.yml')
        d = _data_dir(item.config)
        config = d / appmap_yml
        Env.current.set('APPMAP_CONFIG', config)
        env = {'APPMAP': 'true', 'APPMAP_CONFIG': config}

    appmap._implementation.initialize(env=env)  # pylint: disable=protected-access

    # Some tests want yaml instrumented, others don't.
    # Reload it to make sure it's instrumented, or not, as set in appmap.yml.
    importlib.reload(yaml)
