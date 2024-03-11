import pytest
from fastapi.testclient import TestClient
from fastapiapp import app


@pytest.fixture
def client():
    yield TestClient(app)


def test_request(client):
    response = client.get("/")

    assert response.status_code == 200
