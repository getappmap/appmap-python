import pytest
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:  # pylint: disable=no-member
        yield client


def test_request(client):
    response = client.get("/")

    assert response.status_code == 200
