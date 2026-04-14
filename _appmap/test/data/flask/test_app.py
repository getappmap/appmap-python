import pytest
from flaskapp import app


@pytest.fixture(name="client")
def test_client():
    with app.test_client() as c:  # pylint: disable=no-member
        yield c


def test_request(client):
    response = client.get("/")

    assert response.status_code == 200

def test_not_found(client):
    response = client.get("/not_found")

    assert response.status_code == 404


def test_errorhandler(client):
    response = client.post("/do_post", content_type="application/json")

    assert response.status_code == 400
    assert response.text == "That's a bad request!"
