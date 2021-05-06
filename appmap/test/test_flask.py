"""Test flask integration"""
# pylint: disable=missing-function-docstring

import importlib
import json
import os

import pytest

import appmap
from appmap._implementation.env import Env

from .normalize import normalize_appmap
from .web_framework import TestRequestCapture  # pylint: disable=unused-import


@pytest.fixture(name='client')
def flask_client(data_dir, monkeypatch):
    monkeypatch.syspath_prepend(os.path.join(data_dir, 'flask'))

    Env.current.set("APPMAP_CONFIG",
                    os.path.join(data_dir, 'flask', 'appmap.yml'))

    import app  # pylint: disable=import-error
    importlib.reload(app)

    with app.app.test_client() as client:  # pylint: disable=no-member
        # set user agent so the version number doesn't break diff
        client.environ_base['HTTP_USER_AGENT'] = 'werkzeug'

        yield client


def test_flask_appmap_disabled(client):
    assert not appmap.enabled()

    res = client.get('/_appmap/record')
    assert res.status_code == 404

@pytest.mark.appmap_enabled
class TestFlask:
    @staticmethod
    def test_starts_disabled(client):
        res = client.get('/_appmap/record')
        assert res.status_code == 200
        assert res.is_json
        assert res.json == {'enabled': False}

    @staticmethod
    def test_can_be_enabled(client):
        res = client.post('/_appmap/record')
        assert res.status_code == 200
        assert res.content_length == 0

    @staticmethod
    def test_can_only_enable_once(client):
        res = client.post('/_appmap/record')
        assert res.status_code == 200
        res = client.post('/_appmap/record')
        assert res.status_code == 409

    @staticmethod
    def test_can_record(data_dir, client):
        res = client.post('/_appmap/record')
        assert res.status_code == 200

        res = client.get('/')
        assert res.status_code == 200

        res = client.get('/user/test_user')
        assert res.status_code == 200

        res = client.get('/post/123')
        assert res.status_code == 200

        res = client.delete('/_appmap/record')
        assert res.status_code == 200
        assert res.is_json
        generated_appmap = normalize_appmap(json.dumps(res.json))

        with open(os.path.join(data_dir, 'flask', 'expected.appmap.json')) as f:
            expected_appmap = json.load(f)

        assert generated_appmap == expected_appmap

        res = client.delete('/_appmap/record')
        assert res.status_code == 404
