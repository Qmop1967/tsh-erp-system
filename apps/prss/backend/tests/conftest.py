"""Pytest configuration and fixtures"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from prss.main import app
from prss.db import Base, get_db
from prss.models.all_models import User
from prss.models.base import UserRole
from prss.security.auth import get_password_hash

# Test database URL
TEST_DB_URL = "postgresql+psycopg://prss_user:prss_pass@localhost:5432/prss_test_db"

# Create test engine
engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    """Create test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        role=UserRole.ADMIN,
        hashed_password=get_password_hash("testpass123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """Get authentication headers"""
    response = client.post(
        "/v1/auth/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
