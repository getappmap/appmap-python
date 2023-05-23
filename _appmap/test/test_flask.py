"""Test flask integration"""
# pylint: disable=missing-function-docstring

import importlib
import os
from threading import Thread

import flask
import pytest

from _appmap.env import Env
from _appmap.metadata import Metadata
from appmap.flask import AppmapFlask

from ..test.helpers import DictIncluding

# Make sure assertions in web_framework get rewritten (e.g. to show
# diffs in generated appmaps)
pytest.register_assert_rewrite("_appmap.test.web_framework")

# pylint: disable=unused-import,wrong-import-position
from .web_framework import TestRemoteRecording  # pyright:ignore
from .web_framework import TestRequestCapture  # pyright: ignore
from .web_framework import _TestRecordRequests, exec_cmd, wait_until_port_is

# pylint: enable=unused-import


@pytest.fixture(name="app")
def flask_app(data_dir, monkeypatch):
    monkeypatch.syspath_prepend(data_dir / "flask")

    Env.current.set("APPMAP_CONFIG", data_dir / "flask" / "appmap.yml")

    monkeypatch.setenv("FLASK_DEBUG", "True")

    import app  # pyright: ignore pylint: disable=import-error,import-outside-toplevel

    importlib.reload(app)

    # Add the AppmapFlask extension to the app. This now happens automatically when a Flask app is
    # started from the command line, but must be done manually otherwise.
    AppmapFlask().init_app(app.app)

    return app.app


@pytest.fixture(name="client")
def flask_client(app):
    with app.test_client() as client:  # pylint: disable=no-member
        yield client


# Recording is enabled as a side-effect of requesting the events fixture. There's probably a better
# way, but leave it here for now.
@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_framework_metadata(client, events):  # pylint: disable=unused-argument
    client.get("/")
    assert Metadata()["frameworks"] == [{"name": "flask", "version": flask.__version__}]


@pytest.mark.appmap_enabled
def test_template(app, events):
    with app.app_context():
        flask.render_template("test.html")
    assert events[0].to_dict() == DictIncluding(
        {
            "path": "_appmap/test/data/flask/templates/test.html",
            "event": "call",
            "defined_class": "<templates>._AppmapTestDataFlaskTemplatesTestHtml",
            "method_id": "render",
            "static": False,
        }
    )


class TestRecordRequestsFlask(_TestRecordRequests):
    def server_start_thread(self, debug=True):
        # Use appmap from our working copy, not the module installed by virtualenv. Add the init
        # directory so the sitecustomize.py file it contains will be loaded on startup. This
        # simulates a real installation.
        flask_debug = "FLASK_DEBUG=1" if debug else ""

        exec_cmd(
            """
export PYTHONPATH="$PWD"

cd _appmap/test/data/flask/
PYTHONPATH="$PYTHONPATH:$PWD/init"
"""
            + f" APPMAP_OUTPUT_DIR=/tmp {flask_debug} FLASK_APP=app.py flask run -p "
            + str(_TestRecordRequests.server_port)
        )

    def server_start(self, debug=True):
        # start as background thread so running the tests can continue
        def start_with_debug():
            self.server_start_thread(debug)

        thread = Thread(target=start_with_debug)
        thread.start()
        wait_until_port_is("127.0.0.1", _TestRecordRequests.server_port, "open")

    def server_stop(self):
        exec_cmd(
            "ps -ef"
            + "| grep -i 'flask run'"
            + "| grep -v grep"
            + "| awk '{ print $2 }'"
            + "| xargs kill -9"
        )
        wait_until_port_is("127.0.0.1", _TestRecordRequests.server_port, "closed")

    def test_record_request_appmap_enabled_requests_enabled_no_remote(self):
        self.server_stop()  # ensure it's not running
        self.server_start()
        self.record_request(False)
        self.server_stop()

    def test_record_request_appmap_enabled_requests_enabled_and_remote(self):
        self.server_stop()  # ensure it's not running
        self.server_start()
        self.record_request(True)
        self.server_stop()

    # it's not possible to test for
    # appmap_not_enabled_requests_enabled_and_remote because when
    # APPMAP=false the routes for remote recording are disabled.


class TestFlaskApp:
    """
    Run the tests in the fixture app. These depend on being able to manipulate the app's config in
    ways that are difficult to do from here.
    """

    @pytest.fixture(autouse=True)
    def beforeEach(self, monkeypatch, pytester):
        monkeypatch.setenv("PYTHONPATH", "init")
        pytester.copy_example("flask")

    def test_enabled(self, pytester):
        result = pytester.runpytest("-svv")

        result.assert_outcomes(passed=1, failed=0, errors=0)
        appmap_file = (
            pytester.path / "tmp" / "appmap" / "pytest" / "test_request.appmap.json"
        )
        assert not os.path.exists(pytester.path / "tmp" / "appmap" / "requests")
        assert appmap_file.exists()

    def test_disabled(self, pytester, monkeypatch):
        monkeypatch.setenv("APPMAP", "false")

        result = pytester.runpytest("-svv")

        result.assert_outcomes(passed=1, failed=0, errors=0)
        assert not (pytester.path / "tmp" / "appmap").exists()
