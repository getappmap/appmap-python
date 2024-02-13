"""Common tests for web frameworks such as django and flask."""
# pylint: disable=missing-function-docstring

import concurrent.futures
import json
import multiprocessing
import os
import socket
import subprocess
import time
import traceback
from abc import abstractmethod
from os.path import exists
from random import SystemRandom

import pytest
import requests

import appmap
from _appmap.env import Env

from ..test.helpers import DictIncluding
from .normalize import normalize_appmap

SR = SystemRandom()


def content_type(res):
    # headers attribute is available in Flask, and in Django as of
    # 3.2. For Django 2.2, headers are accessed from the response
    # directly.
    getter = res.headers.get if hasattr(res, "headers") else res.get
    return getter("Content-Type")


@pytest.mark.appmap_enabled(env={"APPMAP_RECORD_REQUESTS": "false"})
class TestRequestCapture:
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

        assert "ETag" in response["headers"]

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

        assert events[0].http_server_request["headers"] == DictIncluding(
            {"Accept": "application/json", "Accept-Language": "pl"}
        )

    @staticmethod
    def test_post(events, client):
        client.post(
            "/test",
            data=json.dumps({"my_param": "example"}),
            content_type="application/json; charset=UTF-8",
            headers={
                "Authorization": 'token "test-token"',
                "Accept": "application/json",
                "Accept-Language": "pl",
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

        assert events[0].http_server_request["headers"] == DictIncluding(
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
    def test_post_form_urlencoded(events, client):
        client.post(
            "/test",
            data="my_param=example",
            content_type="application/x-www-form-urlencoded",
        )

        assert events[0].message == [
            DictIncluding(
                {"name": "my_param", "class": "builtins.str", "value": "'example'"}
            )
        ]

    @staticmethod
    def test_put(events, client):
        client.put("/test", json={"my_param": "example"})

        assert events[0].message == [
            DictIncluding(
                {"name": "my_param", "class": "builtins.str", "value": "'example'"}
            )
        ]

    @pytest.mark.parametrize("bad_json", ["bad json", 1, False, None, [2, 3]])
    def test_post_bad_json(self, events, client, bad_json):
        client.post(
            "/test?my_param=example",
            data=str(bad_json),
            content_type="application/json",
        )

        assert events[0].message == [
            DictIncluding(
                {"name": "my_param", "class": "builtins.str", "value": "'example'"}
            )
        ]

    @staticmethod
    def test_post_multipart(events, client):
        client.post(
            "/test", data={"my_param": "example"}, content_type="multipart/form-data"
        )

        assert events[0].message == [
            DictIncluding(
                {"name": "my_param", "class": "builtins.str", "value": "'example'"}
            )
        ]

    @staticmethod
    def test_post_with_query(events, client):
        client.post("/test?my_param=get", data={"my_param": "example"})

        assert events[0].message == [
            DictIncluding(
                {
                    "name": "my_param",
                    "class": "builtins.list",
                    "value": "['get', 'example']",
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
class TestRemoteRecording:
    """Common tests for remote recording."""

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

    @staticmethod
    def test_can_record(data_dir, client):
        res = client.post("/_appmap/record")
        assert res.status_code == 200

        res = client.get("/")
        assert res.status_code == 200

        res = client.get("/user/test_user")
        assert res.status_code == 200

        res = client.delete("/_appmap/record")
        assert res.status_code == 200
        assert content_type(res) == "application/json"
        data = res.data if hasattr(res, "data") else res.content
        generated_appmap = normalize_appmap(data)

        expected_path = data_dir / "remote.appmap.json"
        with open(expected_path, encoding="utf-8") as expected:
            expected_appmap = json.load(expected)

        assert (
            generated_appmap == expected_appmap
        ), f"expected appmap path {expected_path}"

        res = client.delete("/_appmap/record")
        assert res.status_code == 404


def exec_cmd(command):
    p = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output, _ = p.communicate()
    return output.decode()


def port_state(address, port):
    ret = None
    s = socket.socket()
    try:
        s.connect((address, port))
        ret = "open"
    except Exception:  # pylint: disable=broad-except
        ret = "closed"
        s.close()
    return ret


def wait_until_port_is(address, port, desired_state):
    max_wait_seconds = 10
    sleep_time = 0.1
    max_count = 1 / sleep_time * max_wait_seconds
    count = 0
    # don't "while True" to not lock-up the testsuite if something goes wrong
    while count < max_count:
        current_state = port_state(address, port)
        if current_state == desired_state:
            break

        time.sleep(sleep_time)
        count += 1


class _TestRecordRequests:
    """Common tests for per-requests recording (record requests.)"""

    server_port = 8000

    @abstractmethod
    def server_start(self, debug=False):
        """Start the webserver in the background. Don't block execution."""

    @abstractmethod
    def server_stop(self):
        """Stop the webserver."""

    @staticmethod
    def server_url():
        return "http://127.0.0.1:" + str(_TestRecordRequests.server_port)

    @staticmethod
    def record_request_thread():
        # I've seen occasional test failures, seemingly because the test servers can't handle the
        # barrage of requests. A tiny bit of delay still causes many, many concurrent requests, but
        # eliminates the failures.
        time.sleep(SR.uniform(0, 0.1))
        return requests.get(_TestRecordRequests.server_url() + "/test", timeout=30)

    @staticmethod
    @pytest.mark.appmap_enabled
    def record_request(record_remote):
        if record_remote:
            # when remote recording is enabled, this test also
            # verifies the global recorder doesn't save duplicate
            # events when per-request recording is enabled
            response = requests.post(
                _TestRecordRequests.server_url() + "/_appmap/record", timeout=30
            )
            assert response.status_code == 200

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=multiprocessing.cpu_count()
        ) as executor:
            # start all threads
            max_number_of_threads = 400
            future_to_request_number = {}
            for n in range(max_number_of_threads):
                future = executor.submit(_TestRecordRequests.record_request_thread)
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
                    assert response.headers["AppMap-File-Name"]
                    appmap_file_name = response.headers["AppMap-File-Name"]
                else:
                    # response.headers doesn't exist in Django 2.2
                    assert response["AppMap-File-Name"]
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
                        event["http_server_request"]
                        for event in recording["events"]
                        if "http_server_request" in event
                    ]
                    http_server_responses = [
                        event["http_server_response"]
                        for event in recording["events"]
                        if "http_server_response" in event
                    ]
                    assert len(http_server_requests) == 1
                    assert len(http_server_responses) == 1

                os.remove(appmap_file_name)

    def test_remote_disabled_in_prod(self):
        self.server_stop()
        self.server_start(debug=False)
        response = requests.get(self.server_url() + "/_appmap/record", timeout=30)
        assert response.status_code == 404
        self.server_stop()

    def test_remote_enabled_in_prod(self, monkeypatch):
        self.server_stop()
        monkeypatch.setenv("APPMAP_RECORD_REMOTE", "true")
        self.server_start(debug=False)
        response = requests.get(self.server_url() + "/_appmap/record", timeout=30)
        assert response.status_code == 200
        self.server_stop()
