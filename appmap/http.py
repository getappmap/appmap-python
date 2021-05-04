"""HTTP client request and response capture.

Importing this module patches http.client.HTTPConnection to record
appmap events of any HTTP requests.
"""

from http.client import HTTPConnection
import time
from urllib.parse import urlsplit, parse_qs

from ._implementation.event import HttpClientRequestEvent, HttpClientResponseEvent
from ._implementation.recording import Recorder
from ._implementation.utils import values_dict


def patch_class(cls):
    """Class decorator for monkey patching.

    Decorating a class (patch) with @wrap(orig) will change orig, so that
    every method defined in patch will call that implementation instead
    of the one in orig.

    The methods take the original (unbound) implementation as the
    second argument after self; the rest is passed as is.

    It's the responsibility of the wrapper method to call the original
    if appropriate, with arguments it wants (instance probably being
    the first one.
    """
    def _wrap_fun(wrapper, original):
        def wrapped(self, *args, **kwargs):
            return wrapper(self, original, *args, **kwargs)
        return wrapped
    def _wrap_cls(patch):
        for func in dir(patch):
            wrapper = getattr(patch, func)
            if callable(wrapper) and not func.startswith('__'):
                original = getattr(cls, func)
                setattr(cls, func, _wrap_fun(wrapper, original))
        return patch
    return _wrap_cls


def is_secure(self: HTTPConnection):
    """Checks whether HTTP connection is secure."""
    # isinstance(self, HTTPSConnection) won't work with
    # eg. urllib3 HTTPConnection. Instead try duck typing.
    return hasattr(self, 'key_file')


def base_url(self: HTTPConnection):
    """Extract base URL from an HTTPConnection.

    Example result: https://appmap.example:3000
    """
    scheme = 'https' if is_secure(self) else 'http'
    port = '' if self.port == self.default_port else f':{self.port}'
    return f'{scheme}://{self.host}{port}'


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
            values_dict(parse_qs(split.query).items())
        )
        orig(self, method, url, *args, **kwargs)

    def putheader(self, orig, header, *values):
        request = self._appmap_request.http_client_request
        if not hasattr(request, 'headers'):
            request['headers'] = {}
        headers = request['headers']
        if not header in headers:
            headers[header] = []
        headers[header].extend(values)
        orig(self, header, *values)

    def getresponse(self, orig):
        event = self._appmap_request
        del self._appmap_request
        request = event.http_client_request
        if 'headers' in request:
            request['headers'] = values_dict(request['headers'].items())

        recorder = Recorder()
        if recorder.enabled:
            recorder.add_event(event)

        start = time.monotonic()
        response = orig(self)

        if recorder.enabled:
            recorder.add_event(HttpClientResponseEvent(
                response.status,
                headers=response.headers,
                elapsed=(time.monotonic() - start),
                parent_id=event.id
            ))

        return response
