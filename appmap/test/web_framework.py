"""Common tests for web frameworks such as django and flask."""
# pylint: disable=missing-function-docstring

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

    @staticmethod
    def test_post(events, client):
        client.post('/test', data=json.dumps({ 'my_param': 'example' }),
            content_type='application/json; charset=UTF-8',
            headers={
                'Authorization': 'token "test-token"',
                'Accept': 'application/json',
                'Accept-Language': 'pl'
            }
        )

        assert events[0].message == [
            {
                'name': 'my_param',
                'class': 'builtins.str',
                'object_id': events[0].message[0]['object_id'],
                'value': "'example'"
            }
        ]
        assert events[0].http_server_request.items() >= {
            'request_method': 'POST',
            'path_info': '/test',
            'protocol': 'HTTP/1.1',
            'authorization': 'token "test-token"',
            'mime_type': 'application/json; charset=UTF-8',
        }.items()

        assert events[0].http_server_request['headers'].items() >= {
            'Accept': 'application/json',
            'Accept-Language': 'pl'
        }.items()

    @staticmethod
    def test_get(events, client):
        client.get('/test?my_param=example')

        assert events[0].message == [
            {
                'name': 'my_param',
                'class': 'builtins.str',
                'object_id': events[0].message[0]['object_id'],
                'value': "'example'"
            }
        ]

    @staticmethod
    def test_get_arr(events, client):
        client.get('/test?my_param=example&my_param=example2')

        assert events[0].message == [
            {
                'name': 'my_param',
                'class': 'builtins.list',
                'object_id': events[0].message[0]['object_id'],
                'value': "['example', 'example2']"
            },
        ]


    @staticmethod
    def test_post_form_urlencoded(events, client):
        client.post(
            '/test', data='my_param=example',
            content_type='application/x-www-form-urlencoded'
        )

        assert events[0].message == [
            {
                'name': 'my_param',
                'class': 'builtins.str',
                'object_id': events[0].message[0]['object_id'],
                'value': "'example'"
            }
        ]

    @staticmethod
    def test_put(events, client):
        client.put('/test', json={ 'my_param': 'example' })

        assert events[0].message == [
            {
                'name': 'my_param',
                'class': 'builtins.str',
                'object_id': events[0].message[0]['object_id'],
                'value': "'example'"
            }
        ]

    @staticmethod
    def test_post_bad_json(events, client):
        client.post('/test?my_param=example', data="bad json", content_type='application/json')

        assert events[0].message == [
            {
                'name': 'my_param',
                'class': 'builtins.str',
                'object_id': events[0].message[0]['object_id'],
                'value': "'example'"
            }
        ]

    @staticmethod
    def test_post_multipart(events, client):
        client.post('/test', data={ 'my_param': 'example' }, content_type='multipart/form-data')

        assert events[0].message == [
            {
                'name': 'my_param',
                'class': 'builtins.str',
                'object_id': events[0].message[0]['object_id'],
                'value': "'example'"
            }
        ]

    @staticmethod
    def test_post_with_query(events, client):
        client.post('/test?my_param=get', data={ 'my_param': 'example' })

        assert events[0].message == [
            {
                'name': 'my_param',
                'class': 'builtins.list',
                'object_id': events[0].message[0]['object_id'],
                'value': "['get', 'example']"
            }
        ]

    @staticmethod
    @pytest.mark.parametrize('url,expected', [
        ('/user/test_user', '/user/{username}'),
        ('/post/123', '/post/{post_id}'),
        ('/post/test_user/123/summary', '/post/{username}/{post_id}/summary')
    ])
    def test_path_normalization(client, events, url, expected):
        client.get(url)
        np = events[0].http_server_request['normalized_path_info']
        assert np == expected

    @staticmethod
    @pytest.mark.appmap_enabled
    def test_message_path_segments(events, client):
        client.get('/post/alice/42/summary')

        assert events[0].message == [
            {
                'name': 'username',
                'class': 'builtins.str',
                'object_id': events[0].message[0]['object_id'],
                'value': "'alice'"
            },
            {
                'name': 'post_id',
                'class': 'builtins.int',
                'object_id': events[0].message[1]['object_id'],
                'value': "42"
            }
        ]


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

