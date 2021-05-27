"""Django integration. Captures HTTP requests and SQL queries.

Automatically used in pytest tests. To enable remote recording,
add appmap.django.Middleware to MIDDLEWARE in your app configuration
and run with APPMAP=true set in the environment.
"""

import django
from django.core.handlers.base import BaseHandler
from django.conf import settings
from django.db.backends.utils import CursorDebugWrapper
from django.db.backends.signals import connection_created
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.urls import resolve
from django.urls.resolvers import _route_to_regex

import time
import json
import re

from appmap._implementation import generation
from appmap._implementation.env import Env
from appmap._implementation.event import \
    SqlEvent, ReturnEvent, HttpServerRequestEvent, HttpServerResponseEvent
from appmap._implementation.instrument import is_instrumentation_disabled
from ._implementation.metadata import Metadata
from appmap._implementation.recording import Recorder
from ._implementation.utils import values_dict


def parse_pg_version(version):
    """Transform postgres version number like 120005 to a tuple like 12.0.5."""
    return (version // 10000 % 100, version // 100 % 100, version % 100)


def database_version(connection):
    """Examine a database connection and try to establish the backend version."""
    vendor = connection.vendor
    if vendor == 'sqlite':
        return connection.Database.sqlite_version_info
    if vendor == 'mysql':
        return connection.mysql_version
    if vendor == 'postgresql':
        return parse_pg_version(connection.pg_version)
    if vendor == 'oracle':
        return connection.oracle_version
    return None


def add_metadata():
    """Adds Django framework to metadata for the next appmap generation."""
    Metadata.add_framework('Django', django.get_version())


class ExecuteWrapper:
    def __init__(self):
        self.recorder = Recorder()

    def __call__(self, execute, sql, params, many, context):
        start = time.monotonic()
        try:
            return execute(sql, params, many, context)
        finally:
            if is_instrumentation_disabled():
                # We must be in the middle of fetching object representation.
                # Don't record this query in the appmap.
                pass
            elif self.recorder.enabled:
                add_metadata()
                stop = time.monotonic()
                duration = stop - start
                conn = context['connection']
                # Note this logic is based on django.db.backends.utils.CursorDebugWrapper.
                if many:
                    # Sometimes the same query is executed with different parameter sets.
                    # Instead of substituting them all, just say how many times it was run.
                    try:
                        times = len(params)
                    except TypeError:
                        times = '?'
                    sql = '%s times %s' % (times, sql)
                else:
                    cursor = context['cursor']
                    sql = conn.ops.last_executed_query(cursor, sql, params)
                call_event = SqlEvent(sql, vendor=conn.vendor, version=database_version(conn))
                self.recorder.add_event(call_event)
                return_event = ReturnEvent(parent_id=call_event.id, elapsed=duration)
                self.recorder.add_event(return_event)


# CursorDebugWrapper is used in tests to capture and examine queries.
# However, recording appmap can cause additional queries to run when fetching
# object representation. Make sure tests don't see these queries.

original_execute = CursorDebugWrapper.execute

def wrapped_execute(self, sql, params=None):
    """Directly execute the query if instrumentation is temporarily
    disabled, to avoid capturing queries not issued by the application."""
    if is_instrumentation_disabled():
        return super().execute(sql, params)
    return original_execute(self, sql, params)

CursorDebugWrapper.execute = wrapped_execute


@receiver(connection_created)
def connected(sender, connection, **_):
    # pylint: disable=unused-argument
    wrappers = connection.execute_wrappers
    if not any(isinstance(x, ExecuteWrapper) for x in wrappers):
        wrappers.append(ExecuteWrapper())


def request_params(request):
    """Extract request parameters as a dict.

    Parses query and form data and JSON request body.
    Multiple parameter values are represented as lists."""
    params = request.GET.copy()
    params.update(request.POST)

    if request.content_type == 'application/json':
        try:
            # Note: it's important to use request.body here instead of
            # directly reading request. This way the application can still
            # access the body which is now cached in the request object.
            params.update(json.loads(request.body))
        except (json.decoder.JSONDecodeError, AttributeError):
            pass  # invalid json or not an object

    return values_dict(params.lists())

def normalize_path_info(path_info, resolved):
    # Prior to django 3.2, there doesn't appear to be a good way to
    # determine whether the pattern that matched a request was a path
    # or a re_path. To figure it out, just try to use the route as a
    # regex. If that fails, assume it's a path, and use django's
    # internal parser to turn it into a regex.
    regex = resolved.route
    match = re.match(regex, path_info[1:])
    if not match:
        regex = _route_to_regex(resolved.route)[0]
        match = re.match(regex, path_info[1:])

    # Compile the regex so we can see what groups it contains.
    groups = re.compile(regex).groupindex
    if len(groups) == 0:
        # No named groups means no parameters to normalize.
        return path_info

    # For each parameter, insert the portion of the path that
    # precedes, followed by the name of the parameter.
    np = '/'
    pos = 0
    for i,g in enumerate(groups):
        np += match.string[pos:match.start(i+1)]
        np += f'{{{g}}}'
        pos = match.end(i+1)

    # Finally, append anything remaining in the path
    np += match.string[pos:]
    return np

class Middleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.recorder = Recorder()

    def __call__(self, request):
        if Env.current.enabled and request.path_info == '/_appmap/record':
            return self.recording(request)
        if self.recorder.enabled:
            add_metadata()
            start = time.monotonic()
            resolved = resolve(request.path_info)
            params = request_params(request)
            params.update(resolved.kwargs)
            call_event = HttpServerRequestEvent(
                request_method=request.method,
                path_info=request.path_info,
                message_parameters=params,
                normalized_path_info=normalize_path_info(request.path_info, resolved),
                protocol=request.META['SERVER_PROTOCOL'],
                headers=request.headers
            )
            self.recorder.add_event(call_event)

        response = self.get_response(request)

        if self.recorder.enabled:
            duration = time.monotonic() - start
            return_event = HttpServerResponseEvent(
                parent_id=call_event.id,
                elapsed=duration,
                status_code=response.status_code,
                headers=dict(response.items())
            )
            self.recorder.add_event(return_event)

        return response

    def recording(self, request):
        """Handle recording requests."""
        if request.method == 'GET':
            return JsonResponse({'enabled': self.recorder.enabled})
        if request.method == 'POST':
            if self.recorder.enabled:
                return HttpResponse('Recording is already in progress', status=409)
            self.recorder.clear()
            self.recorder.start_recording()
            return HttpResponse()

        if request.method == 'DELETE':
            if not self.recorder.enabled:
                return HttpResponse('No recording is in progress', status=404)

            self.recorder.stop_recording()
            return HttpResponse(
                generation.dump(self.recorder),
                content_type='application/json'
            )


        return HttpResponseBadRequest()


def inject_middleware():
    """Make sure AppMap middleware is added to the stack"""
    if 'appmap.django.Middleware' not in settings.MIDDLEWARE:
        settings.MIDDLEWARE.insert(0, 'appmap.django.Middleware')


original_load_middleware = BaseHandler.load_middleware


def load_middleware(*args, **kwargs):
    """Patched wrapper to inject AppMap middleware first"""
    inject_middleware()
    BaseHandler.load_middleware = original_load_middleware
    return original_load_middleware(*args, **kwargs)


BaseHandler.load_middleware = load_middleware
