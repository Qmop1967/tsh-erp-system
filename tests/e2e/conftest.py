"""
E2E Test Fixtures
=================

Shared fixtures for end-to-end testing.
"""

import os
import pytest
import httpx
from typing import Dict, Generator


# Base URL for API requests
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def api_client() -> Generator[httpx.Client, None, None]:
    """HTTP client for API requests"""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
def admin_token(api_client: httpx.Client) -> str:
    """Authenticate as admin and return JWT token"""
    response = api_client.post(
        "/api/auth/login",
        json={
            "email": "admin@tsh.sale",
            "password": "admin123"  # Default admin password from seed
        }
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="session")
def manager_token(api_client: httpx.Client) -> str:
    """Authenticate as manager and return JWT token"""
    response = api_client.post(
        "/api/auth/login",
        json={
            "email": "manager@tsh.sale",
            "password": "manager123"  # Default manager password from seed
        }
    )
    assert response.status_code == 200, f"Manager login failed: {response.text}"
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="session")
def salesperson_token(api_client: httpx.Client) -> str:
    """Authenticate as salesperson and return JWT token"""
    response = api_client.post(
        "/api/auth/login",
        json={
            "email": "sales@tsh.sale",
            "password": "sales123"  # Default salesperson password from seed
        }
    )
    assert response.status_code == 200, f"Salesperson login failed: {response.text}"
    data = response.json()
    return data["access_token"]


@pytest.fixture
def auth_headers(admin_token: str) -> Dict[str, str]:
    """Authentication headers with admin token"""
    return {
        "Authorization": f"Bearer {admin_token}"
    }


@pytest.fixture
def manager_headers(manager_token: str) -> Dict[str, str]:
    """Authentication headers with manager token"""
    return {
        "Authorization": f"Bearer {manager_token}"
    }


@pytest.fixture
def salesperson_headers(salesperson_token: str) -> Dict[str, str]:
    """Authentication headers with salesperson token"""
    return {
        "Authorization": f"Bearer {salesperson_token}"
    }
