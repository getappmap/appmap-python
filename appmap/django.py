"""Django integration. Captures HTTP requests and SQL queries.

Automatically used in pytest tests.
"""

import json
import re
import sys
import time

import django
from django.conf import settings as django_settings
from django.core.handlers.base import BaseHandler
from django.db.backends.signals import connection_created
from django.db.backends.utils import CursorDebugWrapper
from django.dispatch import receiver
from django.template import Template
from django.urls import get_resolver, resolve
from django.urls.exceptions import Resolver404

from _appmap.env import Env
from _appmap.event import (
    ExceptionEvent,
    HttpServerRequestEvent,
    HttpServerResponseEvent,
    ReturnEvent,
    SqlEvent,
)
from _appmap.instrument import is_instrumentation_disabled
from _appmap.metadata import Metadata
from _appmap.recorder import Recorder
from _appmap.utils import patch_class, values_dict
from _appmap.web_framework import JSON_ERRORS, AppmapMiddleware, MiddlewareInserter
from _appmap.web_framework import TemplateHandler as BaseTemplateHandler

logger = Env.current.getLogger(__name__)


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


class ExecuteWrapper:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.recorder = Recorder.get_current()

    # This signature is correct, the implementation confuses pylint:
    def __call__(
        self, execute, sql, params, many, context
    ):  # pylint: disable=too-many-arguments
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
        # Seems like pyright: ignore [superCallZeroArgForm] should suppress this, it doesn't:
        return super().execute(sql, params) # pyright: ignore
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
        except JSON_ERRORS:
            pass  # invalid json or not an object

    return values_dict(params.lists())


def get_resolved_match(path_info, resolver):
    resolver_match = resolver.resolve(path_info)

    # The last element of resolver_match.tried is the list of URLResolvers that matched path_info.
    # Each URLResolver knows how to turn itself into a regex that will match the appropriate portion
    # of the path. Iterate through them and create a complete regex for the path.
    parts = []
    for part in resolver_match.tried[-1]:
        # Django inserts a leading '^'.
        r = part.pattern.regex.pattern.lstrip("^")
        parts.append(r)
    regex = "".join(parts)

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
        super().__init__("Django")
        self.get_response = get_response
        self.recorder = Recorder.get_current()

    def __call__(self, request):
        if not self.should_record:
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

    def before_request_main(self, rec, req):
        add_metadata()
        start = time.monotonic()
        params = request_params(req)
        try:
            resolved = resolve(req.path_info)
            params.update(resolved.kwargs)
            normalized_path_info = normalize_path_info(req.path_info, resolved)
        except Resolver404:
            # If the request was for a bad path (e.g. when an app
            # is testing 404 handling), resolving will fail.
            normalized_path_info = None

        call_event = HttpServerRequestEvent(
            request_method=req.method,
            path_info=req.path_info,
            message_parameters=params,
            normalized_path_info=normalized_path_info,
            protocol=req.META["SERVER_PROTOCOL"],
            headers=req.headers,
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


class DjangoInserter(MiddlewareInserter):
    def __init__(self, settings):
        super().__init__(settings.DEBUG)
        self.settings = settings

    def middleware_present(self):
        return "appmap.django.Middleware" in self.settings.MIDDLEWARE

    def insert_middleware(self):
        stack = list(self.settings.MIDDLEWARE)

        new_middleware = ["appmap.django.Middleware"]
        enable_by_default = "true" if self.debug else "false"
        if Env.current.enables("remote", enable_by_default):
            new_middleware.insert(0, "_appmap.django.RemoteRecording")

        stack[0:0] = new_middleware
        # Django is ok with settings.MIDDLEWARE being any kind iterable. Update it, without changing
        # its type, if we can.
        msg = (
            "Don't know how to update settings.MIDDLEWARE of type %s, recording is not enabled.",
        )
        if isinstance(self.settings.MIDDLEWARE, list):
            self.settings.MIDDLEWARE = stack
        elif isinstance(self.settings.MIDDLEWARE, tuple):
            self.settings.MIDDLEWARE = tuple(stack)
        else:
            logger.warning(
                msg,
                type(self.settings.MIDDLEWARE),
            )

    def remote_enabled(self):
        return "_appmap.django.RemoteRecording" in self.settings.MIDDLEWARE


def inject_middleware():
    """Make sure AppMap middleware is added to the stack"""
    DjangoInserter(django_settings).run()


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
