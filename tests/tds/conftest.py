"""
TDS Integration Tests - Fixtures and Configuration

Test fixtures for TDS unified Zoho integration
"""
import pytest
import asyncio
import os
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

from app.tds.integrations.zoho import (
    UnifiedZohoClient,
    ZohoAuthManager,
    ZohoSyncOrchestrator,
    ZohoCredentials,
    UnifiedStockSyncService,
    StockSyncConfig
)
from app.core.event_bus import EventBus


# ============================================================================
# Test Configuration
# ============================================================================

TEST_CREDENTIALS = ZohoCredentials(
    client_id=os.getenv('ZOHO_CLIENT_ID', 'test_client_id'),
    client_secret=os.getenv('ZOHO_CLIENT_SECRET', 'test_client_secret'),
    refresh_token=os.getenv('ZOHO_REFRESH_TOKEN', 'test_refresh_token'),
    organization_id=os.getenv('ZOHO_ORGANIZATION_ID', 'test_org_id')
)


# ============================================================================
# Event Loop
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Mock Data
# ============================================================================

@pytest.fixture
def mock_zoho_items():
    """Mock Zoho inventory items response"""
    return {
        "code": 0,
        "message": "success",
        "items": [
            {
                "item_id": "2646610000000001",
                "name": "Test Product 1",
                "sku": "TEST-001",
                "stock_on_hand": 100,
                "available_stock": 95,
                "warehouse_id": "warehouse_001",
                "warehouse_name": "Main Warehouse",
                "status": "active",
                "last_modified_time": "2025-11-06T10:00:00+0300"
            },
            {
                "item_id": "2646610000000002",
                "name": "Test Product 2",
                "sku": "TEST-002",
                "stock_on_hand": 50,
                "available_stock": 45,
                "warehouse_id": "warehouse_001",
                "warehouse_name": "Main Warehouse",
                "status": "active",
                "last_modified_time": "2025-11-06T10:00:00+0300"
            },
            {
                "item_id": "2646610000000003",
                "name": "Test Product 3 (Low Stock)",
                "sku": "TEST-003",
                "stock_on_hand": 5,
                "available_stock": 5,
                "warehouse_id": "warehouse_001",
                "warehouse_name": "Main Warehouse",
                "status": "active",
                "last_modified_time": "2025-11-06T10:00:00+0300"
            }
        ],
        "page_context": {
            "page": 1,
            "per_page": 200,
            "has_more_page": False,
            "total": 3
        }
    }


@pytest.fixture
def mock_zoho_products():
    """Mock Zoho products response"""
    return {
        "code": 0,
        "message": "success",
        "items": [
            {
                "item_id": "2646610000000001",
                "name": "Test Product 1",
                "sku": "TEST-001",
                "status": "active",
                "unit": "pcs",
                "rate": 10.00,
                "stock_on_hand": 100
            },
            {
                "item_id": "2646610000000002",
                "name": "Test Product 2",
                "sku": "TEST-002",
                "status": "active",
                "unit": "pcs",
                "rate": 20.00,
                "stock_on_hand": 50
            }
        ],
        "page_context": {
            "page": 1,
            "per_page": 200,
            "has_more_page": False,
            "total": 2
        }
    }


@pytest.fixture
def mock_zoho_customers():
    """Mock Zoho customers response"""
    return {
        "code": 0,
        "message": "success",
        "contacts": [
            {
                "contact_id": "3646610000000001",
                "contact_name": "Test Customer 1",
                "email": "customer1@test.com",
                "phone": "+966501234567",
                "status": "active"
            },
            {
                "contact_id": "3646610000000002",
                "contact_name": "Test Customer 2",
                "email": "customer2@test.com",
                "phone": "+966507654321",
                "status": "active"
            }
        ],
        "page_context": {
            "page": 1,
            "per_page": 200,
            "has_more_page": False,
            "total": 2
        }
    }


# ============================================================================
# Event Bus
# ============================================================================

@pytest.fixture
def event_bus():
    """Create event bus for testing"""
    return EventBus()


# ============================================================================
# TDS Components - Mocked
# ============================================================================

@pytest.fixture
async def mock_auth_manager(event_bus):
    """Create mock auth manager"""
    auth = AsyncMock(spec=ZohoAuthManager)
    auth.get_valid_token = AsyncMock(return_value="test_access_token")
    auth.refresh_access_token = AsyncMock(return_value="test_access_token")
    auth.start = AsyncMock()
    auth.stop = AsyncMock()
    return auth


