"""Common tests for web frameworks such as django and flask."""
# pylint: disable=missing-function-docstring

import concurrent.futures
import json
import multiprocessing
import os
import time
import traceback
from os.path import exists
from random import SystemRandom

import pytest
import requests

import appmap
from _appmap.env import Env

from ..test.helpers import DictIncluding, HeadersIncluding
from .normalize import normalize_appmap

TEST_HOST = "127.0.0.1"
TEST_PORT = 8000

_SR = SystemRandom()


def content_type(res):
    # headers attribute is available in Flask, and in Django as of
    # 3.2. For Django 2.2, headers are accessed from the response
    # directly.
    getter = res.headers.get if hasattr(res, "headers") else res.get
    return getter("Content-Type")


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
class _TestFormData:
    @staticmethod
    @pytest.mark.parametrize("bad_json", ["bad json", 1, False, None, [2, 3]])
    def test_post_bad_json(events, client, bad_json):
        client.post(
            "/test?my_param=example",
            data=str(bad_json),
            content_type="application/json",
        )

        assert events[0].message == [
            DictIncluding({"name": "my_param", "class": "builtins.str", "value": "'example'"})
        ]

    @staticmethod
    def test_post_multipart(events, client):
        client.post("/test", data={"my_param": "example"}, content_type="multipart/form-data")

        assert events[0].message == [
            DictIncluding({"name": "my_param", "class": "builtins.str", "value": "'example'"})
        ]


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
class _TestRequestCapture:
    """Common tests for HTTP server request and response capture."""

    @staticmethod
    def test_http_capture(client, events):
        """Test GET request and response capture."""
        client.get("/test")

        assert events[0].http_server_request == DictIncluding(
            {"request_method": "GET", "path_info": "/test", "protocol": "HTTP/1.1"}
        )

        response = events[1].http_server_response
        assert response == DictIncluding(
            {"status_code": 200, "mime_type": "text/html; charset=utf-8"}
        )

        assert "etag" in map(str.lower, response["headers"].keys())

    @staticmethod
    def test_http_capture_post(client, events):
        """Test POST request with JSON body capture."""
        client.post(
            "/test",
            json={"my_param": "example"},
            headers={
                "Authorization": 'token "test-token"',
                "Accept": "application/json",
                "Accept-Language": "pl",
            },
        )

        assert events[0].http_server_request == DictIncluding(
            {
                "request_method": "POST",
                "path_info": "/test",
                "protocol": "HTTP/1.1",
                "authorization": 'token "test-token"',
                "mime_type": "application/json",
            }
        )

        assert events[0].http_server_request["headers"] == HeadersIncluding(
            {"Accept": "application/json", "Accept-Language": "pl"}
        )

    @staticmethod
    def test_post(events, client):
        client.post(
            "/test",
            json={"my_param": "example"},
            headers={
                "Authorization": 'token "test-token"',
                "Accept": "application/json",
                "Accept-Language": "pl",
                "Content-Type": "application/json; charset=UTF-8",
            },
        )

        assert events[0].message == [
            DictIncluding(
                {"name": "my_param", "class": "builtins.str", "value": "'example'"}
            )
        ]
        assert events[0].http_server_request == DictIncluding(
            {
                "request_method": "POST",
                "path_info": "/test",
                "protocol": "HTTP/1.1",
                "authorization": 'token "test-token"',
                "mime_type": "application/json; charset=UTF-8",
            }
        )

        assert events[0].http_server_request["headers"] == HeadersIncluding(
            {"Accept": "application/json", "Accept-Language": "pl"}
        )

    @staticmethod
    def test_get(events, client):
        client.get("/test?my_param=example")

        assert events[0].message == [
            DictIncluding(
                {"name": "my_param", "class": "builtins.str", "value": "'example'"}
            )
        ]

    @staticmethod
    def test_get_arr(events, client):
        client.get("/test?my_param=example&my_param=example2")

        assert events[0].message == [
            DictIncluding(
                {
                    "name": "my_param",
                    "class": "builtins.list",
                    "value": "['example', 'example2']",
                }
            ),
        ]

    @staticmethod
    def test_put(events, client):
        client.put("/test", json={"my_param": "example"})

        assert events[0].message == [
            DictIncluding(
                {"name": "my_param", "class": "builtins.str", "value": "'example'"}
            )
        ]

    @staticmethod
    def test_post_with_query(events, client):
        client.post("/test?my_param=get&my_param=an", json={"my_param": "example"})

        assert events[0].message == [
            DictIncluding(
                {
                    "name": "my_param",
                    "class": "builtins.list",
                    "value": "['get', 'an', 'example']",
                }
            )
        ]

    @staticmethod
    @pytest.mark.parametrize(
        "url,expected",
        [
            ("/user/test_user", "/user/{username}"),
            ("/post/123", "/post/{post_id}"),
            ("/post/test_user/123/summary", "/post/{username}/{post_id}/summary"),
            ("/123/posts/test_user", "/{org}/posts/{username}"),
        ],
    )
    def test_path_normalization(client, events, url, expected):
        client.get(url)
        np = events[0].http_server_request["normalized_path_info"]
        assert np == expected

    @staticmethod
    def test_message_path_segments(events, client):
        client.get("/post/alice/42/summary")

        assert events[0].message == [
            DictIncluding(
                {"name": "username", "class": "builtins.str", "value": "'alice'"}
            ),
            DictIncluding({"name": "post_id", "class": "builtins.int", "value": "42"}),
        ]


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
class _TestFormCapture:
    @staticmethod
    def test_post_form_urlencoded(events, client):
        client.post(
            "/test",
            data="my_param=example",
            content_type="application/x-www-form-urlencoded",
        )

        assert events[0].message == [
            DictIncluding({"name": "my_param", "class": "builtins.str", "value": "'example'"})
        ]

    @staticmethod
    def test_post_multipart(events, client):
        client.post("/test", data={"my_param": "example"}, content_type="multipart/form-data")

        assert events[0].message == [
            DictIncluding({"name": "my_param", "class": "builtins.str", "value": "'example'"})
        ]


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
class _TestRemoteRecording:
    """Common tests for remote recording."""

    @property
    def expected_content_type(self):
        return self._expected_content_type

    @expected_content_type.setter
    def expected_content_type(self, value):
        self._expected_content_type = value

    def setup_method(self):
        self.expected_content_type = "text/html; charset=utf-8"

    @staticmethod
    # since APPMAP records by default, disable it explicitly
    @pytest.mark.appmap_enabled(appmap_enabled=False)
    def test_appmap_disabled(client):
        assert not appmap.enabled()
        assert not Env.current.enables("remote")

        res = client.get("/_appmap/record")
        assert res.status_code == 404

    @staticmethod
    def test_starts_disabled(client):
        res = client.get("/_appmap/record")
        assert res.status_code == 200

        assert content_type(res) == "application/json"

        data = res.json
        if callable(data):
            data = data()
        assert data == {"enabled": False}

    @staticmethod
    def test_can_be_enabled(client):
        res = client.post("/_appmap/record")
        assert res.status_code == 200

    @staticmethod
    def test_can_only_enable_once(client):
        res = client.post("/_appmap/record")
        assert res.status_code == 200
        res = client.post("/_appmap/record")
        assert res.status_code == 409

    def test_can_record(self, data_dir, client):
        res = client.post("/_appmap/record")
        assert res.status_code == 200

        res = client.get("/")
        assert res.status_code == 200
        assert res.headers["content-type"] == self.expected_content_type

        res = client.get("/user/test_user")
        assert res.status_code == 200
        assert res.headers["content-type"] == self.expected_content_type

        res = client.delete("/_appmap/record")
        assert res.status_code == 200
        assert content_type(res) == "application/json"
        data = res.data if hasattr(res, "data") else res.content
        generated_appmap = normalize_appmap(data)

        for evt in generated_appmap["events"]:
            # Strip out thread id. The values for these vary by framework, and
            # may not even be the same within an AppMap (e.g. FastAPI). They
            # should always be ints, though
            if "thread_id" in evt:
                value = evt.pop("thread_id")
                assert isinstance(value, int)

            # Check mime_type. These also vary by framework, but will be
            # consistent within an AppMap.
            if "http_server_response" in evt:
                actual_content_type = evt["http_server_response"].pop("mime_type")
                assert actual_content_type == self.expected_content_type

        expected_path = data_dir / "remote.appmap.json"
        with open(expected_path, encoding="utf-8") as expected:
            expected_appmap = json.load(expected)

        assert generated_appmap == expected_appmap, f"expected appmap path {expected_path}"
        res = client.delete("/_appmap/record")
        assert res.status_code == 404

