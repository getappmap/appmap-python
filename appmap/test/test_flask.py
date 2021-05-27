"""Test flask integration"""
# pylint: disable=missing-function-docstring

import flask
import importlib
import pytest

from appmap._implementation.env import Env
from .._implementation.metadata import Metadata

from .web_framework import TestRequestCapture, TestRecording  # pylint: disable=unused-import


@pytest.fixture(name='client')
def flask_client(data_dir, monkeypatch):
    monkeypatch.syspath_prepend(data_dir / 'flask')

    Env.current.set("APPMAP_CONFIG", data_dir / 'flask' / 'appmap.yml')

    import app  # pylint: disable=import-error
    importlib.reload(app)

    with app.app.test_client() as client:  # pylint: disable=no-member
        yield client


@pytest.mark.appmap_enabled
def test_framework_metadata(client, events):  # pylint: disable=unused-argument
    client.get('/')
    assert Metadata()['frameworks'] == [{
        'name': 'flask',
        'version': flask.__version__
    }]
