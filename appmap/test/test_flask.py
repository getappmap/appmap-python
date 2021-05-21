"""Test flask integration"""
# pylint: disable=missing-function-docstring

import importlib
import pytest

from appmap._implementation.env import Env

from .web_framework import TestRequestCapture, TestRecording  # pylint: disable=unused-import


@pytest.fixture(name='client')
def flask_client(data_dir, monkeypatch):
    monkeypatch.syspath_prepend(data_dir / 'flask')

    Env.current.set("APPMAP_CONFIG", data_dir / 'flask' / 'appmap.yml')

    import app  # pylint: disable=import-error
    importlib.reload(app)

    with app.app.test_client() as client:  # pylint: disable=no-member
        yield client


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
