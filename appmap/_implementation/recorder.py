import logging
import threading
import traceback

from .event import Event, _EventIds
from .metadata import Metadata

logger = logging.getLogger(__name__)


class Recorder:

    # _recorders is a dict of the in-progress recordings. It's keys are an thread-specific
    # recorders, and None if a global recorder was created.
    _recorders = None
    _lock = threading.Lock()

    def __new__(cls, tid=None):
        with cls._lock:
            if cls._recorders is None:
                cls._recorders = {}
            if tid not in cls._recorders:
                recorder = super(Recorder, cls).__new__(cls)

                # Do initialization of the new instance here, rather than in __init__. The latter
                # will be called every time the construct Recorder() is used, but we only want to
                # initialize the instance once.
                recorder.enabled = False
                recorder.start_tb = None
                recorder._events = []
                cls._recorders[tid] = recorder

            return cls._recorders[tid]

    @classmethod
    def initialize(cls):
        cls._recorders = None

    def clear(self):
        self._events = []
        _EventIds.reset()
        Metadata.reset()

    def start_recording(self):
        logger.debug("AppMap recording started")
        if self.enabled:
            logger.error("Recording already in progress, previous start:")
            logger.error("".join(traceback.format_list(self.start_tb)))
            raise RuntimeError("Recording already in progress")
        self.start_tb = traceback.extract_stack()
        self.enabled = True

    def stop_recording(self):
        logger.debug("AppMap recording stopped")
        self.enabled = False
        self.start_tb = None
        return self._events

    @classmethod
    def add_event(cls, event: Event):
        """
        Add the given event to the global recorder, as well as the recorder for the thread
        identified in the event.
        """
        for tid in [None, event.thread_id]:
            if tid in cls._recorders:
                cls._recorders[tid]._add_event(event)

    def _add_event(self, event: Event):
        self._events.append(event)

    @property
    def events(self):
        """
        Get the events from the current recording
        """
        return self._events


def initialize():
    Recorder.initialize()
