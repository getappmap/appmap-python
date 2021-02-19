import pytest
from appmap._implementation.recording import Recorder

pytest.importorskip('django')

# flake8: noqa: E402
import django.conf
import django.db
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
