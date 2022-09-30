import datetime
import json
import os.path
import time
from functools import wraps

import flask
import flask.cli
import jinja2
from flask import _app_ctx_stack, request
from werkzeug.exceptions import BadRequest
from werkzeug.routing import parse_rule

from appmap._implementation import generation, web_framework
from appmap._implementation.env import Env
from appmap._implementation.event import (
    HttpServerRequestEvent,
    HttpServerResponseEvent,
    _EventIds,
)
from appmap._implementation.recording import Recorder, Recording
from appmap._implementation.web_framework import TemplateHandler as BaseTemplateHandler

from ._implementation.metadata import Metadata
from ._implementation.utils import patch_class, values_dict

try:
    # pylint: disable=unused-import
    from . import sqlalchemy  # noqa: F401
except ImportError:
    # not using sqlalchemy
    pass


def request_params(req):
    """Extract request parameters as a dict.

    Parses query and form data and JSON request body.
    Multiple parameter values are represented as lists."""
    params = req.values.copy()
    params.update(req.view_args or {})
    try:
        params.update(req.json or {})
    except BadRequest:
        pass  # probably a JSON parse error

    return values_dict(params.lists())


class AppmapFlask:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not Env.current.enabled:
            return

        if not app:
            return

        self.recording = Recording()

        self.record_url = "/_appmap/record"

        # print('in init_app')
        app.add_url_rule(
            self.record_url,
            "appmap_record_get",
            view_func=self.record_get,
            methods=["GET"],
        )
        app.add_url_rule(
            self.record_url,
            "appmap_record_post",
            view_func=self.record_post,
            methods=["POST"],
        )
        app.add_url_rule(
            self.record_url,
            "appmap_record_delete",
            view_func=self.record_delete,
            methods=["DELETE"],
        )

        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def record_get(self):
        return {"enabled": self.recording.is_running()}

    def record_post(self):
        if self.recording.is_running():
            return "Recording is already in progress", 409

        self.recording.start()
        return "", 200

    def record_delete(self):
        if not self.recording.is_running():
            return "No recording is in progress", 404

        self.recording.stop()

        return json.loads(generation.dump(self.recording))

    def before_request(self):
        if request.path == self.record_url:
            return

        if (Env.current.enabled or self.recording.is_running()):
            # It should be recording or it's currently recording.  The
            # recording is either
            # a) remote, enabled by POST to /_appmap/record, which set
            #    self.recording.is_running, or
            # b) requests, set by Env.current.record_all_requests, or
            # c) both remote and requests; there are multiple active recorders.
            if not Env.current.record_all_requests and self.recording.is_running():
                self.before_request_main([Recorder()])
            else:
                rec = Recorder(_EventIds.get_thread_id())
                rec.start_recording()
                recorders = [rec]
                # Each time an event is added for a thread_id it's
                # also added to the global Recorder().  So don't add
                # the global Recorder() into recorders: that would
                # have added the event in the global Recorder() twice.
                self.before_request_main(recorders)

    def before_request_main(self, recorders):
        for rec in recorders:
            if rec.enabled:
                Metadata.add_framework("flask", flask.__version__)
                np = None
                # See
                # https://github.com/pallets/werkzeug/blob/2.0.0/src/werkzeug/routing.py#L213
                # for a description of parse_rule.
                if request.url_rule:
                    np = "".join(
                        [
                            f"{{{p}}}" if c else p
                            for c, _, p in parse_rule(request.url_rule.rule)
                        ]
                    )
                call_event = HttpServerRequestEvent(
                    request_method=request.method,
                    path_info=request.path,
                    message_parameters=request_params(request),
                    normalized_path_info=np,
                    protocol=request.environ.get("SERVER_PROTOCOL"),
                    headers=request.headers,
                )
                rec.add_event(call_event)

                appctx = _app_ctx_stack.top
                appctx.appmap_request_event = call_event
                appctx.appmap_request_start = time.monotonic()

    def after_request(self, response):
        if request.path == self.record_url:
            return response

        if Env.current.enabled or self.recording.is_running():
            # It should be recording or it's currently recording.  The
            # recording is either
            # a) remote, enabled by POST to /_appmap/record, which set
            #    self.recording.is_running, or
            # b) requests, set by Env.current.record_all_requests, or
            # c) both remote and requests; there are multiple active recorders.
            if not Env.current.record_all_requests and self.recording.is_running():
                # a)
                self.after_request_main([Recorder()], response)
            else:
                # b) or c)
                rec = Recorder(_EventIds.get_thread_id())
                recorders = [rec]
                # Each time an event is added for a thread_id it's
                # also added to the global Recorder().  So don't add
                # the global Recorder() into recorders: that would
                # have added the event in the global Recorder() twice.
                try:
                    self.after_request_main(recorders, response)
                    output_dir = Env.current.output_dir / "requests"
                    web_framework.create_appmap_file(
                        output_dir,
                        request.method,
                        request.path,
                        request.base_url,
                        response,
                        response.headers,
                        rec,
                    )
                finally:
                    rec.stop_recording()

        return response

    def after_request_main(self, recorders, response):
        for rec in recorders:
            if rec.enabled:
                appctx = _app_ctx_stack.top
                parent_id = appctx.appmap_request_event.id
                duration = time.monotonic() - appctx.appmap_request_start

                return_event = HttpServerResponseEvent(
                    parent_id=parent_id,
                    elapsed=duration,
                    status_code=response.status_code,
                    headers=response.headers,
                )
                rec.add_event(return_event)


@patch_class(jinja2.Template)
class TemplateHandler(BaseTemplateHandler):
    # pylint: disable=missing-class-docstring, too-few-public-methods
    pass


def wrap_cli_fn(fn):
    @wraps(fn)
    def install_middleware(*args, **kwargs):
        app = fn(*args, **kwargs)
        if app:
            appmap_flask = AppmapFlask()
            appmap_flask.init_app(app)
        return app

    return install_middleware


if Env.current.enabled:
    flask.cli.call_factory = wrap_cli_fn(flask.cli.call_factory)
    flask.cli.locate_app = wrap_cli_fn(flask.cli.locate_app)
