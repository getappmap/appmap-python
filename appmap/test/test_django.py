# flake8: noqa: E402
# pylint: disable=unused-import, redefined-outer-name

import pytest
from appmap._implementation.recording import Recorder

pytest.importorskip('django')

import django.conf
import django.db
import django.test
import appmap.django  # noqa: F401

django.conf.settings.configure(
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    ROOT_URLCONF=()
)


@pytest.fixture
def events():
    rec = Recorder()
    rec.events().clear()
    rec.enabled = True
    yield rec.events()
    rec.enabled = False
    rec.events().clear()


def test_sql_capture(events):
    conn = django.db.connections['default']
    conn.cursor().execute('SELECT 1').fetchall()

    assert events[0].sql_query['sql'] == 'SELECT 1'


def test_http_capture(events):
    client = django.test.Client()
    client.get('/test')

    assert events[0].http_server_request == {
        'request_method': 'GET',
        'path_info': '/test',
        'protocol': 'HTTP/1.1'
    }

    assert events[1].http_server_response == {
        'status_code': 404,
        'mime_type': 'text/html'
    }
