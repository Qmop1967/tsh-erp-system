# TDS Integration Tests

Tests for TDS unified Zoho integration

## Structure

```
tests/tds/
├── conftest.py                     # Test fixtures and configuration
├── test_stock_sync.py              # Stock sync service tests
├── test_zoho_bulk_sync_router.py   # Router endpoint tests
└── README.md                        # This file
```

## Running Tests

### Unit Tests (Fast, No Credentials Required)
```bash
# All unit tests
pytest tests/tds/ -m unit -v

# Stock sync tests only
pytest tests/tds/test_stock_sync.py -m unit -v

# Router tests only
pytest tests/tds/test_zoho_bulk_sync_router.py -m unit -v
```

### Integration Tests (Requires Zoho Credentials)
```bash
# All integration tests
pytest tests/tds/ -m integration -v

# Specific integration test
pytest tests/tds/test_stock_sync.py::test_real_stock_summary -v
```

### With Coverage
```bash
# Generate coverage report
pytest tests/tds/ --cov=app/tds/integrations/zoho --cov-report=html

# View report
open htmlcov/index.html
```

## Environment Variables

Integration tests require valid Zoho credentials:

```bash
export ZOHO_CLIENT_ID="your_client_id"
export ZOHO_CLIENT_SECRET="your_client_secret"
export ZOHO_REFRESH_TOKEN="your_refresh_token"
export ZOHO_ORGANIZATION_ID="your_org_id"
```

## Test Markers

- `@pytest.mark.unit` - Fast unit tests with mocks
- `@pytest.mark.integration` - Integration tests with real API
- `@pytest.mark.requires_credentials` - Requires valid Zoho credentials

## Fixtures

See `conftest.py` for available fixtures:

**Mock Fixtures:**
- `mock_zoho_items` - Sample inventory items
- `mock_zoho_products` - Sample products
- `mock_zoho_customers` - Sample customers
- `mock_auth_manager` - Mocked auth manager
- `mock_zoho_client` - Mocked Zoho client
- `mock_orchestrator` - Mocked sync orchestrator
- `mock_stock_sync` - Mocked stock sync service

**Real Fixtures (require credentials):**
- `real_auth_manager` - Real auth manager
- `real_zoho_client` - Real Zoho client
- `real_orchestrator` - Real sync orchestrator
- `real_stock_sync` - Real stock sync service

## Writing New Tests

### Unit Test Example
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_my_feature(mock_stock_sync):
    """Test my feature with mocks"""
    result = await mock_stock_sync.my_method()
    assert result is not None
```

### Integration Test Example
```python
@pytest.mark.integration
@pytest.mark.requires_credentials
@pytest.mark.asyncio
async def test_my_feature_real(skip_if_no_credentials, real_stock_sync):
    """Test my feature with real API"""
    result = await real_stock_sync.my_method()
    assert result is not None
```

## CI/CD

Recommended CI pipeline runs unit tests only:

```yaml
pytest tests/tds/ -m unit --cov=app/tds --cov-report=xml
```

Integration tests should run in a separate job with credentials.
