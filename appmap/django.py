from appmap._implementation.event import SqlEvent, ReturnEvent, HttpRequestEvent, HttpResponseEvent
from appmap._implementation.recording import Recorder

from django.core.handlers.base import BaseHandler
from django.conf import settings

from django.db.backends.signals import connection_created
from django.dispatch import receiver

import time
import json


class ExecuteWrapper:
    def __init__(self):
        self.recorder = Recorder()

    def __call__(self, execute, sql, params, many, context):
        start = time.monotonic()
        try:
            return execute(sql, params, many, context)
        finally:
            if self.recorder.enabled:
                stop = time.monotonic()
                duration = stop - start
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
                    db = context['connection']
                    cursor = context['cursor']
                    sql = db.ops.last_executed_query(cursor, sql, params)
                call_event = SqlEvent(sql)
                self.recorder.add_event(call_event)
                return_event = ReturnEvent(parent_id=call_event.id, elapsed=duration)
                self.recorder.add_event(return_event)


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
            # note: replace with json.load(request) after we drop 3.5 support
            params.update(json.loads(request.body.decode()))
        except (json.decoder.JSONDecodeError, AttributeError):
            pass  # invalid json or not an object

    return {k: v[0] if len(v) == 1 else v for k, v in params.lists()}


class Middleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.recorder = Recorder()

    def __call__(self, request):
        if self.recorder.enabled:
            start = time.monotonic()
            call_event = HttpRequestEvent(
                request_method=request.method,
                path_info=request.path_info,
                message_parameters=request_params(request),
                protocol=request.META['SERVER_PROTOCOL']
            )
            self.recorder.add_event(call_event)

        response = self.get_response(request)

        if self.recorder.enabled:
            duration = time.monotonic() - start
            return_event = HttpResponseEvent(
                parent_id=call_event.id,
                elapsed=duration,
                status_code=response.status_code,
                mime_type=response.get('Content-Type', None) or 'unknown'
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
