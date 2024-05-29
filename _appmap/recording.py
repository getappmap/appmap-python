import atexit
import os
from datetime import datetime, timezone
from tempfile import NamedTemporaryFile

from _appmap import generation
from _appmap.web_framework import APPMAP_SUFFIX, HASH_LEN, NAME_MAX, name_hash

from .env import Env
from .recorder import Recorder

logger = Env.current.getLogger(__name__)


class Recording:
    """
    Context manager to make it easy to capture a Recording.  exit_hook
    will be called when the block exits, before any exceptions are
    raised.
    """

    def __init__(self, exit_hook=None):
        self.events = []
        self.exit_hook = exit_hook

    def start(self):
        if not Env.current.enabled:
            return

        r = Recorder.get_current()
        r.clear()
        r.start_recording()

    def stop(self):
        if not Env.current.enabled:
            return

        self.events += Recorder.stop_recording()

    def is_running(self):
        if not Env.current.enabled:
            return False

        return Recorder.get_enabled()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, tb):
        logger.debug("Recording.__exit__, stopping with exception %s", exc_type)
        self.stop()
        if self.exit_hook is not None:
            self.exit_hook(self)
        return False


class NoopRecording:
    """
    A noop context manager to export as "Recording" instead of class
    Recording when not Env.current.enabled.
    """

    def __init__(self, exit_hook=None):
        self.exit_hook = exit_hook

    def start(self):
        pass

    def stop(self):
        pass

    def is_running(self):
        return False

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, tb):
        if self.exit_hook is not None:
            self.exit_hook(self)
        return False


def write_appmap(
    appmap, appmap_fname, recorder_type, metadata=None, basedir=Env.current.output_dir
):
    """Write an appmap file into basedir.

    Adds APPMAP_SUFFIX to basename; shortens the name if necessary.
    Atomically replaces existing files. Creates the basedir if required.
    """

    if len(appmap_fname) > NAME_MAX - len(APPMAP_SUFFIX):
        part = NAME_MAX - len(APPMAP_SUFFIX) - 1 - HASH_LEN
        appmap_fname = appmap_fname[:part] + "-" + name_hash(appmap_fname[part:])[:HASH_LEN]
    filename = appmap_fname + APPMAP_SUFFIX

    basedir = basedir / recorder_type
    basedir.mkdir(parents=True, exist_ok=True)

    with NamedTemporaryFile(mode="w", dir=basedir, delete=False) as tmp:
        tmp.write(generation.dump(appmap, metadata))
    appmap_file = basedir / filename
    logger.info("writing %s", appmap_file)
    os.replace(tmp.name, appmap_file)


def initialize():
    if Env.current.enables("process", Env.RECORD_PROCESS_DEFAULT):
        r = Recording()
        r.start()

        def save_at_exit():
            nonlocal r
            r.stop()
            now = datetime.now(timezone.utc)
            appmap_name = now.isoformat(timespec="seconds").replace("+00:00", "Z")
            recorder_type = "process"
            metadata = {
                "name": appmap_name,
                "recorder": {
                    "name": "process",
                    "type": recorder_type,
                },
            }
            write_appmap(r, appmap_name, recorder_type, metadata)

        atexit.register(save_at_exit)
