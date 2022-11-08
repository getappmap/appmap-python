import app
import pytest
from django.core.handlers.base import BaseHandler
from django.test import Client


@pytest.mark.parametrize(
    "mware", [["app.middleware.hello_world"], ("app.middleware.hello_world",)]
)
def test_middleware(rf, settings, mware):
    settings.MIDDLEWARE = mware
    orig_type = type(settings.MIDDLEWARE)
    request = rf.get("/_appmap/record")
    handler = BaseHandler()
    handler.load_middleware()
    assert type(settings.MIDDLEWARE) == orig_type
    response = handler.get_response(request)
    assert response.status_code == 200


def test_app(settings):
    response = Client().get("/")

    assert response.status_code == 200
