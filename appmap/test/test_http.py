# pylint: disable=missing-function-docstring,missing-function-docstring,missing-module-docstring
# pylint: disable=unused-argument,unused-import
import httpretty
import pytest
import requests

import appmap.http
from appmap.test.helpers import DictIncluding


def test_http_client_capture(mock_requests, events):
    requests.get("https://example.test/foo/bar?q=one&q=two&q2=%F0%9F%A6%A0")

    request = events[0]
    assert request.http_client_request == {
        "request_method": "GET",
        "url": "https://example.test/foo/bar",
        "headers": {"Connection": "keep-alive"},
    }
    message = request.message
    assert message[0] == DictIncluding({"name": "q", "value": "['one', 'two']"})
    assert (message[1] == DictIncluding({"name": "q2", "value": "'🦠'"})) or (
        message[1] == DictIncluding({"name": "q2", "value": "'\\U0001f9a0'"})
    )

    assert events[1].http_client_response == DictIncluding(
        {"status_code": 200, "mime_type": "text/plain; charset=utf-8"}
    )


@pytest.fixture(name="mock_requests")
def mock_requests_fixture():
    with httpretty.enabled(allow_net_connect=False):
        httpretty.register_uri(
            httpretty.GET, "https://example.test/foo/bar", body="hello"
        )
        yield
