"""Test flask integration"""
# pylint: disable=missing-function-docstring

import importlib
import json
import os
from importlib.metadata import version
from types import SimpleNamespace as NS

import flask
import pytest

from _appmap.env import Env
from _appmap.metadata import Metadata
from appmap.flask import AppmapFlask

from ..test.helpers import DictIncluding, check_call_stack
from .web_framework import (
    _TestFormCapture,
    _TestFormData,
    _TestRecordRequests,
    _TestRemoteRecording,
    _TestRequestCapture,
)

class TestFormCapture(_TestFormCapture):
    pass


class TestFormTest(_TestFormData):
    pass


class TestRecordRequests(_TestRecordRequests):
    pass


class TestRemoteRecording(_TestRemoteRecording):
    pass


class TestRequestCapture(_TestRequestCapture):
    pass


@pytest.fixture(name="app")
def flask_app(data_dir, monkeypatch):
    monkeypatch.syspath_prepend(data_dir / "flask")

    Env.current.set("APPMAP_CONFIG", data_dir / "flask" / "appmap.yml")

    monkeypatch.setenv("FLASK_DEBUG", "True")

    import flaskapp  # pyright: ignore pylint: disable=import-error,import-outside-toplevel

    importlib.reload(flaskapp)

    # Add the AppmapFlask extension to the app. This now happens automatically when a Flask app is
    # started from the command line, but must be done manually otherwise.
    AppmapFlask(flaskapp.app).init_app()

    return flaskapp.app


@pytest.fixture(name="client")
def flask_client(app):
    with app.test_client() as client:  # pylint: disable=no-member
        yield client


# Recording is enabled as a side-effect of requesting the events fixture. There's probably a better
# way, but leave it here for now.
@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_framework_metadata(client, events):  # pylint: disable=unused-argument
    client.get("/")
    assert Metadata()["frameworks"] == [{"name": "flask", "version": version("flask")}]


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_exception(client, events):
    with pytest.raises(Exception):
        client.get("/exception")

    assert events[0].http_server_request == DictIncluding(
        {"request_method": "GET", "path_info": "/exception", "protocol": "HTTP/1.1"}
    )

    assert events[1].event == "return"
    assert events[1].parent_id == events[0].id
    assert events[1].http_server_response["status_code"] == 500


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_not_found(client, events):
    client.get("/not_found")

    assert events[0].http_server_request == DictIncluding(
        {"request_method": "GET", "path_info": "/not_found", "protocol": "HTTP/1.1"}
    )

    assert events[1].event == "return"
    assert events[1].parent_id == events[0].id
    assert events[1].http_server_response["status_code"] == 404


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_bad_request(client, events):
    client.post("/test")

    assert events[0].http_server_request == DictIncluding(
        {"request_method": "POST", "path_info": "/test", "protocol": "HTTP/1.1"}
    )

    assert events[1].event == "return"
    assert events[1].parent_id == events[0].id
    assert events[1].http_server_response["status_code"] == 405


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_errorhandler(client, events):
    response = client.post("/do_post", content_type="application/json")

    # Verify that the custom errorhandler was used
    assert response.text == "That's a bad request!"

    assert events[0].http_server_request == DictIncluding(
        {"request_method": "POST", "path_info": "/do_post", "protocol": "HTTP/1.1"}
    )

    assert events[1].event == "return"
    assert events[1].parent_id == events[0].id
    assert events[1].http_server_response["status_code"] == 400


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


@pytest.fixture(name="server")
def flask_server(xprocess, server_base):
    debug = server_base.debug
    host = server_base.host
    port = server_base.port

    name = "flask"
    pattern = f"Running on http://{host}:{port}"
    cmd = f" -m flask run -p {port}"
    env = {
        "FLASK_APP": "flaskapp.py",
        "FLASK_DEBUG": "1" if debug else "0",
    }
    xprocess.ensure(name, server_base.factory(name, cmd, pattern, env))

    url = f"http://{server_base.host}:{port}"
    yield NS(debug=debug, url=url)

    xprocess.getinfo(name).terminate()

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

        result.assert_outcomes(passed=3, failed=0, errors=0)
        appmap_file = (
            pytester.path / "tmp" / "appmap" / "pytest" / "test_request.appmap.json"
        )

        # No request recordings should have been created
        assert not os.path.exists(pytester.path / "tmp" / "appmap" / "requests")

        # but there should be a test recording
        assert appmap_file.exists()

    def test_disabled(self, pytester, monkeypatch):
        monkeypatch.setenv("_APPMAP", "false")

        result = pytester.runpytest("-svv")

        result.assert_outcomes(passed=3, failed=0, errors=0)
        assert not (pytester.path / "tmp" / "appmap").exists()

    def test_disabled_for_process(self, pytester, monkeypatch):
        monkeypatch.setenv("APPMAP_RECORD_PROCESS", "true")

        result = pytester.runpytest("-svv")

        result.assert_outcomes(passed=3, failed=0, errors=0)

        assert (pytester.path / "tmp" / "appmap" / "process").exists()
        assert not (pytester.path / "tmp" / "appmap" / "requests").exists()
        assert not (pytester.path / "tmp" / "appmap" / "pytest").exists()

def verify_events(events):
    def find(event_type):
        return next(filter(lambda e: e[1].get(event_type) is not None, enumerate(events)), None)

    request = find("http_server_request")
    assert request is not None
    request_idx, request_event = request

    response = find("http_server_response")
    assert response is not None
    response_idx, response_event = response

    assert response_event.get("parent_id") == request_event.get("id")

    nested_events = events[request_idx + 1 : response_idx]
    check_call_stack(nested_events)


@pytest.mark.example_dir("flask-instrumented")
class TestFlaskInstrumented:

    def test_all(self, testdir):
        result = testdir.runpytest("-svv")
        result.assert_outcomes(passed=4)

    def test_response(self, testdir):
        result = testdir.runpytest("-svv", "-k", "test_request")
        result.assert_outcomes(passed=1)

        appmap_file = testdir.path / "tmp" / "appmap" / "pytest" / "test_request.appmap.json"
        appmap = json.load(appmap_file.open())
        verify_events(appmap["events"])

    def test_unhandled_exception(self, testdir):
        result = testdir.runpytest("-svv", "-k", "test_exception")
        result.assert_outcomes(passed=1)

        appmap_file = testdir.path / "tmp" / "appmap" / "pytest" / "test_exception.appmap.json"
        appmap = json.load(appmap_file.open())
        verify_events(appmap["events"])

    def test_default_exception(self, testdir):
        result = testdir.runpytest("-svv", "-k", "test_not_found")
        result.assert_outcomes(passed=1)

        appmap_file = testdir.path / "tmp" / "appmap" / "pytest" / "test_not_found.appmap.json"
        appmap = json.load(appmap_file.open())
        verify_events(appmap["events"])

    def test_errorhandler(self, testdir):
        result = testdir.runpytest("-svv", "-k", "test_errorhandler")
        result.assert_outcomes(passed=1)

        appmap_file = testdir.path / "tmp" / "appmap" / "pytest" / "test_errorhandler.appmap.json"
        appmap = json.load(appmap_file.open())
        verify_events(appmap["events"])
