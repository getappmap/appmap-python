"""Rudimentary Flask application for testing."""
# pylint: disable=missing-function-docstring

from flask import Flask, make_response
from markupsafe import escape

from appmap.flask import AppmapFlask

app = Flask(__name__)

appmap_flask = AppmapFlask(app)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/test")
def the_test():
    response = make_response("testing")
    response.add_etag()
    return response


@app.route("/user/<username>")
def show_user_profile(username):
    # show the user profile for that user
    return "User %s" % escape(username)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return "Post %d" % post_id


@app.route("/post/<username>/<int:post_id>/summary")
def show_user_post(username, post_id):
    # Show the summary of a user's post
    return f"User {escape(username)} post {post_id}"
