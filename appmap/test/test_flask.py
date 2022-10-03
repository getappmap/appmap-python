"""Test flask integration"""
# pylint: disable=missing-function-docstring

import importlib
from threading import Thread

import flask
import pytest

from appmap._implementation.env import Env
from appmap.test.helpers import DictIncluding

from .._implementation.metadata import Metadata
from .web_framework import (  # pylint: disable=unused-import
    TestRecording,
    TestRecordRequests,
    TestRequestCapture,
    exec_cmd,
    wait_until_port_is,
)


@pytest.fixture(name="client")
def flask_client(app):
    with app.test_client() as client:  # pylint: disable=no-member
        yield client


@pytest.fixture(name="app")
def flask_app(data_dir, monkeypatch):
    monkeypatch.syspath_prepend(data_dir / "flask")

    Env.current.set("APPMAP_CONFIG", data_dir / "flask" / "appmap.yml")

    import app  # pylint: disable=import-error

    importlib.reload(app)
    return app.app


@pytest.mark.appmap_enabled
def test_framework_metadata(client, events):  # pylint: disable=unused-argument
    client.get("/")
    assert Metadata()["frameworks"] == [{"name": "flask", "version": flask.__version__}]


@pytest.mark.appmap_enabled
def test_template(app, events):
    with app.app_context():
        flask.render_template("test.html")
    assert events[0].to_dict() == DictIncluding(
        {
            "path": "appmap/test/data/flask/templates/test.html",
            "event": "call",
            "defined_class": "<templates>.AppmapTestDataFlaskTemplatesTestHtml",
            "method_id": "render",
            "static": False,
        }
    )


class TestRecordRequestsFlask(TestRecordRequests):
    @staticmethod
    def setup_class():
        TestRecordRequestsFlask.server_stop()  # ensure it's not running
        TestRecordRequestsFlask.server_start()

    @staticmethod
    def teardown_class():
        TestRecordRequestsFlask.server_stop()

    @staticmethod
    def server_start_thread():
        exec_cmd(
            """
# use appmap from our working copy, not the module installed by virtualenv
export PYTHONPATH=`pwd`

cd appmap/test/data/flask/
APPMAP=true APPMAP_RECORD_REQUESTS=true FLASK_DEBUG=1 FLASK_APP=app.py flask run -p """
            + str(TestRecordRequests.server_port)
        )

    @staticmethod
    def server_start():
        # start as background thread so running the tests can continue
        thread = Thread(target=TestRecordRequestsFlask.server_start_thread)
        thread.start()
        wait_until_port_is("127.0.0.1", TestRecordRequests.server_port, "open")

    @staticmethod
    def server_stop():
        exec_cmd(
            "ps -ef | grep -i 'flask run' | grep -v grep | awk '{ print $2 }' | xargs kill -9"
        )
        wait_until_port_is("127.0.0.1", TestRecordRequests.server_port, "closed")

    @pytest.mark.skipif(True, reason="don't pass until _EventIds stops producing duplicate ids")
    def test_record_request_no_remote(client, events):
        TestRecordRequests.record_request(client, events, False)

    @pytest.mark.skipif(True, reason="don't pass until _EventIds stops producing duplicate ids")
    def test_record_request_and_remote(client, events):
        TestRecordRequests.record_request(client, events, True)
