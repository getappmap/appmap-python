"""Test flask integration"""
# pylint: disable=missing-function-docstring

import importlib
import pytest

from appmap._implementation.env import Env

from .web_framework import TestRequestCapture, TestRecording  # pylint: disable=unused-import


@pytest.fixture(name='client')
def flask_client(data_dir, monkeypatch):
    monkeypatch.syspath_prepend(data_dir / 'flask')

    Env.current.set("APPMAP_CONFIG", data_dir / 'flask' / 'appmap.yml')

    import app  # pylint: disable=import-error
    importlib.reload(app)

    with app.app.test_client() as client:  # pylint: disable=no-member
        # set user agent so the version number doesn't break diff
        client.environ_base['HTTP_USER_AGENT'] = 'werkzeug'

        yield client
