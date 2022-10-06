"""HTTP client request and response capture.

Importing this module patches http.client.HTTPConnection to record
appmap events of any HTTP requests.
"""

import time
from http.client import HTTPConnection
from urllib.parse import parse_qs, urlsplit

from ._implementation.event import HttpClientRequestEvent, HttpClientResponseEvent
from ._implementation.recorder import Recorder
from ._implementation.utils import patch_class, values_dict


def is_secure(self: HTTPConnection):
    """Checks whether HTTP connection is secure."""
    # isinstance(self, HTTPSConnection) won't work with
    # eg. urllib3 HTTPConnection. Instead try duck typing.
    return hasattr(self, "key_file")


def base_url(self: HTTPConnection):
    """Extract base URL from an HTTPConnection.

    Example result: https://appmap.example:3000
    """
    scheme = "https" if is_secure(self) else "http"
    port = "" if self.port == self.default_port else f":{self.port}"
    return f"{scheme}://{self.host}{port}"


# pylint: disable=missing-function-docstring
@patch_class(HTTPConnection)
class HTTPConnectionPatch:
    """Patch methods for HTTPConnection, building and recording appmap events
    as requests are issues and responses received.
    """

    # pylint: disable=attribute-defined-outside-init
    def putrequest(self, orig, method, url, *args, **kwargs):
        split = urlsplit(url)
        self._appmap_request = HttpClientRequestEvent(
            method,
            base_url(self) + split.path,
            values_dict(parse_qs(split.query).items()),
        )
        orig(self, method, url, *args, **kwargs)

    def putheader(self, orig, header, *values):
        request = self._appmap_request.http_client_request
        if not hasattr(request, "headers"):
            request["headers"] = {}
        headers = request["headers"]
        if not header in headers:
            headers[header] = []
        headers[header].extend(values)
        orig(self, header, *values)

    def getresponse(self, orig):
        event = self._appmap_request
        del self._appmap_request
        request = event.http_client_request
        if "headers" in request:
            request["headers"] = values_dict(request["headers"].items())

        enabled = Recorder.get_enabled()
        if enabled:
            Recorder.add_event(event)

        start = time.monotonic()
        response = orig(self)

        if enabled:
            Recorder.add_event(
                HttpClientResponseEvent(
                    response.status,
                    headers=response.headers,
                    elapsed=(time.monotonic() - start),
                    parent_id=event.id,
                )
            )

        return response
