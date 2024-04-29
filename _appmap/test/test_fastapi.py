import importlib
from importlib.metadata import version
from types import SimpleNamespace as NS

import pytest
from fastapi.testclient import TestClient

import appmap
from _appmap.env import Env
from _appmap.metadata import Metadata

from .web_framework import (
    _TestRecordRequests,
    _TestRemoteRecording,
    _TestRequestCapture,
)


# Opt in to these tests. (I couldn't find a way to DRY this up that allowed
# pytest collection to find all these tests.)
class TestRecordRequests(_TestRecordRequests):
    pass


@pytest.mark.app(remote_enabled=True)
class TestRemoteRecording(_TestRemoteRecording):
    def setup_method(self):
        self.expected_thread_id = 1
        self.expected_content_type = "application/json"


class TestRequestCapture(_TestRequestCapture):
    pass


@pytest.fixture(name="app")
def fastapi_app(data_dir, monkeypatch, request):
    monkeypatch.syspath_prepend(data_dir / "fastapi")

    Env.current.set("APPMAP_CONFIG", data_dir / "fastapi" / "appmap.yml")

    from fastapiapp import main  # pyright: ignore[reportMissingImports]

    importlib.reload(main)

    # FastAPI doesn't provide a way to say what environment the app is running
    # in. So, instead use a mark to indicate whether remote recording should be
    # enabled. (When we're running as part of a server integration, we infer the
    # environment from the server configure, e.g. "uvicorn --reload".)
    mark = request.node.get_closest_marker("app")
    remote_enabled = None
    if mark is not None:
        remote_enabled = mark.kwargs.get("remote_enabled", None)

    # Add the FastAPI middleware to the app. This now happens automatically when
    # a FastAPI app is started from uvicorn, but must be done manually
    # otherwise.
    return appmap.fastapi.Middleware(main.app, remote_enabled).init_app()


@pytest.fixture(name="client")
def fastapi_client(app):
    yield TestClient(app, headers={})


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
def test_framework_metadata(client, events):  # pylint: disable=unused-argument
    client.get("/")
    assert Metadata()["frameworks"] == [{"name": "FastAPI", "version": version("fastapi")}]


@pytest.fixture(name="server")
def fastapi_server(xprocess, server_base):
    debug = server_base.debug
    host = server_base.host
    port = server_base.port
    reload = "--reload" if debug else ""

    name = "fastapi"
    pattern = f"Uvicorn running on http://{host}:{port}"
    cmd = f"-m uvicorn fastapiapp.main:app {reload} --host {host} --port {port}"
    xprocess.ensure(name, server_base.factory(name, cmd, pattern))

    url = f"http://{server_base.host}:{port}"
    yield NS(debug=debug, url=url)

    xprocess.getinfo(name).terminate()
