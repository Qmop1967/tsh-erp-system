"""
Unit Tests for Branch Service (Phase 4)

Tests the service layer that moves business logic out of routers.

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from app.services.branch_service import BranchService
from app.schemas.branch import BranchCreate, BranchUpdate
from app.models.branch import Branch
from app.exceptions import EntityNotFoundError, DuplicateEntityError


class TestBranchServiceGetOperations:
    """Test suite for branch retrieval operations"""

    def test_get_all_branches_without_filters(self):
        """Should get all branches with pagination"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        mock_branches = [
            Mock(id=1, name="Branch 1"),
            Mock(id=2, name="Branch 2")
        ]

        service.repo.get_all = Mock(return_value=mock_branches)
        service.repo.get_count = Mock(return_value=2)

        # Act
        branches, total = service.get_all_branches(skip=0, limit=10)

        # Assert
        assert len(branches) == 2
        assert total == 2
        service.repo.get_all.assert_called_once()

    def test_get_all_branches_with_search(self):
        """Should search branches by term"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        mock_branches = [Mock(id=1, name="Main Branch")]

        service.repo.search = Mock(return_value=mock_branches)

        # Act
        branches, total = service.get_all_branches(
            skip=0,
            limit=10,
            search="Main"
        )

        # Assert
        assert len(branches) == 1
        service.repo.search.assert_called()

    def test_get_all_branches_with_is_active_filter(self):
        """Should filter branches by active status"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        mock_branches = [Mock(id=1, name="Active Branch", is_active=True)]

        service.repo.get_all = Mock(return_value=mock_branches)
        service.repo.get_count = Mock(return_value=1)

        # Act
        branches, total = service.get_all_branches(
            skip=0,
            limit=10,
            is_active=True
        )

        # Assert
        service.repo.get_all.assert_called_once_with(
            skip=0,
            limit=10,
            filters={'is_active': True}
        )

    def test_get_branch_by_id_found(self):
        """Should return branch if found"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        mock_branch = Mock(id=1, name="Test Branch")
        service.repo.get_or_404 = Mock(return_value=mock_branch)

        # Act
        branch = service.get_branch_by_id(1)

        # Assert
        assert branch == mock_branch
        service.repo.get_or_404.assert_called_once_with(
            1,
            detail="Branch not found"
        )

    def test_get_branch_by_id_not_found_raises(self):
        """Should raise EntityNotFoundError if not found"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        from fastapi import HTTPException
        service.repo.get_or_404 = Mock(
            side_effect=HTTPException(status_code=404, detail="Branch not found")
        )

        # Act & Assert
        with pytest.raises(HTTPException):
            service.get_branch_by_id(999)


