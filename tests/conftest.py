"""
Test configuration and fixtures for TSH ERP System
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests

# Set required environment variables BEFORE importing app modules
# This prevents Pydantic Settings validation errors during test collection
if "SECRET_KEY" not in os.environ:
    os.environ["SECRET_KEY"] = "test_secret_key_for_ci_testing_only_do_not_use_in_production_environments"
if "JWT_SECRET_KEY" not in os.environ:
    os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_for_ci_testing_only_do_not_use_in_production"

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import Base, DATABASE_URL
from app.services.config_service import SecureConfigService

# Test configuration
BASE_URL = "http://localhost:8000/api"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def engine():
    """Create database engine for testing"""
    test_engine = create_engine(DATABASE_URL)
    
    # Create all tables
    try:
        Base.metadata.create_all(bind=test_engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
    
    yield test_engine
    test_engine.dispose()

@pytest.fixture(scope="session")
def token():
    """Get authentication token for API tests"""
    print("🔐 Getting authentication token...")
    
    login_data = {
        "email": "admin@tsh-erp.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print("✅ Login successful!")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

@pytest.fixture(scope="session") 
def roles(token):
    """Get roles for testing"""
    if not token:
        return []
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/users/roles", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

@pytest.fixture(scope="session")
def branches(token):
    """Get branches for testing"""
    if not token:
        return []
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/users/branches", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

@pytest.fixture(scope="session")
def access_token():
    """Get Zoho access token for API tests"""
    try:
        config_service = SecureConfigService()
        credentials = config_service.get_zoho_credentials()
        if credentials:
            return credentials.access_token
        return None
    except:
        return None

@pytest.fixture(scope="session")
def org_id():
    """Get organization ID for testing"""
    try:
        config_service = SecureConfigService()
        credentials = config_service.get_zoho_credentials()
        if credentials:
            return credentials.organization_id
        return None
    except:
        return None

# Mark all async tests
pytest_plugins = ['pytest_asyncio']
