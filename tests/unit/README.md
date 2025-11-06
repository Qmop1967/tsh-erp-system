# Unit Tests - TSH ERP System

## Overview

Unit tests for TSH ERP core functionality. These tests are:
- **Fast** - No database or external services required
- **Isolated** - Test one component at a time
- **Deterministic** - Same input always produces same output
- **Independent** - Tests can run in any order

## Test Structure

```
tests/unit/
├── README.md (this file)
├── test_auth_dependencies.py      # Phase 1: Auth consolidation tests (16 tests)
└── test_tds_zoho_service.py       # Phase 2: TDS Zoho consolidation tests (19 tests)
```

## Running Tests

### Run All Unit Tests
```bash
pytest tests/unit/ -v
```

### Run Specific Test File
```bash
pytest tests/unit/test_auth_dependencies.py -v
pytest tests/unit/test_tds_zoho_service.py -v
```

### Run With Coverage
```bash
pytest tests/unit/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Run Specific Test Class
```bash
pytest tests/unit/test_auth_dependencies.py::TestGetUserPermissions -v
pytest tests/unit/test_tds_zoho_service.py::TestZohoServiceSyncOperations -v
```

### Run Specific Test
```bash
pytest tests/unit/test_auth_dependencies.py::TestGetUserPermissions::test_admin_permissions -v
```

## Test Coverage

### Phase 1: Authentication Dependencies (`test_auth_dependencies.py`)
**16 tests covering:**
- ✅ Role-based permissions (all 7 roles)
- ✅ Role name normalization
- ✅ Token validation
- ✅ Blacklist checking
- ✅ Inactive user handling
- ✅ Full auth flow
- ✅ Performance

**Validates:**
- Consolidation of 3 auth implementations into 1
- `app/dependencies/auth.py` works correctly
- No functionality lost in refactoring

### Phase 2: TDS Zoho Integration (`test_tds_zoho_service.py`)
**19 tests covering:**
- ✅ Service initialization
- ✅ Start/stop lifecycle
- ✅ Sync operations (products, customers, inventory)
- ✅ Webhook processing
- ✅ API operations
- ✅ Auth operations
- ✅ Monitoring
- ✅ Error handling

**Validates:**
- Consolidation of 15 Zoho services into 1 facade
- `app/tds/zoho.py` provides all legacy functionality
- TDS architecture works correctly

## Test Patterns

### Mocking External Dependencies
```python
@patch('app.dependencies.auth.TokenBlacklistService')
@patch('app.dependencies.auth.AuthService')
def test_with_mocks(mock_auth_service, mock_blacklist_service):
    # Arrange
    mock_auth_service.get_current_user.return_value = mock_user

    # Act
    result = function_under_test()

    # Assert
    mock_auth_service.get_current_user.assert_called_once()
```

### Async Tests
```python
@pytest.mark.asyncio
async def test_async_function():
    # Arrange
    service = ZohoService(credentials=mock_credentials)

    # Act
    result = await service.sync_products()

    # Assert
    assert result is not None
```

### Fixtures
```python
@pytest.fixture
def zoho_credentials():
    return ZohoCredentials(
        client_id="test",
        client_secret="test",
        refresh_token="test",
        organization_id="test"
    )

def test_with_fixture(zoho_credentials):
    service = ZohoService(credentials=zoho_credentials)
    assert service.credentials == zoho_credentials
```

## Test Naming Conventions

- **Test Classes**: `TestFeatureName`
- **Test Methods**: `test_what_it_tests`
- **Fixtures**: `descriptive_name` (lowercase with underscores)

**Examples:**
- `TestGetUserPermissions` - Tests the `get_user_permissions` function
- `test_admin_permissions` - Tests admin role permissions
- `test_invalid_token_raises_unauthorized` - Tests invalid token handling

## Test Organization

Each test file follows this structure:

1. **Imports** - All required imports at top
2. **Test Classes** - Grouped by feature/component
3. **Fixtures** - Reusable test data
4. **Documentation** - Summary at end

## Writing New Tests

### Checklist:
- [ ] Test has descriptive name
- [ ] Follows Arrange-Act-Assert pattern
- [ ] Uses mocks for external dependencies
- [ ] Includes docstring explaining what it tests
- [ ] Tests one thing (single responsibility)
- [ ] Runs fast (< 100ms)
- [ ] Independent of other tests

### Example:
```python
def test_admin_has_all_permissions(self):
    """Admin role should have all system permissions"""
    # Arrange
    role = Mock(spec=Role)
    role.name = "Admin"
    user = Mock(spec=User)
    user.role = role

    # Act
    permissions = get_user_permissions(user)

    # Assert
    assert 'admin' in permissions
    assert 'users.delete' in permissions
    assert len(permissions) > 20
```

## CI/CD Integration

These tests run automatically on:
- Every commit
- Every pull request
- Before deployment

**Requirements:**
- All tests must pass
- Coverage must be ≥ 60%
- No skipped tests in main branch

## Dependencies

```bash
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
```

## Troubleshooting

### Tests Fail With Import Errors
```bash
# Ensure you're in the project root
cd /path/to/TSH_ERP_Ecosystem

# Install in development mode
pip install -e .
```

### Async Tests Not Running
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Check pytest.ini has: asyncio_mode = auto
```

### Coverage Report Not Generated
```bash
# Install coverage tools
pip install pytest-cov

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=html
```

## Best Practices

### DO ✅
- Write tests for all new features
- Keep tests fast (mock external services)
- Use descriptive names
- Test edge cases and error conditions
- Mock external dependencies
- Follow AAA pattern (Arrange-Act-Assert)

### DON'T ❌
- Test external services directly (use mocks)
- Write tests that depend on execution order
- Use real database in unit tests
- Skip tests without good reason
- Write tests that take > 1 second
- Test implementation details (test behavior)

## Metrics

**Current Status:**
- Total Unit Tests: 35
- Auth Tests: 16
- TDS Tests: 19
- Average Execution Time: ~50ms per test
- Coverage Target: 60%
- Coverage Actual: (run pytest with --cov to check)

## Related Documentation

- [Integration Tests](../integration/README.md)
- [E2E Tests](../e2e/README.md)
- [Test Strategy](../../docs/testing/TEST_STRATEGY.md)
- [CI/CD Pipeline](../../docs/ci-cd/PIPELINE.md)

## Support

For questions or issues with tests:
1. Check this README
2. Review existing tests for examples
3. Check pytest documentation
4. Contact senior engineer

---

**Last Updated**: January 7, 2025
**Maintainer**: TSH ERP Team
**Status**: ✅ Active
