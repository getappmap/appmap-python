import pytest
from django.core.handlers.base import BaseHandler


@pytest.mark.parametrize(
    "mware",
    [["app.middleware.hello_world"], ("app.middleware.hello_world",)],
)
def test_middleware_iterable_with_reset(client, settings, mware):
    """
    Test that we can update the middleware, whatever type of iterable it may be (Django doesn't
    care).
    """
    settings.DEBUG = True
    settings.MIDDLEWARE = mware
    orig_type = type(settings.MIDDLEWARE)
    response = client.get("/_appmap/record")
    handler = BaseHandler()
    handler.load_middleware()
    assert type(settings.MIDDLEWARE) == orig_type
    assert response.status_code == 200


def test_request(client):
    response = client.get("/")

    assert response.status_code == 200


def test_remote_disabled_in_prod(client, settings):
    settings.DEBUG = False
    response = client.get("/_appmap/record")
    assert response.status_code == 404
