import re
import time

import flask
import flask.cli
import jinja2
from flask import g, request
from flask.cli import ScriptInfo
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from _appmap.env import Env
from _appmap.event import HttpServerRequestEvent, HttpServerResponseEvent
from _appmap.flask import app as remote_recording_app
from _appmap.metadata import Metadata
from _appmap.utils import patch_class, values_dict
from _appmap.web_framework import JSON_ERRORS, AppmapMiddleware, MiddlewareInserter
from _appmap.web_framework import TemplateHandler as BaseTemplateHandler
from appmap import wrapt

try:
    # pylint: disable=unused-import
    from . import sqlalchemy  # noqa: F401
except ImportError:
    # not using sqlalchemy
    pass

logger = Env.current.getLogger(__name__)
_JSON_ERRORS = (
    BadRequest,
    UnsupportedMediaType,
)


def request_params(req):
    """Extract request parameters as a dict.

    Parses query and form data and JSON request body.
    Multiple parameter values are represented as lists."""
    params = req.values.copy()
    params.update(req.view_args or {})
    try:
        params.update(req.json or {})
    # pylint is wrong about this "exception operation":
    except _JSON_ERRORS + JSON_ERRORS:  # pylint: disable=wrong-exception-operation
        # If request claims to be application/json, but its body is unparsable, BadRequest will be
        # raised. json is pretty forgiving about what it will parse, though, so req.json may not be
        # a dict. When that's the case, ValueError or TypeError may be raised when trying to update
        # params.
        pass

    return values_dict(params.lists())


NP_PARAMS = re.compile(r"<Rule '(.*?)'")
NP_PARAM_DELIMS = str.maketrans("<>", "{}")

_REQUEST_ENABLED_ATTR = "_appmap_request_enabled"
_REMOTE_ENABLED_ATTR = "_appmap_remote_enabled"


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

    def __init__(self):
        super().__init__("Flask")

    def init_app(self, app):
        enable_by_default = "true" if app.debug else "false"
        remote_enabled = Env.current.enables("remote", enable_by_default)
        if remote_enabled:
            logger.debug("Remote recording is enabled (Flask)")
            app.wsgi_app = DispatcherMiddleware(
                app.wsgi_app, {"/_appmap": remote_recording_app}
            )
        setattr(app, _REMOTE_ENABLED_ATTR, remote_enabled)

        app.before_request(self.before_request)
        app.after_request(self.after_request)
        setattr(app, _REQUEST_ENABLED_ATTR, True)

    def before_request(self):
        if not self.should_record:
            return

        self.before_request_hook(request, request.path)

    def before_request_main(self, rec, req):
        Metadata.add_framework("flask", flask.__version__)
        np = None
        if req.url_rule:
            # pragma pylint: disable=line-too-long
            # Transform request.url to the expected normalized-path form. For example,
            # "/post/<username>/<post_id>/summary" becomes "/post/{username}/{post_id}/summary".
            # Notes:
            #   * the value of `repr` of this rule begins with "<Rule '/post/<username>/<post_id>/summary'"
            #   * the variable names in a rule can only contain alphanumerics:
            #     * flask 1: https://github.com/pallets/werkzeug/blob/1dde4b1790f9c46b7122bb8225e6b48a5b22a615/src/werkzeug/routing.py#L143
            #     * flask 2: https://github.com/pallets/werkzeug/blob/99f328cf2721e913bd8a3128a9cdd95ca97c334c/src/werkzeug/routing/rules.py#L56
            # pragma pylint: enable=line-too-long
            r = repr(req.url_rule)
            np = NP_PARAMS.findall(r)[0].translate(NP_PARAM_DELIMS)

        call_event = HttpServerRequestEvent(
            request_method=req.method,
            path_info=req.path,
            message_parameters=request_params(req),
            normalized_path_info=np,
            protocol=req.environ.get("SERVER_PROTOCOL"),
            headers=req.headers,
        )
        rec.add_event(call_event)

        # Flask 2 removed the suggestion to use _app_ctx_stack.top, and instead says extensions
        # should use g with a private property.
        g._appmap_request_event = call_event  # pylint: disable=protected-access
        g._appmap_request_start = time.monotonic()  # pylint: disable=protected-access
        return None, None

    def after_request(self, response):
        if not self.should_record:
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

    def after_request_main(self, rec, response, start, _):
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


class FlaskInserter(MiddlewareInserter):
    def __init__(self, app):
        super().__init__(app.debug)
        self.app = app

    def middleware_present(self):
        return hasattr(self.app, _REQUEST_ENABLED_ATTR)

    def insert_middleware(self):
        AppmapFlask().init_app(self.app)

    def remote_enabled(self):
        return getattr(self.app, _REMOTE_ENABLED_ATTR, None)


def install_extension(wrapped, _, args, kwargs):
    app = wrapped(*args, **kwargs)
    if app:
        FlaskInserter(app).run()

    return app


if Env.current.enabled:
    # ScriptInfo.load_app is the function that's used by the Flask cli to load an app, no matter how
    # the app's module is specified (e.g. with the FLASK_APP env var, the `--app` flag, etc). Hook
    # it so it installs our extension on the app.
    ScriptInfo.load_app = wrapt.wrap_function_wrapper(
        "flask.cli", "ScriptInfo.load_app", install_extension
    )
