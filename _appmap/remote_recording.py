""" remote_recording contains the functions neccessary to implement a remote-recording endpoint. """

import json
from threading import Lock

from . import generation
from .recorder import Recorder

# pylint: disable=global-statement
_enabled_lock = Lock()
_enabled = False


def status():
    with _enabled_lock:
        return json.dumps({"enabled": _enabled}), 200


def start():
    global _enabled
    with _enabled_lock:
        if _enabled:
            return "Recording is already in progress", 409

        Recorder.new_global().start_recording()
        _enabled = True
        return "", 200


def stop():
    global _enabled
    with _enabled_lock:
        if not _enabled:
            return "No recording is in progress", 404
        r = Recorder.get_global()
        r.stop_recording()
        _enabled = False
        return generation.dump(r), 200


def initialize():
    global _enabled
    _enabled = False
