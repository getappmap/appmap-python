"""Test flask integration"""
# pylint: disable=missing-function-docstring

import importlib
import os
from importlib.metadata import version
from types import SimpleNamespace as NS

import flask
import pytest

from _appmap.env import Env
from _appmap.metadata import Metadata
from appmap.flask import AppmapFlask

from ..test.helpers import DictIncluding
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
def test_exception(client, events):  # pylint: disable=unused-argument
    with pytest.raises(Exception):
        client.get("/exception")

    assert events[0].http_server_request == DictIncluding(
        {"request_method": "GET", "path_info": "/exception", "protocol": "HTTP/1.1"}
    )
    assert events[1].event == "return"
    assert events[1].parent_id == events[0].id
    assert events[1].exceptions == [
        DictIncluding({"class": "builtins.Exception", "message": "An exception"})
    ]


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

        result.assert_outcomes(passed=1, failed=0, errors=0)
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

        result.assert_outcomes(passed=1, failed=0, errors=0)
        assert not (pytester.path / "tmp" / "appmap").exists()

    def test_disabled_for_process(self, pytester, monkeypatch):
        monkeypatch.setenv("APPMAP_RECORD_PROCESS", "true")

        result = pytester.runpytest("-svv")

        result.assert_outcomes(passed=1, failed=0, errors=0)

        assert (pytester.path / "tmp" / "appmap" / "process").exists()
        assert not (pytester.path / "tmp" / "appmap" / "requests").exists()
        assert not (pytester.path / "tmp" / "appmap" / "pytest").exists()
