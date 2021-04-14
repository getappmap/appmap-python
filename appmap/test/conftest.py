import os.path

import pytest

import appmap._implementation


@pytest.fixture
def appmap_enabled(data_dir, monkeypatch, request):
    monkeypatch.setenv('APPMAP', 'true')
    config = request.node.get_closest_marker('appmap_config')
    if config:
        config = config.args[0]
    else:
        config = 'appmap.yml'
    monkeypatch.setenv('APPMAP_CONFIG', os.path.join(data_dir, config))

    appmap._implementation.initialize()  # pylint: disable=protected-access

    yield

    monkeypatch.delenv('APPMAP')
    monkeypatch.delenv('APPMAP_CONFIG')