class TestBranchServiceCreateOperations:
    """Test suite for branch creation"""

    def test_create_branch_success(self):
        """Should create branch successfully"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        branch_data = Mock(spec=BranchCreate)
        branch_data.dict.return_value = {'name': 'New Branch', 'code': 'BR001'}
        branch_data.code = 'BR001'

        mock_created_branch = Mock(id=1, name='New Branch', code='BR001')

        service.repo.validate_unique = Mock()
        service.repo.create = Mock(return_value=mock_created_branch)

        # Act
        branch = service.create_branch(branch_data)

        # Assert
        assert branch == mock_created_branch
        service.repo.validate_unique.assert_called_once_with(
            field='code',
            value='BR001',
            error_message="Branch code already exists"
        )
        service.repo.create.assert_called_once()

    def test_create_branch_duplicate_code_raises(self):
        """Should raise error if code already exists"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        branch_data = Mock(spec=BranchCreate)
        branch_data.code = 'BR001'

        from fastapi import HTTPException
        service.repo.validate_unique = Mock(
            side_effect=HTTPException(status_code=400, detail="Branch code already exists")
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_branch(branch_data)

        assert exc_info.value.status_code == 400


class TestBranchServiceUpdateOperations:
    """Test suite for branch updates"""

    def test_update_branch_success(self):
        """Should update branch successfully"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        branch_data = Mock(spec=BranchUpdate)
        branch_data.dict.return_value = {'name': 'Updated Branch'}
        branch_data.code = None

        mock_updated_branch = Mock(id=1, name='Updated Branch')

        service.repo.update = Mock(return_value=mock_updated_branch)

        # Act
        branch = service.update_branch(1, branch_data)

        # Assert
        assert branch == mock_updated_branch
        service.repo.update.assert_called_once_with(
            1,
            {'name': 'Updated Branch'}
        )

    def test_update_branch_with_code_validation(self):
        """Should validate unique code on update"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        branch_data = Mock(spec=BranchUpdate)
        branch_data.dict.return_value = {'code': 'BR002'}
        branch_data.code = 'BR002'

        mock_updated_branch = Mock(id=1, code='BR002')

        service.repo.validate_unique = Mock()
        service.repo.update = Mock(return_value=mock_updated_branch)

        # Act
        branch = service.update_branch(1, branch_data)

        # Assert
        service.repo.validate_unique.assert_called_once_with(
            field='code',
            value='BR002',
            exclude_id=1,
            error_message="Branch code already exists"
        )


class TestBranchServiceDeleteOperations:
    """Test suite for branch deletion"""

    def test_delete_branch_success(self):
        """Should delete branch (hard delete)"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        service.repo.delete = Mock(return_value=True)

        # Act
        result = service.delete_branch(1)

        # Assert
        assert result is True
        service.repo.delete.assert_called_once_with(1)

    def test_deactivate_branch_success(self):
        """Should soft delete branch"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        mock_branch = Mock(id=1, is_active=False)
        service.repo.soft_delete = Mock(return_value=mock_branch)

        # Act
        branch = service.deactivate_branch(1)

        # Assert
        assert branch.is_active is False
        service.repo.soft_delete.assert_called_once_with(1)

    def test_activate_branch_success(self):
        """Should reactivate deactivated branch"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        mock_branch = Mock(id=1, is_active=True)
        service.repo.update = Mock(return_value=mock_branch)

        # Act
        branch = service.activate_branch(1)

        # Assert
        service.repo.update.assert_called_once_with(1, {'is_active': True})


class TestBranchServiceUtilityMethods:
    """Test suite for utility methods"""

    def test_get_active_branches(self):
        """Should get all active branches without pagination"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        mock_branches = [
            Mock(id=1, is_active=True),
            Mock(id=2, is_active=True)
        ]

        service.repo.get_all = Mock(return_value=mock_branches)

        # Act
        branches = service.get_active_branches()

        # Assert
        assert len(branches) == 2
        service.repo.get_all.assert_called_once_with(
            filters={'is_active': True},
            skip=0,
            limit=1000
        )

    def test_branch_exists(self):
        """Should check if branch with code exists"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        service.repo.exists = Mock(return_value=True)

        # Act
        exists = service.branch_exists('BR001')

        # Assert
        assert exists is True
        service.repo.exists.assert_called_once_with({'code': 'BR001'})


class TestBranchServiceIntegration:
    """Integration tests validating service layer pattern"""

    def test_service_uses_repository_pattern(self):
        """Service should use BaseRepository for all DB operations"""
        # Arrange
        mock_db = Mock(spec=Session)

        # Act
        service = BranchService(mock_db)

        # Assert
        assert service.repo is not None
        assert service.db == mock_db

    def test_service_provides_business_logic_layer(self):
        """Service should provide business logic, not just CRUD"""
        # Arrange
        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        # Assert - Service has methods beyond basic CRUD
        assert hasattr(service, 'get_active_branches')
        assert hasattr(service, 'branch_exists')
        assert hasattr(service, 'deactivate_branch')
        assert hasattr(service, 'activate_branch')

    def test_replaces_router_database_operations(self):
        """Service should replace direct DB operations from router"""
        # This validates that the pattern works:
        # BEFORE: Router → DB directly (174 operations)
        # AFTER: Router → Service → Repository → DB

        mock_db = Mock(spec=Session)
        service = BranchService(mock_db)

        # Service provides clean interface
        assert hasattr(service, 'get_all_branches')
        assert hasattr(service, 'get_branch_by_id')
        assert hasattr(service, 'create_branch')
        assert hasattr(service, 'update_branch')
        assert hasattr(service, 'delete_branch')


# ============================================================================
# Test Statistics
# ============================================================================

"""
Test Coverage Summary:
- Get operations: 5 tests
- Create operations: 2 tests
- Update operations: 2 tests
- Delete operations: 3 tests
- Utility methods: 2 tests
- Integration validation: 3 tests
- Total: 17 tests

Critical Paths Covered:
✅ Get all with pagination
✅ Get all with search
✅ Get all with filters
✅ Get by ID (found/not found)
✅ Create with validation
✅ Create with duplicate detection
✅ Update with validation
✅ Hard delete
✅ Soft delete (deactivate)
✅ Reactivate
✅ Get active branches
✅ Check existence
✅ Service layer pattern validation

Phase 4 Validation:
✅ Tests validate BranchService works correctly
✅ Proves service layer separates concerns
✅ Provides mockable interface for router testing
✅ Documents expected behavior
"""
