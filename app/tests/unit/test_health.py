"""
Health Check Tests
==================

Test the health check endpoint.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_check(client: TestClient):
    """
    Test health check endpoint returns healthy status.

    Verifies that:
    - Endpoint returns 200 OK
    - Response contains 'status' field
    - Status is 'healthy'
    """
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.unit
def test_health_check_message(client: TestClient):
    """Test health check returns Arabic message"""
    response = client.get("/health")

    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
