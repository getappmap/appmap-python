# flake8: noqa: E402
# pylint: disable=missing-function-docstring,redefined-outer-name

import json
import os
import sys
from pathlib import Path
from threading import Thread

import django
import django.core.handlers.exception
import django.db
import django.http
import django.test
import pytest
from django.template.loader import render_to_string
from django.test.client import MULTIPART_CONTENT

import appmap
import appmap.django  # noqa: F401
from _appmap.metadata import Metadata

from ..test.helpers import DictIncluding

# Make sure assertions in web_framework get rewritten (e.g. to show
# diffs in generated appmaps)
pytest.register_assert_rewrite("_appmap.test.web_framework")

# pylint: disable=unused-import,wrong-import-position
from .web_framework import TestRemoteRecording  # pyright:ignore
from .web_framework import TestRequestCapture  # pyright: ignore
from .web_framework import _TestRecordRequests, exec_cmd, wait_until_port_is

# pylint: enable=unused-import

sys.path += [str(Path(__file__).parent / "data" / "django")]

# Import app just for the side-effects. It must happen after sys.path has been modified.
import app  # pyright: ignore pylint: disable=import-error, unused-import,wrong-import-order,wrong-import-position


@pytest.mark.django_db
@pytest.mark.appmap_enabled(appmap_enabled=False)
def test_sql_capture(events):
    conn = django.db.connections["default"]
    conn.cursor().execute("SELECT 1").fetchall()
    assert events[0].sql_query == DictIncluding({"sql": "SELECT 1", "database_type": "sqlite"})
    assert events[0].sql_query["server_version"].startswith("3.")
    assert Metadata()["frameworks"] == [{"name": "Django", "version": django.get_version()}]


# Recording is enabled as a side-effect of requesting the events fixture. There's probably a better
# way, but leave it here for now.
@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_framework_metadata(client, events):  # pylint: disable=unused-argument
    client.get("/")
    assert Metadata()["frameworks"] == [{"name": "Django", "version": django.get_version()}]


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_app_can_read_body(client):
    response = client.post("/echo", json={"test": "json"})
    assert response.content == b'{"test": "json"}'


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_template(events):
    render_to_string("hello_world.html")
    assert events[0].to_dict() == DictIncluding(
        {
            "path": "_appmap/test/data/django/app/hello_world.html",
            "event": "call",
            "defined_class": "<templates>._AppmapTestDataDjangoAppHello_WorldHtml",
            "method_id": "render",
            "static": False,
        }
    )


# pylint: disable=arguments-differ
class ClientAdaptor(django.test.Client):
    """Adaptor for the client request parameters used in .web_framework tests."""

    # pylint: disable=too-many-arguments
    def generic(
        self,
        method,
        path,
        data="",
        content_type="application/octet-stream",
        secure=False,
        headers=None,
        json=None,
        **kwargs,
    ):
        headers = {"HTTP_" + k.replace("-", "_").upper(): v for k, v in (headers or {}).items()}

        if json:
            content_type = "application/json"
            data = self._encode_json(json, "application/json")

        return super().generic(method, path, data, content_type, secure, **headers, **kwargs)

    def post(self, path, data=None, content_type=MULTIPART_CONTENT, secure=False, **extra):
        if content_type == "multipart/form-data":
            content_type = MULTIPART_CONTENT
        return super().post(path, data, content_type, secure, **extra)


@pytest.fixture
def client(settings):
    # We might be able to set DEBUG in the app's settings. But, using the settings fixture here
    # ensures that all the settings (esp MIDDLEWARE) will be reset before each test run.
    settings.DEBUG = True
    return ClientAdaptor()


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_unnamed(client, events):
    client.get("/post/unnamed/5")

    assert appmap.enabled()  # sanity check
    # unnamed captures in a re_path don't show up in the event's
    # message attribute.
    assert len(events[0].message) == 0


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_included_view(client, events):
    client.get("/post/included/test_user")

    assert len(events) == 2
    assert events[0].http_server_request == DictIncluding(
        {
            "path_info": "/post/included/test_user",
            "normalized_path_info": "/post/included/{username}",
        }
    )


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_exception(client, events, monkeypatch):
    def raise_on_call(*args):
        raise RuntimeError("An error")

    monkeypatch.setattr(django.core.handlers.exception, "response_for_exception", raise_on_call)

    with pytest.raises(RuntimeError):
        client.get("/exception")

    assert events[0].http_server_request == DictIncluding(
        {"request_method": "GET", "path_info": "/exception", "protocol": "HTTP/1.1"}
    )

    assert events[1].parent_id == events[0].id
    assert events[1].exceptions == [
        DictIncluding({"class": "builtins.RuntimeError", "message": "An error"})
    ]


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_deeply_nested_routes(client, events):
    client.get("/admincp/permissions/edit/1")

    assert len(events) == 2
    assert events[0].http_server_request == DictIncluding(
        {"normalized_path_info": "/admincp/permissions/edit/{pk}"}
    )


class TestDjangoApp:
    """
    Run the tests in the fixture app. These depend on being able to manipulate the app's config in
    ways that are difficult to do from here.
    """

    @pytest.fixture(autouse=True)
    def beforeEach(self, monkeypatch, pytester):
        monkeypatch.setenv("PYTHONPATH", "init")
        pytester.copy_example("django")

    def test_enabled(self, pytester):
        # To really check middleware reset, the tests must run in order,
        # so disable randomly.
        result = pytester.runpytest("-svv", "-p", "no:randomly")
        result.assert_outcomes(passed=4, failed=0, errors=0)
        # Look for the http_server_request event in test_app's appmap. If
        # middleware reset is broken, it won't be there.
        appmap_file = pytester.path / "tmp" / "appmap" / "pytest" / "test_request.appmap.json"
        assert not os.path.exists(pytester.path / "tmp" / "appmap" / "requests")

        events = json.loads(appmap_file.read_text())["events"]
        assert "http_server_request" in events[0]

    def test_disabled(self, pytester, monkeypatch):
        monkeypatch.setenv("APPMAP", "false")
        result = pytester.runpytest("-svv", "-p", "no:randomly", "-k", "test_request")
        result.assert_outcomes(passed=1, failed=0, errors=0)
        assert not (pytester.path / "tmp").exists()


class TestRecordRequestsDjango(_TestRecordRequests):
    def server_start_thread(self, debug=True):
        # Use appmap from our working copy, not the module installed by virtualenv. Add the init
        # directory so the sitecustomize.py file it contains will be loaded on startup. This
        # simulates a real installation.
        settings = "settings_dev" if debug else "settings"
        exec_cmd(
            """
export PYTHONPATH="$PWD"

cd _appmap/test/data/django/
PYTHONPATH="$PYTHONPATH:$PWD/init"
"""
            + f" APPMAP_OUTPUT_DIR=/tmp DJANGO_SETTINGS_MODULE=app.{settings}"
            + " python manage.py runserver"
            + f" 127.0.0.1:{_TestRecordRequests.server_port}"
        )

    def server_start(self, debug=True):
        def start_with_debug():
            self.server_start_thread(debug)

        # start as background thread so running the tests can continue
        thread = Thread(target=start_with_debug)
        thread.start()
        wait_until_port_is("127.0.0.1", _TestRecordRequests.server_port, "open")

    def server_stop(self):
        exec_cmd(
            "ps -ef"
            + "| grep -i 'manage.py runserver'"
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
