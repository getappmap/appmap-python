"""
This file contains a FastAPI app that is mounted on /_appmap to expose the remote-recording endpoint
in a user's app.

It should only be imported if other code has already verified that FastAPI is available.
"""

from fastapi import FastAPI, Response

from . import remote_recording

app = FastAPI()


def _rr_response(fn):
    body, rrstatus = fn()
    return Response(content=body, status_code=rrstatus, media_type="application/json")


@app.get("/record")
def status():
    return _rr_response(remote_recording.status)


@app.post("/record")
def start():
    return _rr_response(remote_recording.start)


@app.delete("/record")
def stop():
    return _rr_response(remote_recording.stop)
