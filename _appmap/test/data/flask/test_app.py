import pytest
from flaskapp import app


@pytest.fixture(name="client")
def test_client():
    with app.test_client() as c:  # pylint: disable=no-member
        yield c


def test_request(client):
    response = client.get("/")

    assert response.status_code == 200
