import re
import time
from importlib.metadata import version
from types import SimpleNamespace

import jinja2
from blinker import signal
from flask import g, request, request_finished, request_started
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from _appmap import wrapt
from _appmap.env import Env
from _appmap.event import HttpServerRequestEvent
from _appmap.flask import app as remote_recording_app
from _appmap.metadata import Metadata
from _appmap.utils import patch_class, values_dict
from _appmap.web_framework import (
    JSON_ERRORS,
    REMOTE_ENABLED_ATTR,
    REQUEST_ENABLED_ATTR,
    AppmapMiddleware,
    MiddlewareInserter,
)
from _appmap.web_framework import TemplateHandler as BaseTemplateHandler

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
_after_finalize = signal("_appmap_after_finalize")
_before_exception = signal("_appmap_before_exception")


class AppmapFlask(AppmapMiddleware):
    """
    A Flask extension to add remote recording to an application.
    Should be loaded by default, but can also be added manually.

    For example:

    ```
    from appmap.flask import AppmapFlask

    app = new Flask(__Name__)
    AppmapFlask(app).init_app()
    ```
    """

    def __init__(self, app):
        super().__init__("Flask")
        self.app = app

    def init_app(self):
        enable_by_default = "true" if self.app.debug else "false"
        remote_enabled = Env.current.enables("remote", enable_by_default)
        if remote_enabled:
            logger.debug("Remote recording is enabled (Flask)")
            self.app.wsgi_app = DispatcherMiddleware(
                self.app.wsgi_app, {"/_appmap": remote_recording_app}
            )
        setattr(self.app, REMOTE_ENABLED_ATTR, remote_enabled)

        request_started.connect(self.request_started, self.app, weak=False)
        request_finished.connect(self.request_finished, self.app, weak=False)
        _after_finalize.connect(self.after_finalize, sender=self.app, weak=False)

        setattr(self.app, REQUEST_ENABLED_ATTR, True)

    def request_started(self, _, **__):
        # request context is bound, we can use flask.request now:
        self.before_request_hook(request)

    def before_request_main(self, rec, req):
        Metadata.add_framework("flask", version("flask"))
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

        # Save the current recorder in flask.g, so it will be available in
        # the got_request_exception signal handler. Flask seems to be resetting the
        # current Context before signaling, which removes our ContextVar.
        # TODO: enhance AppmapMiddleware so it allows subclasses to specify how
        #       the request recording should be stored.
        g.appmap_recorder = rec
        g.appmap_request_event = call_event
        g.appmap_request_start = time.monotonic()
        return None, None

    def after_finalize(self, _, **__):
        if not self.should_record:
            return

        return_event = self.after_request_main(
            request.path,
            None,
            None,
            g.appmap_request_start,
            g.appmap_request_event.id,
        )

        self.after_request_hook(
            request.path,
            request.method,
            request.base_url,
            g.appmap_response.status_code,
            g.appmap_response.headers,
            return_event,
        )

    def request_finished(self, _, response, **__):
        if not self.should_record:
            return response
        g.appmap_response = response
        return response


@patch_class(jinja2.Template)
class TemplateHandler(BaseTemplateHandler):
    # pylint: disable=missing-class-docstring, too-few-public-methods
    pass


class FlaskInserter(MiddlewareInserter):
    def __init__(self, app):
        super().__init__(app.debug)
        self.app = app

    def middleware_present(self):
        return hasattr(self.app, REQUEST_ENABLED_ATTR)

    def insert_middleware(self):
        AppmapFlask(self.app).init_app()

    def remote_enabled(self):
        return getattr(self.app, REMOTE_ENABLED_ATTR, None)


def install_extension(wrapped, _, args, kwargs):
    app = wrapped(*args, **kwargs)
    if app:
        FlaskInserter(app).run()

    return app

def _finalize_request(wrapped, inst, args, kwargs):
    if not Env.current.enabled or kwargs.get("from_error_handler"):
        return wrapped(*args, **kwargs)

    ret = wrapped(*args, **kwargs)
    _after_finalize.send(inst)
    return ret


def _handle_user_exception(wrapped, inst, args, kwargs):
    if not Env.current.enabled:
        return wrapped(*args, **kwargs)

    try:
        return wrapped(*args, **kwargs)
    except Exception:  # pylint: disable=broad-exception-caught
        g.appmap_response = SimpleNamespace(status_code=500, headers={})
        _after_finalize.send(inst)
        raise


if Env.current.enabled:
    # ScriptInfo.load_app is the function that's used by the Flask cli to load an app, no matter how
    # the app's module is specified (e.g. with the FLASK_APP env var, the `--app` flag, etc). Hook
    # it so it installs our extension on the app.
    wrapt.wrap_function_wrapper("flask.cli", "ScriptInfo.load_app", install_extension)
    wrapt.wrap_function_wrapper("flask.app", "Flask.finalize_request", _finalize_request)
    wrapt.wrap_function_wrapper("flask.app", "Flask.handle_user_exception", _handle_user_exception)
