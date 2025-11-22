from fastapi.testclient import TestClient
from panopticon.api.main import app
import pytest

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "nodes" in data

def test_search_endpoint_unauthorized():
    # Should allow but log warning (mock auth)
    response = client.post("/search/person", json={"name": "Test"})
    assert response.status_code == 200

def test_search_endpoint_authorized():
    headers = {"X-API-Key": "panopticon-secret"}
    response = client.post("/search/person", json={"email": "test@example.com"}, headers=headers)
    assert response.status_code == 200