class _TestRecordRequests:
    """Common tests for per-requests recording (record requests.)"""

    @classmethod
    def server_url(cls):
        return f"http://{TEST_HOST}:{TEST_PORT}"

    @classmethod
    def record_request_thread(cls):
        # I've seen occasional test failures, seemingly because the test servers can't handle the
        # barrage of requests. A tiny bit of delay still causes many, many concurrent requests, but
        # eliminates the failures.
        time.sleep(_SR.uniform(0, 0.1))
        return requests.get(cls.server_url() + "/test", timeout=30)

    def record_requests(self, record_remote):
        # pylint: disable=too-many-locals
        if record_remote:
            # when remote recording is enabled, this test also
            # verifies the global recorder doesn't save duplicate
            # events when per-request recording is enabled
            response = requests.post(self.server_url() + "/_appmap/record", timeout=30)
            assert response.status_code == 200

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=multiprocessing.cpu_count()
        ) as executor:
            # start all threads
            max_number_of_threads = 400
            future_to_request_number = {}
            for n in range(max_number_of_threads):
                future = executor.submit(self.record_request_thread)
                future_to_request_number[future] = n

            # wait for all threads to complete
            for future in concurrent.futures.as_completed(future_to_request_number):
                try:
                    response = future.result()
                except Exception:  # pylint: disable=broad-except
                    traceback.print_exc()
                assert response.status_code == 200

                if hasattr(response, "content"):
                    # django uses response.content
                    assert response.content == b"testing"
                else:
                    # flask  uses response.get_data
                    assert response.get_data() == b"testing"

                if hasattr(response, "headers"):
                    assert "AppMap-File-Name" in response.headers
                    appmap_file_name = response.headers["AppMap-File-Name"]
                else:
                    # response.headers doesn't exist in Django 2.2
                    assert "AppMap-File-Name" in response
                    appmap_file_name = response["AppMap-File-Name"]
                assert exists(appmap_file_name)
                appmap_file_name_basename = appmap_file_name.split("/")[-1]
                appmap_file_name_basename_part = "_".join(
                    appmap_file_name_basename.split("_")[2:]
                )
                assert (
                    appmap_file_name_basename_part
                    == "http_127_0_0_1_8000_test.appmap.json"
                )

                with open(appmap_file_name, encoding="utf-8") as f:
                    recording = json.loads(f.read())

                    # Every event should come from the same thread
                    thread_ids = {
                        event["thread_id"]: True for event in recording["events"]
                    }
                    assert len(thread_ids) == 1

                    # AppMap should contain only one request and response
                    http_server_requests = [
                        event for event in recording["events"] if "http_server_request" in event
                    ]
                    http_server_responses = [
                        event for event in recording["events"] if "http_server_response" in event
                    ]
                    assert len(http_server_requests) == 1
                    assert len(http_server_responses) == 1
                    assert http_server_responses[0]["parent_id"] == http_server_requests[0]["id"]

                os.remove(appmap_file_name)

    @pytest.mark.appmap_enabled
    @pytest.mark.server(debug=True)
    def test_record_requests_with_remote(self, server):
        self.record_requests(server.debug)

    @pytest.mark.appmap_enabled
    @pytest.mark.server(debug=False)
    def test_record_requests_without_remote(self, server):
        self.record_requests(server.debug)

    @pytest.mark.server(debug=False)
    def test_remote_disabled_in_prod(self, server):
        response = requests.get(server.url + "/_appmap/record", timeout=30)
        assert response.status_code == 404

    @pytest.mark.server(debug=False, env={"APPMAP_RECORD_REMOTE": "true"})
    @pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REMOTE": "true"})
    def test_remote_enabled_in_prod(self, server):
        response = requests.get(server.url + "/_appmap/record", timeout=30)
        assert response.status_code == 200
