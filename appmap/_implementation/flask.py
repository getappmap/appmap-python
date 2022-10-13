""" remote_recording is a Flask app that can be mounted to expose the remote-recording endpoint. """
import json

from flask import Flask

from . import generation
from .recorder import Recorder
from .web_framework import AppmapMiddleware

remote_recording = Flask(__name__)


@remote_recording.route("/record", methods=["GET"])
def status():
    if not AppmapMiddleware.should_record():
        return "Appmap is disabled.", 404

    return {"enabled": Recorder.get_current().get_enabled()}


@remote_recording.route("/record", methods=["POST"])
def start():
    r = Recorder.get_current()
    if r.get_enabled():
        return "Recording is already in progress", 409

    r.start_recording()
    return "", 200


@remote_recording.route("/record", methods=["DELETE"])
def stop():
    r = Recorder.get_current()
    if not r.get_enabled():
        return "No recording is in progress", 404

    r.stop_recording()

    return json.loads(generation.dump(r))
