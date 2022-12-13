import logging

from .env import Env
from .recorder import Recorder

logger = logging.getLogger(__name__)


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
            return False

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
