# flake8: noqa: E402
# pylint: disable=unused-import, redefined-outer-name, missing-function-docstring

import django.conf
import django.db
import django.http
import django.test
from django.test.client import MULTIPART_CONTENT
import django.urls
import pytest


import appmap.django  # noqa: F401

from .web_framework import TestRequestCapture, TestRecording


def test_sql_capture(events):
    conn = django.db.connections['default']
    conn.cursor().execute('SELECT 1').fetchall()
    assert events[0].sql_query.items() >= {
        'sql': 'SELECT 1',
        'database_type': 'sqlite'
    }.items()
    assert events[0].sql_query['server_version'].startswith('3.')


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


def view(_request):
    return django.http.HttpResponse('testing')

def user_view(_request, name):
    return django.http.HttpResponse(f'user {name}')

def post_view(_request, post_id):
    return django.http.HttpResponse(f'post {post_id}')

def user_post_view(_request, name, post_id):
    return django.http.HttpResponse(f'user {name} post {post_id} summary')

urlpatterns = [
    django.urls.path('test', view),
    django.urls.path('', view),
    django.urls.path('user/<name>', user_view),
    django.urls.path('post/<int:post_id>', post_view),
    django.urls.path('post/<name>/<int:post_id>/summary', user_post_view),
]


django.conf.settings.configure(
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    MIDDLEWARE=['django.middleware.http.ConditionalGetMiddleware'],
    ROOT_URLCONF='appmap.test.test_django'
)
