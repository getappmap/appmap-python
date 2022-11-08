"""
This file contains a Flask app that is mounted on /_appmap to expose the remote-recording endpoint
in a user's app.

It should only be imported if other code has already verified that Flask is available.
"""

from flask import Flask, Response

from . import remote_recording

app = Flask(__name__)


@app.route("/record", methods=["GET"])
def status():
    body, rrstatus = remote_recording.status()
    return Response(body, status=rrstatus, mimetype="application/json")


@app.route("/record", methods=["POST"])
def start():
    body, rrstatus = remote_recording.start()
    return Response(body, status=rrstatus, mimetype="application/json")


@app.route("/record", methods=["DELETE"])
def stop():
    body, rrstatus = remote_recording.stop()
    return Response(body, status=rrstatus, mimetype="application/json")
