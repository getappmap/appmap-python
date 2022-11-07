# flake8: noqa: E402
# pylint: disable=missing-function-docstring,redefined-outer-name

import json
import sys
from pathlib import Path
from threading import Thread

import django
import django.conf
import django.core.handlers.exception
import django.db
import django.http
import django.test
import pytest
from django.template.loader import render_to_string
from django.test.client import MULTIPART_CONTENT

import appmap
import appmap.django  # noqa: F401
from appmap.test.helpers import DictIncluding

from .._implementation.metadata import Metadata
from .web_framework import TestRecordRequests, exec_cmd, wait_until_port_is

sys.path += [str(Path(__file__).parent / "data" / "django")]

# Import app just for the side-effects. It must happen after sys.path has been modified.
import app  # pyright: ignore pylint: disable=import-error, unused-import,wrong-import-order

# Make sure assertions in web_framework get rewritten (e.g. to show
# diffs in generated appmaps)
pytest.register_assert_rewrite("appmap.test.web_framework")


@pytest.mark.django_db
def test_sql_capture(events, monkeypatch):
    monkeypatch.setenv("APPMAP", "false")
    conn = django.db.connections["default"]
    conn.cursor().execute("SELECT 1").fetchall()
    assert events[0].sql_query == DictIncluding(
        {"sql": "SELECT 1", "database_type": "sqlite"}
    )
    assert events[0].sql_query["server_version"].startswith("3.")
    assert Metadata()["frameworks"] == [
        {"name": "Django", "version": django.get_version()}
    ]


@pytest.mark.appmap_enabled
def test_framework_metadata(
    client, events, monkeypatch
):  # pylint: disable=unused-argument
    monkeypatch.setenv("APPMAP_RECORD_REQUESTS", "false")
    client.get("/")
    assert Metadata()["frameworks"] == [
        {"name": "Django", "version": django.get_version()}
    ]


@pytest.mark.appmap_enabled
def test_app_can_read_body(
    client, events, monkeypatch
):  # pylint: disable=unused-argument
    monkeypatch.setenv("APPMAP_RECORD_REQUESTS", "false")
    response = client.post("/echo", json={"test": "json"})
    assert response.content == b'{"test": "json"}'


