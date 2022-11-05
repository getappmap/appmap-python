import re
import time

import flask
import flask.cli
import jinja2
from flask import g, request
from flask.cli import ScriptInfo
from werkzeug.exceptions import BadRequest
from werkzeug.middleware.dispatcher import DispatcherMiddleware

import appmap.wrapt as wrapt
from appmap._implementation.detect_enabled import DetectEnabled
from appmap._implementation.env import Env
from appmap._implementation.event import HttpServerRequestEvent, HttpServerResponseEvent
from appmap._implementation.flask import app as remote_recording_app
from appmap._implementation.web_framework import AppmapMiddleware
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


NP_PARAMS = re.compile(r"<Rule '(.*?)'")
NP_PARAM_DELIMS = str.maketrans("<>", "{}")


class AppmapFlask(AppmapMiddleware):
    """
    A Flask extension to add remote recording to an application.
    Should be loaded by default, but can also be added manually.

    For example:

    ```
    from appmap.flask import AppmapFlask

    app = new Flask(__Name__)
    AppmapFlask().init_app(app)
    ```
    """

    def init_app(self, app):
        if DetectEnabled.should_enable("remote"):
            app.wsgi_app = DispatcherMiddleware(
                app.wsgi_app, {"/_appmap": remote_recording_app}
            )

        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        if not self.should_record():
            return

        self.before_request_hook(request, request.path)

    def before_request_main(self, rec, request):
        Metadata.add_framework("flask", flask.__version__)
        np = None
        if request.url_rule:
            # pragma pylint: disable=line-too-long
            # Transform request.url to the expected normalized-path form. For example,
            # "/post/<username>/<post_id>/summary" becomes "/post/{username}/{post_id}/summary".
            # Notes:
            #   * the value of `repr` of this rule begins with "<Rule '/post/<username>/<post_id>/summary'"
            #   * the variable names in a rule can only contain alphanumerics:
            #     * flask 1: https://github.com/pallets/werkzeug/blob/1dde4b1790f9c46b7122bb8225e6b48a5b22a615/src/werkzeug/routing.py#L143
            #     * flask 2: https://github.com/pallets/werkzeug/blob/99f328cf2721e913bd8a3128a9cdd95ca97c334c/src/werkzeug/routing/rules.py#L56
            # pragma pylint: enable=line-too-long
            r = repr(request.url_rule)
            np = NP_PARAMS.findall(r)[0].translate(NP_PARAM_DELIMS)

        call_event = HttpServerRequestEvent(
            request_method=request.method,
            path_info=request.path,
            message_parameters=request_params(request),
            normalized_path_info=np,
            protocol=request.environ.get("SERVER_PROTOCOL"),
            headers=request.headers,
        )
        rec.add_event(call_event)

        # Flask 2 removed the suggestion to use _app_ctx_stack.top, and instead says extensions
        # should use g with a private property.
        g._appmap_request_event = call_event  # pylint: disable=protected-access
        g._appmap_request_start = time.monotonic()  # pylint: disable=protected-access
        return None, None

    def after_request(self, response):
        if not self.should_record():
            return response

        return self.after_request_hook(
            request.path,
            request.method,
            request.base_url,
            response,
            response.headers,
            None,
            None,
        )

    def after_request_main(self, rec, response, start, call_event_id):
        parent_id = g._appmap_request_event.id  # pylint: disable=protected-access
        start = g._appmap_request_start  # pylint: disable=protected-access
        duration = time.monotonic() - start
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


def install_extension(wrapped, _, args, kwargs):
    app = wrapped(*args, **kwargs)
    if app:
        AppmapFlask().init_app(app)

    return app


if Env.current.enabled:
    # ScriptInfo.load_app is the function that's used by the Flask cli to load an app, no matter how
    # the app's module is specified (e.g. with the FLASK_APP env var, the `--app` flag, etc). Hook
    # it so it installs our extension on the app.
    ScriptInfo.load_app = wrapt.wrap_function_wrapper(
        "flask.cli", "ScriptInfo.load_app", install_extension
    )
