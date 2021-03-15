from flask import Flask
from markupsafe import escape

from appmap.flask import AppmapFlask


app = Flask(__name__)

appmap_flask = AppmapFlask(app)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % escape(username)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id
