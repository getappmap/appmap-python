from django.core.handlers.base import BaseHandler
from django.conf import settings
from django.db.backends.utils import CursorDebugWrapper
from django.db.backends.signals import connection_created
from django.dispatch import receiver

import time
import json

from appmap._implementation.event import \
    SqlEvent, ReturnEvent, HttpServerRequestEvent, HttpServerResponseEvent
from appmap._implementation.instrument import is_instrumentation_disabled
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
            params.update(json.load(request))
        except (json.decoder.JSONDecodeError, AttributeError):
            pass  # invalid json or not an object

    return values_dict(params.lists())


class Middleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.recorder = Recorder()

    def __call__(self, request):
        if self.recorder.enabled:
            start = time.monotonic()
            call_event = HttpServerRequestEvent(
                request_method=request.method,
                path_info=request.path_info,
                message_parameters=request_params(request),
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
