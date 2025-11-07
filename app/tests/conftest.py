"""
Test Configuration and Fixtures
================================

Provides common fixtures and utilities for testing TSH ERP backend.
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.models import User, Role, Branch, Customer, Product

# Test database URL (SQLite in-memory for fast tests)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with special settings for SQLite
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Use static pool for in-memory database
)

# Enable foreign keys for SQLite
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Fixtures

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a test database session.

    Creates all tables before test and drops them after.
    Each test gets a fresh database.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Drop all tables
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with test database.

    Overrides the get_db dependency to use test database.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def test_branch(db_session: Session) -> Branch:
    """Create a test branch"""
    branch = Branch(
        name="Test Branch",
        code="TEST01",
        location="Test Location",
        is_active=True
    )
    db_session.add(branch)
    db_session.commit()
    db_session.refresh(branch)
    return branch


@pytest.fixture
def test_role(db_session: Session) -> Role:
    """Create a test role"""
    role = Role(
        name="Test Role",
        description="Test role for testing"
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def test_user_data():
    """Test user data dictionary"""
    return {
        "email": "test@tsh.sale",
        "password": "testpassword123",
        "name": "Test User",
        "full_name": "Test User Full Name"
    }


@pytest.fixture
def test_user(db_session: Session, test_role: Role, test_branch: Branch, test_user_data: dict) -> User:
    """Create a test user"""
    from app.utils.hashing import get_password_hash

    user = User(
        email=test_user_data["email"],
        password=get_password_hash(test_user_data["password"]),
        name=test_user_data["name"],
        full_name=test_user_data["full_name"],
        role_id=test_role.id,
        branch_id=test_branch.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client: TestClient, test_user: User, test_user_data: dict) -> TestClient:
    """
    Create an authenticated test client.

    Logs in the test user and adds Authorization header.
    """
    # Login
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")

        if access_token:
            # Add Authorization header
            client.headers.update({"Authorization": f"Bearer {access_token}"})

    return client


@pytest.fixture
def test_customer(db_session: Session, test_branch: Branch) -> Customer:
    """Create a test customer"""
    customer = Customer(
        name="Test Customer",
        email="customer@test.com",
        phone="1234567890",
        branch_id=test_branch.id,
        is_active=True
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def test_product(db_session: Session, test_branch: Branch) -> Product:
    """Create a test product"""
    product = Product(
        name="Test Product",
        sku="TEST-001",
        price=100.0,
        cost=50.0,
        branch_id=test_branch.id,
        is_active=True,
        stock_quantity=100
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


# Async fixtures for async tests

@pytest.fixture
async def async_client() -> AsyncGenerator[TestClient, None]:
    """Create an async test client"""
    async with TestClient(app) as ac:
        yield ac


# Pytest configuration

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers based on test location
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
