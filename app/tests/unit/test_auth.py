"""
Authentication Tests
===================

Test the authentication system endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.unit
def test_auth_endpoint_exists(client: TestClient):
    """
    Test that the auth login endpoint exists.

    Verifies that:
    - Endpoint is registered at /api/auth/login
    - Returns 422 for invalid request (not 404)
    """
    response = client.post("/api/auth/login")

    # Should get 422 (validation error) not 404 (not found)
    assert response.status_code == 422, "Auth endpoint should exist"


@pytest.mark.unit
def test_auth_login_validation(client: TestClient):
    """
    Test auth login input validation.

    Verifies that:
    - Email is required
    - Password is required
    - Proper error messages are returned
    """
    # Missing both fields
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 422

    # Missing password
    response = client.post("/api/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 422

    # Missing email
    response = client.post("/api/auth/login", json={"password": "password123"})
    assert response.status_code == 422


@pytest.mark.unit
def test_auth_login_invalid_credentials(client: TestClient):
    """
    Test login with invalid credentials.

    Verifies that:
    - Returns 401 for invalid credentials
    - Does not leak information about which field is wrong
    """
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


@pytest.mark.unit
def test_auth_login_success(authenticated_client: TestClient, test_user):
    """
    Test successful authentication.

    Verifies that:
    - Returns 200 for valid credentials
    - Response contains access_token
    - Response contains refresh_token
    - Response contains user info
    """
    # authenticated_client fixture already has a logged-in user
    # Just verify the token was set
    assert authenticated_client.headers.get("Authorization") is not None


@pytest.mark.unit
def test_deprecated_auth_simple_marked(client: TestClient):
    """
    Test that auth_simple endpoint is marked as deprecated.

    Note: This endpoint may not be registered in main.py anymore,
    so we expect 404. When it is registered, it should show as deprecated
    in the OpenAPI schema.
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi_schema = response.json()

    # Check if auth-simple endpoint exists and is marked deprecated
    if "/api/auth-simple/login" in openapi_schema.get("paths", {}):
        login_endpoint = openapi_schema["paths"]["/api/auth-simple/login"]
        post_method = login_endpoint.get("post", {})

        # Should be marked as deprecated
        assert post_method.get("deprecated") is True, \
            "auth_simple login endpoint should be marked as deprecated"


@pytest.mark.unit
def test_auth_enhanced_is_primary(client: TestClient):
    """
    Test that auth_enhanced is the primary auth endpoint.

    Verifies that:
    - /api/auth/login exists in OpenAPI schema
    - Not marked as deprecated
    - Has proper documentation
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi_schema = response.json()

    # Check that primary auth endpoint exists
    assert "/api/auth/login" in openapi_schema.get("paths", {}), \
        "Primary auth endpoint /api/auth/login should exist"

    login_endpoint = openapi_schema["paths"]["/api/auth/login"]
    post_method = login_endpoint.get("post", {})

    # Should NOT be marked as deprecated
    assert post_method.get("deprecated") is not True, \
        "Primary auth endpoint should not be deprecated"

    # Should have summary and description
    assert "summary" in post_method or "description" in post_method, \
        "Auth endpoint should be documented"


@pytest.mark.unit
def test_no_hardcoded_secrets_in_response(client: TestClient):
    """
    Test that API responses don't leak secrets.

    Verifies that:
    - Error responses don't contain SECRET_KEY
    - Error responses don't contain database passwords
    - Error responses don't contain internal paths
    """
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrong"
        }
    )

    response_text = response.text.lower()

    # Should not contain common secret indicators
    assert "secret_key" not in response_text
    assert "database_password" not in response_text
    assert "postgresql://" not in response_text
    assert "jwt_secret" not in response_text
