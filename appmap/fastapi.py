import sys
import time
from importlib.metadata import version
from urllib.parse import urlunparse

import fastapi
from starlette.middleware.base import BaseHTTPMiddleware

from _appmap import utils, wrapt
from _appmap.env import Env
from _appmap.event import HttpServerRequestEvent
from _appmap.fastapi import app as fastapi_remote
from _appmap.importer import Filterable, FilterableFn, Importer
from _appmap.metadata import Metadata
from _appmap.utils import appmap_tls_context, values_dict
from _appmap.web_framework import (
    JSON_ERRORS,
    REMOTE_ENABLED_ATTR,
    REQUEST_ENABLED_ATTR,
    AppmapMiddleware,
    MiddlewareInserter,
)

logger = Env.current.getLogger(__name__)


def _add_api_route(wrapped, _, args, kwargs):
    if not Env.current.enabled:
        wrapped(*args, **kwargs)
        return

    fn = args[1]

    fqn = utils.FqFnName(fn)
    scope = Filterable(fqn.scope, fqn.fqclass, None)

    filterable_fn = FilterableFn(scope, fn, fn)
    logger.debug("_add_api_route, fn: %s", filterable_fn.fqname)
    instrumented_fn = Importer.instrument_function(fqn.fn_name, filterable_fn)

    if instrumented_fn != filterable_fn.obj:
        instrumented_fn = wrapt.FunctionWrapper(fn, instrumented_fn)
    wrapped(args[0], instrumented_fn, **kwargs)


if Env.current.enabled:
    wrapt.wrap_function_wrapper("fastapi.routing", "APIRouter.add_api_route", _add_api_route)


_REQUEST_EVENT_ATTR = "_appmap_server_request_event"
_MAX_JSON_LENGTH = 2048
class Middleware(AppmapMiddleware, BaseHTTPMiddleware):

    def __init__(self, app, remote_enabled=None):
        super().__init__("FastAPI")
        BaseHTTPMiddleware.__init__(self, app)
        self._json = None
        self._remote_enabled = remote_enabled

    def init_app(self):
        # pylint: disable=import-outside-toplevel
        from starlette.routing import Mount, Router

        # pylint: enable=import-outside-toplevel

        routes = [Mount("/", Middleware(self.app))]
        setattr(self.app, REQUEST_ENABLED_ATTR, True)

        if self._remote_enabled is not None:
            enable_by_default = "true" if self._remote_enabled else "false"
        else:
            enable_by_default = "false"

        remote_enabled = Env.current.enables("remote", enable_by_default)
        if remote_enabled:
            routes.insert(0, Mount("/_appmap", fastapi_remote))
        setattr(self.app, REMOTE_ENABLED_ATTR, remote_enabled)

        return Router(routes=routes)

    def before_request_main(self, rec, req: fastapi.Request):
        self.add_framework_metadata()
        start = time.monotonic()
        scope = req.scope
        scope[_REQUEST_EVENT_ATTR] = call_event = HttpServerRequestEvent(
            request_method=req.method,
            path_info=scope["path"],
            message_parameters={},
            headers=req.headers,
            protocol=f"{scope['scheme'].upper()}/{scope['http_version']}",
        )
        rec.add_event(call_event)

        return start, call_event.id

    async def dispatch(self, request, call_next):
        with appmap_tls_context():
            response = await self._dispatch(request, call_next)
        return response

    async def _dispatch(self, request, call_next):
        if not self.should_record:
            response = await call_next(request)
            return response

        await self._parse_json(request)

        rec, start, call_event_id = self.before_request_hook(request)

        try:
            response = await call_next(request)
        except:
            self.on_exception(rec, start, call_event_id, sys.exc_info())
            raise

        self._update_request_event(request)

        parsed = request.url.components
        baseurl = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
        self.after_request_hook(
            request.url.path,
            request.method,
            baseurl,
            response.status_code,
            response.headers,
            start,
            call_event_id,
        )
        return response

    async def _parse_json(self, request):
        content_length = int(request.headers.get("Content-Length", 0))
        json_content = request.headers.get("Content-Type", "").startswith("application/json")
        if not json_content or not 0 < content_length <= _MAX_JSON_LENGTH:
            return

        # Calling Request.json loads and caches the entire body. The cache
        # will be used when any code subsequently tries to access the body
        # in any way (e.g. Request.stream, Request.body, etc)
        try:
            self._json = await request.json()
            if not isinstance(self._json, dict):
                # parseable, but not a JSON object
                self._json = None
        except JSON_ERRORS:
            # parsing failed, igore
            pass

    def _update_request_event(self, request):
        # This updates the http_server_request event that was previously added
        # to the recording. This is ok for now, because we haven't done anything
        # with the events, e.g. streamed them to disk.
        #
        # If, at some point in the future, we implement some sort of
        # checkpointing, we'll need to change this so it adds the event to the
        # recording's `eventUpdates` instead.
        scope = request.scope
        if "route" not in scope:
            return

        request_event = scope[_REQUEST_EVENT_ATTR]
        route = scope["route"]
        request_event.normalized_path_info = route.path_format
        query_params = {k: request.query_params.getlist(k) for k in request.query_params.keys()}
        if self._json is not None:
            for k, v in self._json.items():
                if k in query_params:
                    query_params[k].append(v)
                else:
                    query_params[k] = [v]

        params = values_dict(query_params.items())
        # path_params are orthogonal to query_params, so update is ok
        params.update(request.path_params)
        request_event.message_parameters = params

    def add_framework_metadata(self):
        Metadata.add_framework("FastAPI", version("fastapi"))


class FastAPIInserter(MiddlewareInserter):
    def __init__(self, app, remote_enabled):
        super().__init__(remote_enabled)
        self.app = app

    def middleware_present(self):
        return hasattr(self.app, REQUEST_ENABLED_ATTR)

    def insert_middleware(self):
        return Middleware(self.app, self.debug).init_app()

    def remote_enabled(self):
        return getattr(self.app, REMOTE_ENABLED_ATTR, None)
