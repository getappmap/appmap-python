"""Django integration. Captures HTTP requests and SQL queries.

Automatically used in pytest tests. To enable remote recording,
add appmap.django.Middleware to MIDDLEWARE in your app configuration
and run with APPMAP=true set in the environment.
"""

import json
import re
import sys
import time

import django
from django.conf import settings
from django.core.handlers.base import BaseHandler
from django.db.backends.signals import connection_created
from django.db.backends.utils import CursorDebugWrapper
from django.dispatch import receiver
from django.template import Template
from django.urls import get_resolver, resolve
from django.urls.exceptions import Resolver404
from django.urls.resolvers import _route_to_regex

from appmap._implementation.detect_enabled import DetectEnabled

from ._implementation.event import (
    ExceptionEvent,
    HttpServerRequestEvent,
    HttpServerResponseEvent,
    ReturnEvent,
    SqlEvent,
)
from ._implementation.instrument import is_instrumentation_disabled
from ._implementation.metadata import Metadata
from ._implementation.recorder import Recorder
from ._implementation.utils import patch_class, values_dict
from ._implementation.web_framework import AppmapMiddleware
from ._implementation.web_framework import TemplateHandler as BaseTemplateHandler


def parse_pg_version(version):
    """Transform postgres version number like 120005 to a tuple like 12.0.5."""
    return (version // 10000 % 100, version // 100 % 100, version % 100)


def database_version(connection):
    """Examine a database connection and try to establish the backend version."""
    vendor = connection.vendor
    if vendor == "sqlite":
        return connection.Database.sqlite_version_info
    if vendor == "mysql":
        return connection.mysql_version
    if vendor == "postgresql":
        return parse_pg_version(connection.pg_version)
    if vendor == "oracle":
        return connection.oracle_version
    return None


def add_metadata():
    """Adds Django framework to metadata for the next appmap generation."""
    Metadata.add_framework("Django", django.get_version())


class ExecuteWrapper:
    def __init__(self):
        self.recorder = Recorder.get_current()

    def __call__(self, execute, sql, params, many, context):
        start = time.monotonic()
        try:
            return execute(sql, params, many, context)
        finally:
            if is_instrumentation_disabled():
                # We must be in the middle of fetching object representation.
                # Don't record this query in the appmap.
                pass
            elif self.recorder.get_enabled():
                add_metadata()
                stop = time.monotonic()
                duration = stop - start
                conn = context["connection"]
                # Note this logic is based on django.db.backends.utils.CursorDebugWrapper.
                if many:
                    # Sometimes the same query is executed with different parameter sets.
                    # Instead of substituting them all, just say how many times it was run.
                    try:
                        times = len(params)
                    except TypeError:
                        times = "?"
                    sql = "%s times %s" % (times, sql)
                else:
                    cursor = context["cursor"]
                    sql = conn.ops.last_executed_query(cursor, sql, params)
                call_event = SqlEvent(
                    sql, vendor=conn.vendor, version=database_version(conn)
                )
                Recorder.add_event(call_event)
                return_event = ReturnEvent(parent_id=call_event.id, elapsed=duration)
                Recorder.add_event(return_event)


# CursorDebugWrapper is used in tests to capture and examine queries.
# However, recording appmap can cause additional queries to run when fetching
# object representation. Make sure tests don't see these queries.

original_execute = CursorDebugWrapper.execute


def wrapped_execute(self, sql, params=None):
    """Directly execute the query if instrumentation is temporarily
    disabled, to avoid capturing queries not issued by the application."""
    if is_instrumentation_disabled():
        # fmt: off
        return super().execute(sql, params) # pyright: ignore (seems like [superCallZeroArgForm] should suppress this, it doesn't)
        # fmt on
    return original_execute(self, sql, params)


CursorDebugWrapper.execute = wrapped_execute


@receiver(connection_created)
def connected(sender, connection, **_):
    # pylint: disable=unused-argument

    # warm the version cache in the backend to avoid running
    # additional queries in the middle of processing client queries
    database_version(connection)

    wrappers = connection.execute_wrappers
    if not any(isinstance(x, ExecuteWrapper) for x in wrappers):
        wrappers.append(ExecuteWrapper())


def request_params(request):
    """Extract request parameters as a dict.

    Parses query and form data and JSON request body.
    Multiple parameter values are represented as lists."""
    params = request.GET.copy()
    params.update(request.POST)

    if request.content_type == "application/json":
        try:
            # Note: it's important to use request.body here instead of
            # directly reading request. This way the application can still
            # access the body which is now cached in the request object.
            params.update(json.loads(request.body))
        except (json.decoder.JSONDecodeError, AttributeError):
            pass  # invalid json or not an object

    return values_dict(params.lists())


def get_resolved_match(path_info, resolver):
    resolver_match = resolver.resolve(path_info)

    # Sometimes the route returned by resolve is a regex, sometimes
    # it's a url pattern.

    # Start by assuming it's a regex.
    regex = resolver_match.route

    match = re.match(regex, path_info[1:])
    if match:
        return (regex, match)

    # If it didn't match, it's a url pattern. Use _route_to_regex to
    # turn it into a regex.  (url patterns sometimes start with a
    # caret, which needs to be stripped before conversion.)
    if regex[0] == "^":
        regex = regex[1:]
    regex = _route_to_regex(regex)[0]

    match = re.match(regex, path_info[1:])
    if not match:
        raise RuntimeError(
            "No match for %s found with resolver %r, regex %s"
            % (path_info, resolver, regex)
        )

    return (regex, match)


def normalize_path_info(path_info, resolved):
    if not resolved.kwargs:
        # No kwargs mean no parameters to normalize
        return path_info

    resolver = get_resolver()
    regex, match = get_resolved_match(path_info, resolver)

    # Compile the regex so we can see what groups it contains.
    groups = re.compile(regex).groupindex

    # For each parameter, insert the portion of the path that precedes
    # it, followed by the name of the parameter.
    np = "/"
    pos = 0
    for i, g in enumerate(groups):
        np += match.string[pos : match.start(i + 1)]
        np += f"{{{g}}}"
        pos = match.end(i + 1)

    # Finally, append anything remaining in the path
    np += match.string[pos:]
    return np


class Middleware(AppmapMiddleware):
    """
    Django middleware to record HTTP requests. Add it to `MIDDLEWARE` in your application's
    `settings.py`.

    **NB**: This middleware isn't async capable, so the default value of `async_capable` (False) is
    correct. If you add it to the middleware stack for an async app, Django will detect this and
    ensure that requests get handled in separate threads.

    More discussion about sync vs async middleware can be found in the Django
    doc: https://docs.djangoproject.com/en/4.1/topics/http/middleware/#async-middleware.
    """

    def __init__(self, get_response):
        super().__init__()
        self.get_response = get_response
        self.recorder = Recorder.get_current()

    def __call__(self, request):
        if not self.should_record():
            return self.get_response(request)

        rec, start, call_event_id = self.before_request_hook(request, request.path_info)

        try:
            response = self.get_response(request)
        except:
            if rec.get_enabled():
                duration = time.monotonic() - start
                exception_event = ExceptionEvent(
                    parent_id=call_event_id,
                    elapsed=duration,
                    exc_info=sys.exc_info(),
                )
                rec.add_event(exception_event)
            raise

        self.after_request_hook(
            request.path_info,
            request.method,
            request.build_absolute_uri(),
            response,
            response,
            start,
            call_event_id,
        )

        return response

    def before_request_main(self, rec, request):
        add_metadata()
        start = time.monotonic()
        params = request_params(request)
        try:
            resolved = resolve(request.path_info)
            params.update(resolved.kwargs)
            normalized_path_info = normalize_path_info(request.path_info, resolved)
        except Resolver404:
            # If the request was for a bad path (e.g. when an app
            # is testing 404 handling), resolving will fail.
            normalized_path_info = None

        call_event = HttpServerRequestEvent(
            request_method=request.method,
            path_info=request.path_info,
            message_parameters=params,
            normalized_path_info=normalized_path_info,
            protocol=request.META["SERVER_PROTOCOL"],
            headers=request.headers,
        )
        rec.add_event(call_event)

        return start, call_event.id

    def after_request_main(self, rec, response, start, call_event_id):
        duration = time.monotonic() - start
        return_event = HttpServerResponseEvent(
            parent_id=call_event_id,
            elapsed=duration,
            status_code=response.status_code,
            headers=dict(response.items()),
        )
        rec.add_event(return_event)


def inject_middleware():
    """Make sure AppMap middleware is added to the stack"""
    if "appmap.django.Middleware" not in settings.MIDDLEWARE:
        new_middleware = ["appmap.django.Middleware"]
        if DetectEnabled.should_enable("remote"):
            new_middleware.insert(0, "appmap._implementation.django.RemoteRecording")
        settings.MIDDLEWARE[0:0] = new_middleware


original_load_middleware = BaseHandler.load_middleware


def load_middleware(*args, **kwargs):
    """Patched wrapper to inject AppMap middleware first"""
    inject_middleware()
    return original_load_middleware(*args, **kwargs)


BaseHandler.load_middleware = load_middleware


@patch_class(Template)
class TemplateHandler(BaseTemplateHandler):
    @property
    def filename(self):
        """The full path of the template file."""
        return self.origin.name  # pylint: disable=no-member
