import app
from django.core.handlers.base import BaseHandler
from django.test import Client


def test_middleware(rf, settings):
    settings.MIDDLEWARE = ["app.middleware.hello_world"]
    request = rf.get("/")
    handler = BaseHandler()
    handler.load_middleware()
    response = handler.get_response(request)
    assert response.status_code == 200


def test_app(settings):
    response = Client().get("/")

    assert response.status_code == 200
