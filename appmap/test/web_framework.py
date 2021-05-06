"""Common tests for web frameworks such as django and flask."""

import json
import pytest


import appmap
from .normalize import normalize_appmap


@pytest.mark.appmap_enabled
class TestRequestCapture:
    """Common tests for HTTP server request and response capture."""
    @staticmethod
    def test_http_capture(client, events):
        """Test GET request and response capture."""
        client.get('/test')

        assert events[0].http_server_request.items() >= {
            'request_method': 'GET',
            'path_info': '/test',
            'protocol': 'HTTP/1.1'
        }.items()

        response = events[1].http_server_response
        assert response.items() >= {
            'status_code': 200,
            'mime_type': 'text/html; charset=utf-8'
        }.items()

        assert 'ETag' in response['headers']

    @staticmethod
    def test_http_capture_post(client, events):
        """Test POST request with JSON body capture."""
        client.post(
            '/test', json={'my_param': 'example'}, headers={
                'Authorization': 'token "test-token"',
                'Accept': 'application/json',
                'Accept-Language': 'pl'
            }
        )

        assert events[0].http_server_request.items() >= {
            'request_method': 'POST',
            'path_info': '/test',
            'protocol': 'HTTP/1.1',
            'authorization': 'token "test-token"',
            'mime_type': 'application/json',
        }.items()

        assert events[0].http_server_request['headers'].items() >= {
            'Accept': 'application/json',
            'Accept-Language': 'pl'
        }.items()


class TestRecording:
    """Common tests for remote recording."""

    @staticmethod
    def test_appmap_disabled(client):
        assert not appmap.enabled()

        res = client.get('/_appmap/record')
        assert res.status_code == 404

    @staticmethod
    @pytest.mark.appmap_enabled
    def test_starts_disabled(client):
        res = client.get('/_appmap/record')
        assert res.status_code == 200
        assert res.headers['Content-Type'] == 'application/json'
        data = res.json
        if callable(data):
            data = data()
        assert data == {'enabled': False}

    @staticmethod
    @pytest.mark.appmap_enabled
    def test_can_be_enabled(client):
        res = client.post('/_appmap/record')
        assert res.status_code == 200

    @staticmethod
    @pytest.mark.appmap_enabled
    def test_can_only_enable_once(client):
        res = client.post('/_appmap/record')
        assert res.status_code == 200
        res = client.post('/_appmap/record')
        assert res.status_code == 409

    @staticmethod
    @pytest.mark.appmap_enabled
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
        assert res.headers['Content-Type'] == 'application/json'
        data = res.data if hasattr(res, 'data') else res.content
        generated_appmap = normalize_appmap(data)

        with open(data_dir / 'remote.appmap.json') as expected:
            expected_appmap = json.load(expected)

        assert generated_appmap == expected_appmap

        res = client.delete('/_appmap/record')
        assert res.status_code == 404
