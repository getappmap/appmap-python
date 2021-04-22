"""Test flask integration"""

import importlib
import json
import os
import sys

import pytest

from .appmap_test_base import AppMapTestBase

# pylint: disable=redefined-outer-name
@pytest.fixture
def flask_client(data_dir, monkeypatch):
    sys.path.append(os.path.join(data_dir, 'flask'))

    monkeypatch.setenv("APPMAP_CONFIG", os.path.join(data_dir, 'flask', 'appmap.yml'))

    import app  # pylint: disable=import-error
    importlib.reload(app)

    with app.app.test_client() as client:  # pylint: disable=no-member
        yield client


def test_flask_appmap_disabled(flask_client):
    res = flask_client.get('/_appmap/record')
    assert res.status_code == 404

@pytest.mark.usefixtures('appmap_enabled')
class TestFlaskRemoteRecording(AppMapTestBase):
    def test_starts_disabled(self, flask_client):
        res = flask_client.get('/_appmap/record')
        assert res.status_code == 200
        assert res.is_json
        assert res.json == {'enabled': False}

    def test_can_be_enabled(self, flask_client):
        res = flask_client.post('/_appmap/record')
        assert res.status_code == 200
        assert res.content_length == 0

    def test_can_only_enable_once(self, flask_client):
        res = flask_client.post('/_appmap/record')
        assert res.status_code == 200
        res = flask_client.post('/_appmap/record')
        assert res.status_code == 409

    def test_can_record(self, data_dir, flask_client):
        res = flask_client.post('/_appmap/record')
        assert res.status_code == 200

        res = flask_client.get('/')
        assert res.status_code == 200

        res = flask_client.get('/user/test_user')
        assert res.status_code == 200

        res = flask_client.get('/post/123')
        assert res.status_code == 200

        res = flask_client.delete('/_appmap/record')
        assert res.status_code == 200
        assert res.is_json
        generated_appmap = self.normalize_appmap(json.dumps(res.json))

        with open(os.path.join(data_dir, 'flask', 'expected.appmap.json')) as f:
            expected_appmap = json.load(f)

        assert generated_appmap == expected_appmap

        res = flask_client.delete('/_appmap/record')
        assert res.status_code == 404

    @staticmethod
    def test_http_capture(flask_client, events):
        flask_client.get('/test')

        assert events[0].http_server_request.items() >= {
            'request_method': 'GET',
            'path_info': '/test',
            'protocol': 'HTTP/1.1'
        }.items()

        assert events[1].http_server_response == {
            'status_code': 404,
            'mime_type': 'text/html; charset=utf-8'
        }
