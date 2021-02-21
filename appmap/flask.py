from functools import wraps
import json
import time

import flask.cli
from flask import g, request

from appmap._implementation.env import Env
from appmap._implementation import generation
from appmap._implementation.event import HttpRequestEvent, HttpResponseEvent
from appmap._implementation.recording import Recorder, Recording


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

        self.record_url = '/_appmap/record'

        # print('in init_app')
        app.add_url_rule(self.record_url, 'appmap_record_get', view_func=self.record_get, methods=['GET'])
        app.add_url_rule(self.record_url, 'appmap_record_post', view_func=self.record_post, methods=['POST'])
        app.add_url_rule(self.record_url, 'appmap_record_delete', view_func=self.record_delete, methods=['DELETE'])

        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def record_get(self):
        return {'enabled': self.recording.is_running()}

    def record_post(self):
        if self.recording.is_running():
            return 'Recording is already in progress', 409

        self.recording.start()
        return '', 200

    def record_delete(self):
        if not self.recording.is_running():
            return 'No recording is in progress', 404

        self.recording.stop()

        return json.loads(generation.dump(self.recording))

    def before_request(self):
        if self.recording.is_running() and request.path != self.record_url:
            call_event = HttpRequestEvent(
                request_method=request.method,
                path_info=request.path,
                normalized_path_info=request.url_rule.rule,
                protocol=request.environ.get('SERVER_PROTOCOL')
            )
            Recorder().add_event(call_event)

            g.appmap_request_event = call_event
            g.appmap_request_start = time.monotonic()

    def after_request(self, response):
        if self.recording.is_running() and request.path != self.record_url:
            parent_id = g.appmap_request_event.id
            duration = time.monotonic() - g.appmap_request_start

            return_event = HttpResponseEvent(
                parent_id=parent_id,
                elapsed=duration,
                status_code=response.status_code,
                mime_type=response.content_type
            )
            Recorder().add_event(return_event)

        return response


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
