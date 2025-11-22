import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("PANOPTICON_API_KEY", "test-panopticon")
from panopticon.api.main import app  # noqa: E402

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": os.environ["PANOPTICON_API_KEY"]}

def test_sql_injection_attempt():
    """Test API resilience against SQL/Cypher injection strings."""
    # We rely on parameterized queries in the backend, let's ensure 200 OK (handled) or 422 (validation)
    # but definitely NOT 500 Internal Server Error
    payload = {"username": "' OR 1=1 --"}
    response = client.post("/search/person", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    # Result should ideally be empty, not the entire DB
    data = response.json()
    assert len(data['matches']) == 0

def test_huge_payload():
    """Test API behavior with massive input strings (Buffer Overflow attempt)."""
    huge_str = "A" * 100000
    payload = {"email": f"{huge_str}@example.com"}
    response = client.post("/search/person", json=payload, headers=AUTH_HEADERS)
    # Should be handled by Pydantic or Nginx limits, but app shouldn't crash
    assert response.status_code in [200, 422]

def test_malformed_json():
    """Test API behavior with invalid JSON."""
    response = client.post("/search/person", content="{broken_json:", headers=AUTH_HEADERS)
    assert response.status_code == 422 # Unprocessable Entity
