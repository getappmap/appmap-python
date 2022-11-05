"""
This file contains Django middleware that can be inserted into an app's stack to expose the remote
recording endpoint.

It expects the importer to have verified that Django is available.
"""

from http import HTTPStatus

from django.http import HttpRequest, HttpResponse

from . import remote_recording


class RemoteRecording:  # pylint: disable=missing-class-docstring
    def __init__(self, get_response):
        super().__init__()
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.path != "/_appmap/record":
            return self.get_response(request)

        handlers = {
            "GET": remote_recording.status,
            "POST": remote_recording.start,
            "DELETE": remote_recording.stop,
        }

        def not_allowed():
            return "", HTTPStatus.METHOD_NOT_ALLOWED

        body, status = handlers.get(request.method, not_allowed)()
        return HttpResponse(body, status=status, content_type="application/json")
