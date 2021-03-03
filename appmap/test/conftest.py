import os.path

import pytest

import appmap._implementation


@pytest.fixture
def appmap_enabled(data_dir, monkeypatch):
    monkeypatch.setenv('APPMAP', 'true')
    monkeypatch.setenv('APPMAP_CONFIG', os.path.join(data_dir, 'appmap.yml'))

    appmap._implementation.initialize()  # pylint: disable=protected-access

    yield

    monkeypatch.delenv('APPMAP')
    monkeypatch.delenv('APPMAP_CONFIG')