@pytest.fixture
async def mock_zoho_client(mock_auth_manager, event_bus, mock_zoho_items):
    """Create mock Zoho client"""
    client = AsyncMock(spec=UnifiedZohoClient)

    # Mock methods
    client.get = AsyncMock(return_value=mock_zoho_items)
    client.post = AsyncMock(return_value={"code": 0, "message": "success"})
    client.put = AsyncMock(return_value={"code": 0, "message": "success"})
    client.delete = AsyncMock(return_value={"code": 0, "message": "success"})
    client.paginated_fetch = AsyncMock(return_value=mock_zoho_items["items"])
    client.batch_request = AsyncMock(return_value=[])
    client.start_session = AsyncMock()
    client.close_session = AsyncMock()

    return client


@pytest.fixture
async def mock_orchestrator(mock_zoho_client, event_bus):
    """Create mock sync orchestrator"""
    from app.tds.integrations.zoho.sync import SyncResult, SyncStatus
    from datetime import datetime, timedelta

    orchestrator = AsyncMock(spec=ZohoSyncOrchestrator)

    # Mock sync result
    mock_result = SyncResult(
        sync_id="test_sync_001",
        entity_type="products",
        status=SyncStatus.COMPLETED,
        mode="full",
        total_processed=3,
        total_success=3,
        total_failed=0,
        total_skipped=0,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow() + timedelta(seconds=10),
        duration=timedelta(seconds=10)
    )

    orchestrator.sync_entity = AsyncMock(return_value=mock_result)

    return orchestrator


# ============================================================================
# TDS Components - Real (for integration tests)
# ============================================================================

@pytest.fixture
async def real_auth_manager(event_bus):
    """Create real auth manager (requires valid credentials)"""
    auth = ZohoAuthManager(
        credentials=TEST_CREDENTIALS,
        auto_refresh=True,
        event_bus=event_bus
    )
    await auth.start()
    yield auth
    await auth.stop()


@pytest.fixture
async def real_zoho_client(real_auth_manager, event_bus):
    """Create real Zoho client (requires valid credentials)"""
    client = UnifiedZohoClient(
        auth_manager=real_auth_manager,
        organization_id=TEST_CREDENTIALS.organization_id,
        rate_limit=100,
        event_bus=event_bus
    )
    await client.start_session()
    yield client
    await client.close_session()


@pytest.fixture
async def real_orchestrator(real_zoho_client, event_bus):
    """Create real sync orchestrator (requires valid credentials)"""
    orchestrator = ZohoSyncOrchestrator(
        zoho_client=real_zoho_client,
        event_bus=event_bus
    )
    return orchestrator


@pytest.fixture
async def real_stock_sync(real_zoho_client, real_orchestrator, event_bus):
    """Create real stock sync service (requires valid credentials)"""
    service = UnifiedStockSyncService(
        zoho_client=real_zoho_client,
        sync_orchestrator=real_orchestrator,
        event_bus=event_bus
    )
    return service


# ============================================================================
# Stock Sync Service - Mocked
# ============================================================================

@pytest.fixture
async def mock_stock_sync(mock_zoho_client, mock_orchestrator, event_bus):
    """Create mock stock sync service"""
    service = UnifiedStockSyncService(
        zoho_client=mock_zoho_client,
        sync_orchestrator=mock_orchestrator,
        event_bus=event_bus
    )
    return service


# ============================================================================
# Test Markers
# ============================================================================

def pytest_configure(config):
    """Register custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast)"
    )
    config.addinivalue_line(
        "markers", "requires_credentials: marks tests that require real Zoho credentials"
    )


# ============================================================================
# Test Helpers
# ============================================================================

def has_valid_credentials():
    """Check if valid Zoho credentials are available"""
    return all([
        os.getenv('ZOHO_CLIENT_ID'),
        os.getenv('ZOHO_CLIENT_SECRET'),
        os.getenv('ZOHO_REFRESH_TOKEN'),
        os.getenv('ZOHO_ORGANIZATION_ID')
    ])


@pytest.fixture
def skip_if_no_credentials():
    """Skip test if no valid credentials"""
    if not has_valid_credentials():
        pytest.skip("Requires valid Zoho credentials")
