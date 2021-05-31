# flake8: noqa: E402
# pylint: disable=unused-import, redefined-outer-name, missing-function-docstring

import django
import django.conf
import django.db
import django.http
import django.test
from django.test.client import MULTIPART_CONTENT
from django.urls import include, path, re_path
import pytest

import appmap
import appmap.django  # noqa: F401
from appmap.test.helpers import DictIncluding
from .._implementation.metadata import Metadata

# Make sure assertions in web_framework get rewritten (e.g. to show
# diffs in generated appmaps)
pytest.register_assert_rewrite('appmap.test.web_framework')
from .web_framework import TestRequestCapture, TestRecording

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

def user_view(_request, username):
    return django.http.HttpResponse(f'user {username}')

def post_view(_request, post_id):
    return django.http.HttpResponse(f'post {post_id}')

def post_unnamed_view(_request, arg):
    return django.http.HttpResponse(f'post with unnamed, {arg}')

def user_post_view(_request, username, post_id):
    return django.http.HttpResponse(f'post {username} {post_id}')

def echo_view(request):
    return django.http.HttpResponse(request.body)

def user_included_view(_request, username):
    return django.http.HttpResponse(f'user {username}, included')

urlpatterns = [
    path('test', view),
    path('', view),
    re_path('^user/(?P<username>[^/]+)$', user_view),
    path('post/<int:post_id>', post_view),
    path('post/<username>/<int:post_id>/summary', user_post_view),
    re_path(r'^post/unnamed/(\d+)$', post_unnamed_view),
    path('echo', echo_view),
    re_path(r'^post/included/', include([
            path('<username>', user_view)]))
]


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

django.conf.settings.configure(
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    MIDDLEWARE=['django.middleware.http.ConditionalGetMiddleware'],
    ROOT_URLCONF='appmap.test.test_django'
)
