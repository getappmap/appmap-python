# flake8: noqa: E402
# pylint: disable=unused-import, redefined-outer-name, missing-function-docstring

import json
from pathlib import Path

import django
import django.conf
import django.core.handlers.exception
import django.db
import django.http
from django.template.loader import render_to_string
import django.test
from django.test.client import MULTIPART_CONTENT

import pytest

import appmap
import appmap.django  # noqa: F401
from appmap.test.helpers import DictIncluding

import sys
sys.path += [str(Path(__file__).parent / 'data' / 'django')]
import app
from .._implementation.metadata import Metadata

# Make sure assertions in web_framework get rewritten (e.g. to show
# diffs in generated appmaps)
pytest.register_assert_rewrite('appmap.test.web_framework')
from .web_framework import TestRequestCapture, TestRecording

@pytest.mark.django_db
def test_sql_capture(events):
    conn = django.db.connections['default']
    conn.cursor().execute('SELECT 1').fetchall()
    assert events[0].sql_query == DictIncluding({
        'sql': 'SELECT 1',
        'database_type': 'sqlite'
    })
    assert events[0].sql_query['server_version'].startswith('3.')
    assert Metadata()['frameworks'] == [{
        'name': 'Django',
        'version': django.get_version()
    }]


@pytest.mark.appmap_enabled
def test_framework_metadata(client, events):  # pylint: disable=unused-argument
    client.get('/')
    assert Metadata()['frameworks'] == [{
        'name': 'Django',
        'version': django.get_version()
    }]


@pytest.mark.appmap_enabled
def test_app_can_read_body(client, events):  # pylint: disable=unused-argument
    response = client.post('/echo', json={'test': 'json'})
    assert response.content == b'{"test": "json"}'


@pytest.mark.appmap_enabled
def test_template(events):
    render_to_string('hello_world.html')
    assert events[0].to_dict() == DictIncluding({
        'path': 'appmap/test/data/django/app/hello_world.html',
        'event': 'call',
        'defined_class': '<templates>.AppmapTestDataDjangoAppHello_WorldHtml',
        'method_id': 'render',
        'static': False
    })


# pylint: disable=arguments-differ
class ClientAdaptor(django.test.Client):
    """Adaptor for the client request parameters used in .web_framework tests."""

    # pylint: disable=too-many-arguments
    def generic(
        self, method, path, data='', content_type='application/octet-stream', secure=False,
        headers=None, json=None, **kwargs
    ):
        headers = {
            'HTTP_' + k.replace('-', '_').upper(): v
            for k, v in (headers or {}).items()
        }

        if json:
            content_type = 'application/json'
            data = self._encode_json(json, 'application/json')

        return super().generic(method, path, data, content_type, secure, **headers, **kwargs)


    def post(self, path, data=None, content_type=MULTIPART_CONTENT,
             secure=False, **extra):
        if content_type == 'multipart/form-data':
            content_type = MULTIPART_CONTENT
        return super().post(path, data, content_type, secure, **extra)


@pytest.fixture
def client():
    return ClientAdaptor()


@pytest.mark.appmap_enabled
def test_unnamed(client, events):
    client.get('/post/unnamed/5')

    assert appmap.enabled()     # sanity check
    # unnamed captures in a re_path don't show up in the event's
    # message attribute.
    assert len(events[0].message) == 0

@pytest.mark.appmap_enabled
def test_included_view(client, events):
    client.get('/post/included/test_user')

    assert len(events) == 2
    assert events[0].http_server_request == DictIncluding({
        'path_info': '/post/included/test_user',
        'normalized_path_info': '/post/included/{username}'
    })

@pytest.mark.appmap_enabled
def test_exception(client, events, monkeypatch):
    def raise_on_call(*args):
        raise RuntimeError('An error')
    monkeypatch.setattr(django.core.handlers.exception, 'response_for_exception', raise_on_call)

    with pytest.raises(RuntimeError):
        client.get('/exception')

    assert events[0].http_server_request == DictIncluding({
        'request_method': 'GET',
        'path_info': '/exception',
        'protocol': 'HTTP/1.1'
    })

    assert events[1].parent_id == events[0].id
    assert events[1].exceptions == [DictIncluding({
            'class': 'builtins.RuntimeError',
            'message': 'An error'
    })]

@pytest.mark.appmap_enabled
def test_deeply_nested_routes(client, events):
    client.get('/admincp/permissions/edit/1')

    assert len(events) == 2
    assert events[0].http_server_request == DictIncluding({
        'normalized_path_info': '/admincp/permissions/edit/{pk}'
    })

def test_middleware_reset(pytester, monkeypatch):
    monkeypatch.setenv('PYTHONPATH', 'init')
    monkeypatch.setenv('APPMAP', 'true')

    pytester.copy_example('django')

    # To really check middleware reset, the tests must run in order,
    # so disable randomly.
    pytester.runpytest('-svv', '-p', 'no:randomly')

    # Look for the http_server_request event in test_app's appmap. If
    # middleware reset is broken, it won't be there.
    appmap_file = pytester.path / 'tmp' / 'appmap' / 'pytest' / 'test_app.appmap.json'
    events = json.loads(appmap_file.read_text())['events']
    assert 'http_server_request' in events[0]
