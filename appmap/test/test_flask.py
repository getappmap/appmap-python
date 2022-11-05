"""Test flask integration"""
# pylint: disable=missing-function-docstring

import importlib
from threading import Thread

import flask
import pytest

from appmap._implementation.env import Env
from appmap.flask import AppmapFlask
from appmap.test.helpers import DictIncluding

from .._implementation.metadata import Metadata
from .web_framework import (  # pylint: disable=unused-import
    TestRecordRequests,
    exec_cmd,
    wait_until_port_is,
)

# Make sure assertions in web_framework get rewritten (e.g. to show
# diffs in generated appmaps)
pytest.register_assert_rewrite("appmap.test.web_framework")


@pytest.fixture(name="client")
def flask_client(app):
    with app.test_client() as client:  # pylint: disable=no-member
        yield client


@pytest.fixture(name="app")
def flask_app(data_dir, monkeypatch):
    monkeypatch.syspath_prepend(data_dir / "flask")

    Env.current.set("APPMAP_CONFIG", data_dir / "flask" / "appmap.yml")

    import app  # pyright: ignore pylint: disable=import-error,import-outside-toplevel

    importlib.reload(app)

    # Add the AppmapFlask extension to the app. This now happens automatically when a Flask app is
    # started from the command line, but must be done manually otherwise.
    AppmapFlask().init_app(app.app)

    return app.app


@pytest.mark.appmap_enabled
def test_framework_metadata(
    client, events, monkeypatch
):  # pylint: disable=unused-argument
    monkeypatch.setenv("APPMAP_RECORD_REQUESTS", "false")
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
    def server_start_thread(env_vars_str):
        # Use appmap from our working copy, not the module installed by virtualenv. Add the init
        # directory so the sitecustomize.py file it contains will be loaded on startup. This
        # simulates a real installation.
        exec_cmd(
            """
export PYTHONPATH="$PWD"

cd appmap/test/data/flask/
PYTHONPATH="$PYTHONPATH:$PWD/init"
"""
            + env_vars_str
            + """ APPMAP_OUTPUT_DIR=/tmp FLASK_DEBUG=1 FLASK_APP=app.py flask run -p """
            + str(TestRecordRequests.server_port)
        )

    @staticmethod
    def server_start(env_vars_str):
        # start as background thread so running the tests can continue
        thread = Thread(
            target=TestRecordRequestsFlask.server_start_thread, args=(env_vars_str,)
        )
        thread.start()
        wait_until_port_is("127.0.0.1", TestRecordRequests.server_port, "open")

    @staticmethod
    def server_stop():
        exec_cmd(
            "ps -ef"
            + "| grep -i 'flask run'"
            + "| grep -v grep"
            + "| awk '{ print $2 }'"
            + "| xargs kill -9"
        )
        wait_until_port_is("127.0.0.1", TestRecordRequests.server_port, "closed")

    def test_record_request_appmap_enabled_requests_enabled_no_remote(client, events):
        TestRecordRequestsFlask.server_stop()  # ensure it's not running
        TestRecordRequestsFlask.server_start("APPMAP=true APPMAP_RECORD_REQUESTS=true")
        TestRecordRequests.record_request(client, events, False)
        TestRecordRequestsFlask.server_stop()

    def test_record_request_appmap_enabled_requests_enabled_and_remote(client, events):
        TestRecordRequestsFlask.server_stop()  # ensure it's not running
        TestRecordRequestsFlask.server_start("APPMAP=true APPMAP_RECORD_REQUESTS=true")
        TestRecordRequests.record_request(client, events, True)
        TestRecordRequestsFlask.server_stop()

    # not enabled means APPMAP isn't set.  This isn't the same as APPMAP=false.
    def test_record_request_appmap_not_enabled_requests_enabled_no_remote(
        client, events
    ):
        TestRecordRequestsFlask.server_stop()  # ensure it's not running
        TestRecordRequestsFlask.server_start("APPMAP_RECORD_REQUESTS=true")
        TestRecordRequests.record_request(client, events, False)
        TestRecordRequestsFlask.server_stop()

    # it's not possible to test for
    # appmap_not_enabled_requests_enabled_and_remote because when
    # APPMAP=false the routes for remote recording are disabled.
