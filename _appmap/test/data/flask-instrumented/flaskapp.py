"""
Rudimentary Flask application for testing.
"""
# pylint: disable=missing-function-docstring

import werkzeug
from appmap.flask import AppmapFlask
from flask import Flask, request

app = Flask(__name__)
AppmapFlask(app).init_app()


@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/exception")
def raise_exception():
    raise Exception("An exception")

@app.post("/do_post")
def do_post():
    _ = request.get_json()
    return "Got post request"


@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return "That's a bad request!", 400