# flake8: noqa: E402
# pylint: disable=unused-import, redefined-outer-name, missing-function-docstring

import django.conf
import django.db
import django.http
import django.test
import django.urls
import pytest


import appmap.django  # noqa: F401

from .web_framework import TestRequestCapture


def test_sql_capture(events):
    conn = django.db.connections['default']
    conn.cursor().execute('SELECT 1').fetchall()
    assert events[0].sql_query.items() >= {
        'sql': 'SELECT 1',
        'database_type': 'sqlite'
    }.items()
    assert events[0].sql_query['server_version'].startswith('3.')


def test_message_capture_post(events, client):
    client.post('/test', { 'my_param': 'example' },
        content_type='application/json; charset=UTF-8',
        HTTP_AUTHORIZATION='token "test-token"',
        HTTP_ACCEPT='application/json',
        HTTP_ACCEPT_LANGUAGE='pl'
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

def test_message_capture_get(events, client):
    client.get('/test', { 'my_param': 'example' })

    assert events[0].message == [
        {
            'name': 'my_param',
            'class': 'builtins.str',
            'object_id': events[0].message[0]['object_id'],
            'value': "'example'"
        }
    ]

def test_message_capture_get_arr(events, client):
    client.get('/test', { 'my_param': ['example', 'example2'] })

    assert events[0].message == [
        {
            'name': 'my_param',
            'class': 'builtins.list',
            'object_id': events[0].message[0]['object_id'],
            'value': "['example', 'example2']"
        },
    ]


def test_message_capture_post_form_urlencoded(events, client):
    client.post('/test', 'my_param=example', content_type='application/x-www-form-urlencoded')

    assert events[0].message == [
        {
            'name': 'my_param',
            'class': 'builtins.str',
            'object_id': events[0].message[0]['object_id'],
            'value': "'example'"
        }
    ]

def test_message_capture_put(events, client):
    client.put('/test', { 'my_param': 'example' }, content_type='application/json')

    assert events[0].message == [
        {
            'name': 'my_param',
            'class': 'builtins.str',
            'object_id': events[0].message[0]['object_id'],
            'value': "'example'"
        }
    ]

def test_message_capture_post_bad_json(events, client):
    client.post('/test?my_param=example', "bad json", content_type='application/json')

    assert events[0].message == [
        {
            'name': 'my_param',
            'class': 'builtins.str',
            'object_id': events[0].message[0]['object_id'],
            'value': "'example'"
        }
    ]


def test_message_capture_post_multipart(events, client):
    client.post('/test', { 'my_param': 'example' })

    assert events[0].message == [
        {
            'name': 'my_param',
            'class': 'builtins.str',
            'object_id': events[0].message[0]['object_id'],
            'value': "'example'"
        }
    ]


def test_message_capture_post_with_query(events, client):
    client.post('/test?my_param=get', { 'my_param': 'example' })

    assert events[0].message == [
        {
            'name': 'my_param',
            'class': 'builtins.list',
            'object_id': events[0].message[0]['object_id'],
            'value': "['get', 'example']"
        }
    ]


# pylint: disable=arguments-differ
class ClientAdaptor(django.test.Client):
    """Adaptor for the client request parameters used in .web_framework tests."""
    def generic(self, *args, headers=None, **kwargs):
        headers = {
            'HTTP_' + k.replace('-', '_').upper(): v
            for k, v in (headers or {}).items()
        }
        return super().generic(*args, **headers, **kwargs)

    def post(self, *args, json=None, **kwargs):
        if json:
            kwargs['data'] = json
            kwargs['content_type'] = 'application/json'
        return super().post(*args, **kwargs)


@pytest.fixture
def client():
    return ClientAdaptor()


def view(_request):
    return django.http.HttpResponse('testing')


urlpatterns = [
    django.urls.path('test', view)
]


django.conf.settings.configure(
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    MIDDLEWARE=['django.middleware.http.ConditionalGetMiddleware'],
    ROOT_URLCONF='appmap.test.test_django'
)
