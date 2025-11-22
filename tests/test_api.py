import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("PANOPTICON_API_KEY", "test-panopticon")
from panopticon.api.main import app  # noqa: E402

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": os.environ["PANOPTICON_API_KEY"]}


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_stats_endpoint_requires_auth():
    response = client.get("/stats")
    assert response.status_code == 403


def test_stats_endpoint_authorized():
    response = client.get("/stats", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "nodes" in data


def test_search_endpoint_unauthorized():
    response = client.post("/search/person", json={"name": "Test"})
    assert response.status_code == 403


def test_search_endpoint_authorized():
    response = client.post(
        "/search/person", json={"email": "test@example.com"}, headers=AUTH_HEADERS
    )
    assert response.status_code == 200