@pytest.mark.appmap_enabled
def test_template(events, monkeypatch):
    monkeypatch.setenv("APPMAP_RECORD_REQUESTS", "false")
    render_to_string("hello_world.html")
    assert events[0].to_dict() == DictIncluding(
        {
            "path": "appmap/test/data/django/app/hello_world.html",
            "event": "call",
            "defined_class": "<templates>.AppmapTestDataDjangoAppHello_WorldHtml",
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
        **kwargs
    ):
        headers = {
            "HTTP_" + k.replace("-", "_").upper(): v for k, v in (headers or {}).items()
        }

        if json:
            content_type = "application/json"
            data = self._encode_json(json, "application/json")

        return super().generic(
            method, path, data, content_type, secure, **headers, **kwargs
        )

    def post(
        self, path, data=None, content_type=MULTIPART_CONTENT, secure=False, **extra
    ):
        if content_type == "multipart/form-data":
            content_type = MULTIPART_CONTENT
        return super().post(path, data, content_type, secure, **extra)


@pytest.fixture
def client():
    return ClientAdaptor()


@pytest.mark.appmap_enabled
def test_unnamed(client, events, monkeypatch):
    monkeypatch.setenv("APPMAP_RECORD_REQUESTS", "false")
    client.get("/post/unnamed/5")

    assert appmap.enabled()  # sanity check
    # unnamed captures in a re_path don't show up in the event's
    # message attribute.
    assert len(events[0].message) == 0


@pytest.mark.appmap_enabled
def test_included_view(client, events, monkeypatch):
    monkeypatch.setenv("APPMAP_RECORD_REQUESTS", "false")
    client.get("/post/included/test_user")

    assert len(events) == 2
    assert events[0].http_server_request == DictIncluding(
        {
            "path_info": "/post/included/test_user",
            "normalized_path_info": "/post/included/{username}",
        }
    )


@pytest.mark.appmap_enabled
def test_exception(client, events, monkeypatch):
    monkeypatch.setenv("APPMAP_RECORD_REQUESTS", "false")

    def raise_on_call(*args):
        raise RuntimeError("An error")

    monkeypatch.setattr(
        django.core.handlers.exception, "response_for_exception", raise_on_call
    )

    with pytest.raises(RuntimeError):
        client.get("/exception")

    assert events[0].http_server_request == DictIncluding(
        {"request_method": "GET", "path_info": "/exception", "protocol": "HTTP/1.1"}
    )

    assert events[1].parent_id == events[0].id
    assert events[1].exceptions == [
        DictIncluding({"class": "builtins.RuntimeError", "message": "An error"})
    ]


@pytest.mark.appmap_enabled
def test_deeply_nested_routes(client, events, monkeypatch):
    monkeypatch.setenv("APPMAP_RECORD_REQUESTS", "false")
    client.get("/admincp/permissions/edit/1")

    assert len(events) == 2
    assert events[0].http_server_request == DictIncluding(
        {"normalized_path_info": "/admincp/permissions/edit/{pk}"}
    )


def test_middleware_reset(pytester, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "init")
    monkeypatch.setenv("APPMAP", "true")

    pytester.copy_example("django")

    # To really check middleware reset, the tests must run in order,
    # so disable randomly.
    pytester.runpytest("-svv", "-p", "no:randomly")

    # Look for the http_server_request event in test_app's appmap. If
    # middleware reset is broken, it won't be there.
    appmap_file = pytester.path / "tmp" / "appmap" / "pytest" / "test_app.appmap.json"
    events = json.loads(appmap_file.read_text())["events"]
    assert "http_server_request" in events[0]


class TestRecordRequestsDjango(TestRecordRequests):
    @staticmethod
    def server_start_thread(env_vars_str):
        # Use appmap from our working copy, not the module installed by virtualenv. Add the init
        # directory so the sitecustomize.py file it contains will be loaded on startup. This
        # simulates a real installation.
        exec_cmd(
            """
export PYTHONPATH="$PWD"

cd appmap/test/data/django/
PYTHONPATH="$PYTHONPATH:$PWD/init"
"""
            + env_vars_str
            + """ APPMAP_OUTPUT_DIR=/tmp  python manage.py runserver 127.0.0.1:"""
            + str(TestRecordRequests.server_port)
        )

    @staticmethod
    def server_start(env_vars_str):
        # start as background thread so running the tests can continue
        thread = Thread(
            target=TestRecordRequestsDjango.server_start_thread, args=(env_vars_str,)
        )
        thread.start()
        wait_until_port_is("127.0.0.1", TestRecordRequests.server_port, "open")

    @staticmethod
    def server_stop():
        exec_cmd(
            "ps -ef"
            + "| grep -i 'manage.py runserver'"
            + "| grep -v grep"
            + "| awk '{ print $2 }'"
            + "| xargs kill -9"
        )
        wait_until_port_is("127.0.0.1", TestRecordRequests.server_port, "closed")

    def test_record_request_appmap_enabled_requests_enabled_no_remote(client, events):
        TestRecordRequestsDjango.server_stop()  # ensure it's not running
        TestRecordRequestsDjango.server_start("APPMAP=true APPMAP_RECORD_REQUESTS=true")
        TestRecordRequests.record_request(client, events, False)
        TestRecordRequestsDjango.server_stop()

    def test_record_request_appmap_enabled_requests_enabled_and_remote(client, events):
        TestRecordRequestsDjango.server_stop()  # ensure it's not running
        TestRecordRequestsDjango.server_start("APPMAP=true APPMAP_RECORD_REQUESTS=true")
        TestRecordRequests.record_request(client, events, True)
        TestRecordRequestsDjango.server_stop()

    # not enabled means APPMAP isn't set.  This isn't the same as APPMAP=false.
    def test_record_request_appmap_not_enabled_requests_enabled_no_remote(
        client, events
    ):
        TestRecordRequestsDjango.server_stop()  # ensure it's not running
        TestRecordRequestsDjango.server_start("APPMAP_RECORD_REQUESTS=true")
        TestRecordRequests.record_request(client, events, False)
        TestRecordRequestsDjango.server_stop()

    # it's not possible to test for
    # appmap_not_enabled_requests_enabled_and_remote because when
    # APPMAP=false the routes for remote recording are disabled.
