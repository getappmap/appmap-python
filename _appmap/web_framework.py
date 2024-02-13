"""Common utilities for web framework integration"""

import datetime
import os
import os.path
import re
import sys
import textwrap
import time
from abc import ABC, abstractmethod
from contextvars import ContextVar
from hashlib import sha256
from json.decoder import JSONDecodeError

from _appmap import recording

from . import generation, remote_recording
from .env import Env
from .event import Event, ReturnEvent, describe_value
from .recorder import Recorder, ThreadRecorder
from .utils import root_relative_path, scenario_filename

logger = Env.current.getLogger(__name__)
request_recorder = ContextVar("appmap_request_recorder")

# These are the errors that can get raised when trying to update params based on the results of
# parsing the body of an application/json request:
JSON_ERRORS = (JSONDecodeError, AttributeError, TypeError, ValueError)


class TemplateEvent(Event):  # pylint: disable=too-few-public-methods
    """A special call event that records template rendering."""

    __slots__ = ["receiver", "path"]

    def __init__(self, path, instance=None):
        super().__init__("call")
        self.receiver = describe_value(None, instance)
        self.path = root_relative_path(path)

    def to_dict(self, attrs=None):
        result = super().to_dict(attrs)
        classlike_name = re.sub(r"\W", "", self.path.title())
        result.update(
            {
                "defined_class": f"<templates>.{classlike_name}",
                "method_id": "render",
                "static": False,
            }
        )
        return result


class TemplateHandler:  # pylint: disable=too-few-public-methods
    """Patch for a template class to capture and record template
    rendering (if recording is enabled).

    This patch can be used with .utils.patch_class to patch any template class
    which has a .render() method. Note it requires a .filename property; if
    there is no such property, this handler can be subclassed first to provide it.
    """

    def render(self, orig, *args, **kwargs):
        """Calls the original implementation.

        If recording is enabled, adds appropriate TemplateEvent
        and ReturnEvent.
        """
        rec = Recorder.get_current()
        if rec.get_enabled():
            start = time.monotonic()
            call_event = TemplateEvent(self.filename, self)  # pylint: disable=no-member
            Recorder.add_event(call_event)
        try:
            return orig(self, *args, **kwargs)
        finally:
            if rec.get_enabled():
                Recorder.add_event(ReturnEvent(call_event.id, time.monotonic() - start))


NAME_MAX = 255  # true for most filesystems
HASH_LEN = 7  # arbitrary, but git proves it's a reasonable value
APPMAP_SUFFIX = ".appmap.json"


def name_hash(namepart):
    """Returns the hex digits of the sha256 of the os.fsencode()d namepart."""
    return sha256(os.fsencode(namepart)).hexdigest()


def create_appmap_file(
    output_dir,
    request_method,
    request_path_info,
    request_full_path,
    response,
    headers,
    rec,
):
    start_time = datetime.datetime.now()
    appmap_name = (
        request_method
        + " "
        + request_path_info
        + " ("
        + str(response.status_code)
        + ") - "
        + start_time.strftime("%T.%f")[:-3]
    )
    appmap_basename = scenario_filename("_".join([str(start_time.timestamp()), request_full_path]))
    appmap_file_path = os.path.join(output_dir, appmap_basename)

    recorder_type = "requests"
    metadata = {
        "name": appmap_name,
        "timestamp": start_time.timestamp(),
        "recorder": {"name": "record_requests", "type": recorder_type},
    }
    recording.write_appmap(rec, appmap_basename, recorder_type, metadata)
    headers["AppMap-Name"] = os.path.abspath(appmap_name)
    headers["AppMap-File-Name"] = os.path.abspath(appmap_file_path) + APPMAP_SUFFIX


class AppmapMiddleware(ABC):
    def __init__(self, framework_name):
        self.record_url = "/_appmap/record"
        env = Env.current
        record_requests = env.enables("requests")
        if record_requests:
            logger.debug("Requests will be recorded (%s)", framework_name)

        self.should_record = env.enables("remote") or record_requests

    def before_request_hook(self, request, request_path):
        if request_path == self.record_url:
            return None, None, None

        rec = None
        start = None
        call_event_id = None
        env = Env.current
        if env.enables("requests"):
            rec = ThreadRecorder()
            Recorder.set_current(rec)
            rec.start_recording()
            request_recorder.set(rec)
        elif env.enables("remote"):
            rec = Recorder.get_global()

        if rec and rec.get_enabled():
            start, call_event_id = self.before_request_main(rec, request)

        return rec, start, call_event_id

    @abstractmethod
    def before_request_main(self, rec, req):
        """Specify the main operations to be performed by a request is processed."""

    def after_request_hook(
        self,
        request_path,
        request_method,
        request_base_url,
        response,
        response_headers,
        start,
        call_event_id,
    ):
        if request_path == self.record_url:
            return response

        env = Env.current
        if env.enables("requests"):
            rec = request_recorder.get()
            try:
                self.after_request_main(rec, response, start, call_event_id)

                output_dir = Env.current.output_dir / "requests"
                create_appmap_file(
                    output_dir,
                    request_method,
                    request_path,
                    request_base_url,
                    response,
                    response_headers,
                    rec,
                )
            finally:
                rec.stop_recording()
                Recorder.set_current(None)
                request_recorder.set(None)
        elif env.enables("remote"):
            rec = Recorder.get_global()
            if rec.get_enabled():
                self.after_request_main(rec, response, start, call_event_id)

        return response

    @abstractmethod
    def after_request_main(self, rec, response, start, call_event_id):
        """Specify the main operations to be performed after a request is processed."""


class MiddlewareInserter(ABC):
    def __init__(self, debug):
        self.debug = debug

    @abstractmethod
    def middleware_present(self):
        """Return True if the AppMap middleware is present, False otherwise."""

    @abstractmethod
    def insert_middleware(self):
        """Insert the AppMap middleware."""

    @abstractmethod
    def remote_enabled(self):
        """Return True if the AppMap middleware has enabled remote recording, False otherwise."""

    def run(self):
        if not self.middleware_present():
            self.insert_middleware()

        if self.remote_enabled() and not self.debug:
            self._show_warning()

    def _show_warning(self):
        # The user has explicitly asked for remote recording to be enabled in production. Let them
        # know this probably isn't a good idea.
        print("\n\n*** SECURITY RISK ***", file=sys.stderr)
        msg = "Enabling remote recording in production can expose secret information."
        print(
            textwrap.fill(msg),
            file=sys.stderr,
        )
        print("*** SECURITY RISK ***\n\n", file=sys.stderr)
        logger.warning(msg)


def initialize():
    remote_recording.initialize()
