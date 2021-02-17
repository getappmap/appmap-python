import pytest
from appmap._implementation.recording import Recorder

pytest.importorskip('django')


def test_sql_capture():
    # pylint: disable=unused-import
    import django.conf
    import django.db
    import appmap.django  # noqa: F401

    recorder = Recorder()
    recorder.events().clear()
    recorder.enabled = True

    django.conf.settings.configure(DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}})

    conn = django.db.connections['default']
    conn.cursor().execute('SELECT 1').fetchall()

    recorder.enabled = False
    assert recorder.events()[0].sql_query['sql'] == 'SELECT 1'
