import threading
import time
import traceback
from abc import ABC, abstractmethod

from .env import Env
from .utils import appmap_tls

logger = Env.current.getLogger(__name__)

# pylint: disable=global-statement
_default_recorder = None

# Allow the user to suggest a limit on the number of events that should be added to a Recorder.
# Depending on how exceptions get processed by the framework, there may be some more added, but it
# shouldn't be an enormous number.
_MAX_EVENTS = Env.current.get("APPMAP_MAX_EVENTS")
if _MAX_EVENTS is not None:
    _MAX_EVENTS = int(_MAX_EVENTS)

_MAX_TIME = Env.current.get("APPMAP_MAX_TIME")
if _MAX_TIME is not None:
    _MAX_TIME = int(_MAX_TIME)


class AppMapLimitExceeded(RuntimeError):
    """Class of events thrown when some limit has been exceeded"""


class AppMapTooManyEvents(AppMapLimitExceeded):
    """Thrown when a recorder has more than APPMAP_MAX_EVENTS"""


class AppMapSessionTooLong(AppMapLimitExceeded):
    """Throw when an individual recording session has exceeded APPMAP_MAX_TIME"""


class Recorder(ABC):
    """
    A base class for Recorders.

    Note that the abstract methods have implementations for use by subclasses.
    """

    _aborting = False

    @property
    @abstractmethod
    def events(self):
        return self._events

    _next_event_id = 0
    _next_event_id_lock = threading.Lock()

    @classmethod
    def next_event_id(cls):
        with cls._next_event_id_lock:
            cls._next_event_id += 1
            return cls._next_event_id

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
        tls = appmap_tls()
        if r:
            tls[cls._RECORDER_KEY] = r
        else:
            del tls[cls._RECORDER_KEY]

        return r

    @classmethod
    def get_global(cls):
        _, shared = cls._get_current()
        return shared

    @classmethod
    def new_global(cls):
        global _default_recorder
        _default_recorder = SharedRecorder()
        return _default_recorder

    @classmethod
    def get_enabled(cls):
        return cls.get_current()._enabled  # pylint: disable=protected-access

    @classmethod
    def set_enabled(cls, e):
        cls.get_current()._enabled = e  # pylint: disable=protected-access

    @classmethod
    def start_recording(cls):
        cls.get_current()._start_recording()  # pylint: disable=protected-access

    @classmethod
    def stop_recording(cls):
        return cls.get_current()._stop_recording()  # pylint: disable=protected-access

    @classmethod
    def check_time(cls, event_time):
        if _MAX_TIME is None:
            return
        if event_time - cls.get_current()._start_time > _MAX_TIME:
            raise AppMapSessionTooLong(f"Session exceeded {_MAX_TIME} seconds")

    @classmethod
    def add_event(cls, event):
        """
        Add the given event to the global recorder, as well as the thread's recorder (if it has
        one).
        """
        perthread, shared = cls._get_current()
        shared._add_event(event)  # pylint: disable=protected-access
        if perthread:
            perthread._add_event(event)  # pylint: disable=protected-access

    _RECORDER_KEY = "appmap_recorder"

    @classmethod
    def _get_current(cls):
        perthread = appmap_tls().get(cls._RECORDER_KEY, None)

        return [perthread, _default_recorder]

    def clear(self):
        Recorder._aborting = False
        self._events = []

    def __init__(self, enabled=False):
        self._events = []
        self._enabled = enabled
        self.start_tb = None
        self._start_time = None

    @abstractmethod
    def _start_recording(self):
        logger.debug("AppMap recording started")
        if self._enabled:
            logger.debug("Recording already in progress, previous start:")
            logger.debug("".join(traceback.format_list(self.start_tb)))
            raise RuntimeError("Recording already in progress")
        self.start_tb = traceback.extract_stack()
        self._enabled = True
        self._start_time = time.time()

    @abstractmethod
    def _stop_recording(self):
        logger.debug("AppMap recording stopped")
        self._enabled = False
        self.start_tb = None
        return self._events

    @abstractmethod
    def _add_event(self, event):
        if Recorder._aborting:
            return

        self._events.append(event)
        if _MAX_EVENTS is not None and len(self._events) > _MAX_EVENTS:
            Recorder._aborting = True
            raise AppMapTooManyEvents(f"Session exceeded {_MAX_EVENTS} events")

    @staticmethod
    def _initialize():
        """Create a new default, shared recorder.

        This method is intentionally not thread-safe. It really doesn't make sense have multiple
        threads initializing the default recorder. If you find yourself wanting to do that, you
        should probably be using per-thread recording.
        """
        Recorder.new_global()


class ThreadRecorder(Recorder):
    """
    A Recorder to use for a thread. Not thread-safe, of course.
    """

    @property
    def events(self):
        return super().events

    # They're not useless, because they're abtract with a default implementation
    # pragma pylint: disable=useless-super-delegation
    def _start_recording(self):
        super()._start_recording()

    def _stop_recording(self):
        return super()._stop_recording()

    def _add_event(self, event):
        super()._add_event(event)

    # pragma pylint: enable=useless-super-delegation


class SharedRecorder(Recorder):
    """
    A shared Recorder. The global recorder is an instance of this class.
    """

    _lock = threading.RLock()

    def __init__(self):
        super().__init__()
        Recorder._next_event_id = 0

    def clear(self):
        super().clear()
        Recorder._next_event_id = 0

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

    def _add_event(self, event):
        with self._lock:
            super()._add_event(event)


def initialize():
    Recorder._initialize()  # pylint: disable=protected-access
