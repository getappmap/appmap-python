import logging
import threading
import traceback
from abc import ABC, abstractmethod

from appmap._implementation.utils import appmap_tls

logger = logging.getLogger(__name__)

_default_recorder = None


class Recorder(ABC):
    """
    A base class for Recorders.

    Note that the abstract methods have implementations for use by subclasses.
    """

    @property
    @abstractmethod
    def events(self):
        return self._events

    @abstractmethod
    def next_event_id(self):
        self._next_event_id += 1
        return self._next_event_id

    # It might be nice to put @property on the getters here. The python maintainers have gone back
    # and forth on whether you should be able to combine @classmethod and @property. In 3.11,
    # they've decided you can't: https://docs.python.org/3.11/library/functions.html#classmethod.
    @classmethod
    def get_current(cls):
        """
        Get the recorder for the current thread. If none has been set, return the global, shared
        recorder.
        """
        perthread, shared = cls._get_current()
        return perthread if perthread else shared

    @classmethod
    def set_current(cls, r):
        """
        Set the recorder for the current thread.
        """
        appmap_tls()[cls._RECORDER_KEY] = r
        return r

    @classmethod
    def get_enabled(cls):
        return cls.get_current()._enabled

    @classmethod
    def set_enabled(cls, e):
        cls.get_current()._enabled = e

    @classmethod
    def start_recording(cls):
        cls.get_current()._start_recording()

    @classmethod
    def stop_recording(cls):
        return cls.get_current()._stop_recording()

    @classmethod
    def add_event(cls, event):
        """
        Add the given event to the global recorder, as well as the thread's recorder (if it has
        one).
        """
        perthread, shared = cls._get_current()
        shared._add_event(event)
        if perthread:
            perthread._add_event(event)

    _RECORDER_KEY = "appmap_recorder"

    @classmethod
    def _get_current(cls):
        global _default_recorder
        perthread = appmap_tls().get(cls._RECORDER_KEY, None)

        return [perthread, _default_recorder]

    def clear(self):
        self._events = []
        self._next_event_id = 0

    def __init__(self, enabled=False):
        self._events = []
        self._enabled = enabled
        self.start_tb = None
        self._next_event_id = 0

    @abstractmethod
    def _start_recording(self):
        logger.debug("AppMap recording started")
        if self._enabled:
            logger.error("Recording already in progress, previous start:")
            logger.error("".join(traceback.format_list(self.start_tb)))
            raise RuntimeError("Recording already in progress")
        self.start_tb = traceback.extract_stack()
        self._enabled = True

    @abstractmethod
    def _stop_recording(self):
        logger.debug("AppMap recording stopped")
        self._enabled = False
        self.start_tb = None
        return self._events

    @abstractmethod
    def _add_event(self, event):
        self._events.append(event)

    @staticmethod
    def _initialize():
        """Create a new default, shared recorder.

        This method is intentionally not thread-safe. It really doesn't make sense have multiple
        threads initializing the default recorder. If you find yourself wanting to do that, you
        should probably be using per-thread recording.
        """
        global _default_recorder
        _default_recorder = SharedRecorder()


class ThreadRecorder(Recorder):
    """
    A Recorder to use for a thread. Not thread-safe, of course.
    """

    @property
    def events(self):
        return super().events

    def next_event_id(self):
        return super().next_event_id()

    def _start_recording(self):
        super()._start_recording()

    def _stop_recording(self):
        return super()._stop_recording()

    def _add_event(self, event):
        super()._add_event(event)


class SharedRecorder(Recorder):
    """
    A shared Recorder. The global recorder is an instance of this class.
    """

    _lock = threading.Lock()

    @property
    def events(self):
        with self._lock:
            return super().events

    def _start_recording(self):
        with self._lock:
            super()._start_recording()

    def _stop_recording(self):
        with self._lock:
            return super()._stop_recording()

    def next_event_id(self):
        with self._lock:
            return super().next_event_id()

    def _add_event(self, event):
        with self._lock:
            super()._add_event(event)


def initialize():
    Recorder._initialize()
