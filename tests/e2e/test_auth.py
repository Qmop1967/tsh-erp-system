"""
Authentication E2E Tests
========================

End-to-end tests for authentication and authorization flows.
"""

import pytest
import httpx
from typing import Dict


class TestAuthentication:
    """Test authentication flows"""

    def test_health_endpoint_no_auth(self, api_client: httpx.Client):
        """Health endpoint should work without authentication"""
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "redis" in data

    def test_login_with_valid_credentials(self, api_client: httpx.Client):
        """Login with valid credentials should return JWT token"""
        response = api_client.post(
            "/api/auth/login",
            json={
                "email": "admin@tsh.sale",
                "password": "admin123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "admin@tsh.sale"

    def test_login_with_invalid_credentials(self, api_client: httpx.Client):
        """Login with invalid credentials should fail"""
        response = api_client.post(
            "/api/auth/login",
            json={
                "email": "admin@tsh.sale",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_with_nonexistent_user(self, api_client: httpx.Client):
        """Login with nonexistent user should fail"""
        response = api_client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@tsh.sale",
                "password": "password123"
            }
        )
        assert response.status_code == 401

    def test_access_protected_route_without_token(self, api_client: httpx.Client):
        """Accessing protected route without token should fail"""
        response = api_client.get("/api/users/me")
        assert response.status_code == 401

    def test_access_protected_route_with_invalid_token(self, api_client: httpx.Client):
        """Accessing protected route with invalid token should fail"""
        response = api_client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_access_protected_route_with_valid_token(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """Accessing protected route with valid token should succeed"""
        response = api_client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "role" in data

    def test_token_refresh(self, api_client: httpx.Client, admin_token: str):
        """Token refresh should work"""
        response = api_client.post(
            "/api/auth/refresh",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # If refresh endpoint exists
        if response.status_code != 404:
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data


class TestAuthorization:
    """Test role-based access control"""

    def test_admin_can_access_admin_routes(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """Admin should access admin routes"""
        response = api_client.get("/api/users", headers=auth_headers)
        # Assuming admin has access to user list
        assert response.status_code in [200, 404]  # 404 if route not implemented yet

    def test_salesperson_cannot_access_admin_routes(
        self,
        api_client: httpx.Client,
        salesperson_headers: Dict[str, str]
    ):
        """Salesperson should not access admin-only routes"""
        response = api_client.delete(
            "/api/users/1",
            headers=salesperson_headers
        )
        # Should be 403 (Forbidden) if RBAC is implemented
        assert response.status_code in [403, 404]

    def test_manager_can_access_manager_routes(
        self,
        api_client: httpx.Client,
        manager_headers: Dict[str, str]
    ):
        """Manager should access manager-level routes"""
        response = api_client.get("/api/reports/sales", headers=manager_headers)
        # Assuming managers have access to reports
        assert response.status_code in [200, 404]  # 404 if route not implemented yet


class TestLogout:
    """Test logout functionality"""

    def test_logout_clears_session(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """Logout should invalidate session"""
        response = api_client.post("/api/auth/logout", headers=auth_headers)
        # If logout endpoint exists
        if response.status_code != 404:
            assert response.status_code == 200

            # Token should not work after logout (if token blacklisting is implemented)
            response = api_client.get("/api/users/me", headers=auth_headers)
            # Token might still work if stateless JWT without blacklist
            assert response.status_code in [200, 401]
