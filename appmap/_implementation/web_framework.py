"""Common utilities for web framework integration"""

import datetime
import os
import os.path
import re
import time
from abc import ABC, abstractmethod
from contextvars import ContextVar
from hashlib import sha256
from tempfile import NamedTemporaryFile

from . import generation, remote_recording
from .detect_enabled import DetectEnabled
from .env import Env
from .event import Event, ReturnEvent, describe_value
from .recorder import Recorder, ThreadRecorder
from .utils import root_relative_path, scenario_filename


class TemplateEvent(Event):  # pylint: disable=too-few-public-methods
    """A special call event that records template rendering."""

    __slots__ = ["receiver", "path"]

    def __init__(self, path, instance=None):
        super().__init__("call")
        self.receiver = describe_value(instance)
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


def write_appmap(basedir, basename, contents):
    """Write an appmap file into basedir.

    Adds APPMAP_SUFFIX to basename; shortens the name if necessary.
    Atomically replaces existing files. Creates the basedir if required.
    """

    if len(basename) > NAME_MAX - len(APPMAP_SUFFIX):
        part = NAME_MAX - len(APPMAP_SUFFIX) - 1 - HASH_LEN
        basename = basename[:part] + "-" + name_hash(basename[part:])[:HASH_LEN]
    filename = basename + APPMAP_SUFFIX

    if not basedir.exists():
        basedir.mkdir(parents=True, exist_ok=True)

    with NamedTemporaryFile(mode="w", dir=basedir, delete=False) as tmp:
        tmp.write(contents)
    os.replace(tmp.name, basedir / filename)


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
    appmap_basename = scenario_filename(
        "_".join([str(start_time.timestamp()), request_full_path])
    )
    appmap_file_path = os.path.join(output_dir, appmap_basename)
    metadata = {
        "name": appmap_name,
        "timestamp": start_time.timestamp(),
        "recorder": {"name": "record_requests"},
    }
    write_appmap(output_dir, appmap_basename, generation.dump(rec, metadata))
    headers["AppMap-Name"] = os.path.abspath(appmap_name)
    headers["AppMap-File-Name"] = os.path.abspath(appmap_file_path) + APPMAP_SUFFIX


request_recorder = ContextVar("appmap_request_recorder")


class AppmapMiddleware(ABC):
    def __init__(self):
        self.record_url = "/_appmap/record"

    @staticmethod
    def should_record():
        return DetectEnabled.should_enable("remote") or DetectEnabled.should_enable(
            "requests"
        )

    def before_request_hook(self, request, request_path):
        if request_path == self.record_url:
            return None, None, None

        rec = None
        start = None
        call_event_id = None
        if DetectEnabled.should_enable("requests"):
            # a) requests
            rec = ThreadRecorder()
            Recorder.set_current(rec)
            rec.start_recording()
            request_recorder.set(rec)
        elif DetectEnabled.should_enable("remote"):
            rec = Recorder.get_global()

        if rec and rec.get_enabled():
            start, call_event_id = self.before_request_main(rec, request)

        return rec, start, call_event_id

    @abstractmethod
    def before_request_main(self, rec):
        pass

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

        if DetectEnabled.should_enable("requests"):
            # a) requests
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

        elif DetectEnabled.should_enable("remote"):
            rec = Recorder.get_global()
            if rec.get_enabled():
                self.after_request_main(rec, response, start, call_event_id)

        return response

    @abstractmethod
    def after_request_main(self, rec, response, start, call_event_id):
        pass


def initialize():
    remote_recording.initialize()
