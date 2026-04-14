"""
Rudimentary FastAPI application for testing.

NB: This should not explicitly reference the `appmap` module in any way. Doing so invalidates
testing of record-by-default.
"""
# pylint: disable=missing-function-docstring

from typing import List

from fastapi import FastAPI, Query, Request, Response

app = FastAPI()


@app.get("/")
def hello_world():
    return {"Hello": "World!"}


@app.post("/echo")
async def echo(request: Request):
    body = await request.body()
    return Response(content=body, media_type="application/json")


@app.get("/test")
async def get_test(my_params: List[str] = Query(None)):
    response = Response(content="testing", media_type="text/html; charset=utf-8")
    response.headers["ETag"] = "W/01"
    return response


@app.post("/test")
async def post_test(request: Request):
    await request.json()
    response = Response(content='{"test":true}', media_type="application/json")
    response.headers["ETag"] = "W/01"
    return response


@app.get("/user/{username}")
def get_user_profile(username):
    # show the user profile for that user
    return {"user": username}


@app.get("/post/{post_id:int}")
def get_post(post_id):
    # show the post with the given id, the id is an integer
    return {"post": post_id}


@app.get("/post/{username}/{post_id:int}/summary")
def get_user_post(username, post_id):
    # Show the summary of a user's post
    return {"user": username, "post": post_id}


@app.get("/{org:int}/posts/{username}")
def get_org_user_posts(org, username):
    return {"org": org, "username": username}


@app.get("/exception")
def raise_exception():
    raise Exception("An exception")
