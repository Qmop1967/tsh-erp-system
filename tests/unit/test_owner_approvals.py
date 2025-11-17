"""
Unit tests for Owner Approvals system

Tests the core functionality of the owner approval workflow:
- Approval request creation
- Code generation
- QR JWT signing
- Status transitions
- Authorization checks
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.models.owner_approval import (
    OwnerApproval, ApprovalStatus, ApprovalMethod,
    ApprovalType, RiskLevel, ApprovalAuditLog
)
from app.schemas.owner_approval import (
    CreateApprovalRequest, ApproveRequest, DenyRequest,
    ApprovalTypeSchema, RiskLevelSchema, ApprovalMethodSchema
)
from app.routers.owner_approvals import (
    generate_qr_jwt, verify_qr_jwt, approval_to_response
)


class TestOwnerApprovalModel:
    """Test OwnerApproval model methods"""

    def test_generate_approval_code(self):
        """Should generate 6-digit numeric code"""
        code = OwnerApproval.generate_approval_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_approval_code_uniqueness(self):
        """Should generate different codes"""
        codes = [OwnerApproval.generate_approval_code() for _ in range(100)]
        # Should have high uniqueness (allow some collisions)
        assert len(set(codes)) > 90

    def test_default_expiration(self):
        """Should default to 10 minutes from now"""
        expiration = OwnerApproval.default_expiration()
        expected = datetime.utcnow() + timedelta(minutes=10)
        # Allow 1 second tolerance
        assert abs((expiration - expected).total_seconds()) < 1

    def test_is_expired_true(self):
        """Should return True for expired approval"""
        approval = OwnerApproval(
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            approval_code="123456",
            expires_at=datetime.utcnow() - timedelta(minutes=1)
        )
        assert approval.is_expired() is True

    def test_is_expired_false(self):
        """Should return False for non-expired approval"""
        approval = OwnerApproval(
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            approval_code="123456",
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        assert approval.is_expired() is False

    def test_is_pending_true(self):
        """Should return True for pending, non-expired approval"""
        approval = OwnerApproval(
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            approval_code="123456",
            status=ApprovalStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        assert approval.is_pending() is True

    def test_is_pending_false_when_expired(self):
        """Should return False for expired approval"""
        approval = OwnerApproval(
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            approval_code="123456",
            status=ApprovalStatus.PENDING,
            expires_at=datetime.utcnow() - timedelta(minutes=1)
        )
        assert approval.is_pending() is False

    def test_is_pending_false_when_resolved(self):
        """Should return False for resolved approval"""
        approval = OwnerApproval(
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            approval_code="123456",
            status=ApprovalStatus.APPROVED,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        assert approval.is_pending() is False

    def test_to_notification_payload(self):
        """Should generate valid notification payload"""
        approval = OwnerApproval(
            id="test-uuid-123",
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            risk_level=RiskLevel.HIGH,
            approval_code="123456",
            request_description="Test request",
            request_description_ar="طلب اختبار",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            created_at=datetime.utcnow()
        )

        payload = approval.to_notification_payload()

        assert payload["type"] == "owner_approval_request"
        assert payload["approval_id"] == "test-uuid-123"
        assert payload["approval_type"] == "high_value_transaction"
        assert payload["risk_level"] == "high"
        assert payload["requester_id"] == 1
        assert payload["approval_code"] == "123456"
        assert payload["description"] == "Test request"
        assert payload["description_ar"] == "طلب اختبار"


class TestApprovalSchemas:
    """Test Pydantic schema validation"""

    def test_create_approval_request_valid(self):
        """Should accept valid request"""
        request = CreateApprovalRequest(
            approval_type=ApprovalTypeSchema.HIGH_VALUE_TRANSACTION,
            risk_level=RiskLevelSchema.HIGH,
            request_description="Transfer 5,000,000 IQD to vendor account",
            request_description_ar="تحويل 5,000,000 دينار عراقي",
            app_id="accounting_app",
            expiration_minutes=10
        )
        assert request.approval_type == ApprovalTypeSchema.HIGH_VALUE_TRANSACTION
        assert request.risk_level == RiskLevelSchema.HIGH

    def test_create_approval_request_min_description(self):
        """Should reject too short description"""
        with pytest.raises(ValueError):
            CreateApprovalRequest(
                approval_type=ApprovalTypeSchema.HIGH_VALUE_TRANSACTION,
                request_description="Too short"  # < 10 chars
            )

    def test_approve_request_valid_code(self):
        """Should accept valid 6-digit code"""
        request = ApproveRequest(
            approval_code="123456",
            biometric_verified=True
        )
        assert request.approval_code == "123456"

    def test_approve_request_invalid_code_length(self):
        """Should reject non-6-digit codes"""
        with pytest.raises(ValueError):
            ApproveRequest(approval_code="12345")  # Only 5 digits

    def test_approve_request_invalid_code_chars(self):
        """Should reject non-numeric codes"""
        with pytest.raises(ValueError):
            ApproveRequest(approval_code="12345a")  # Contains letter

    def test_deny_request_valid(self):
        """Should accept valid denial"""
        request = DenyRequest(
            resolution_reason="Request denied due to suspicious activity pattern"
        )
        assert len(request.resolution_reason) >= 10

    def test_deny_request_too_short_reason(self):
        """Should reject too short reason"""
        with pytest.raises(ValueError):
            DenyRequest(resolution_reason="Too short")  # < 10 chars


class TestQRJWT:
    """Test QR code JWT generation and verification"""

    @patch('app.routers.owner_approvals.SECRET_KEY', 'test_secret')
    @patch('app.routers.owner_approvals.ALGORITHM', 'HS256')
    def test_generate_qr_jwt(self):
        """Should generate valid JWT"""
        approval = OwnerApproval(
            id="test-uuid-123",
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            approval_code="123456",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            created_at=datetime.utcnow()
        )

        jwt_token = generate_qr_jwt(approval)

        assert isinstance(jwt_token, str)
        assert len(jwt_token) > 50  # JWT should be reasonably long
        assert jwt_token.count('.') == 2  # JWT has 3 parts

    @patch('app.routers.owner_approvals.SECRET_KEY', 'test_secret')
    @patch('app.routers.owner_approvals.ALGORITHM', 'HS256')
    def test_verify_qr_jwt_valid(self):
        """Should verify valid JWT"""
        approval = OwnerApproval(
            id="test-uuid-123",
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            approval_code="123456",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            created_at=datetime.utcnow()
        )

        jwt_token = generate_qr_jwt(approval)
        payload = verify_qr_jwt(jwt_token)

        assert payload["approval_id"] == "test-uuid-123"
        assert payload["approval_type"] == "high_value_transaction"
        assert payload["requester_id"] == 1

    @patch('app.routers.owner_approvals.SECRET_KEY', 'test_secret')
    @patch('app.routers.owner_approvals.ALGORITHM', 'HS256')
    def test_verify_qr_jwt_expired(self):
        """Should reject expired JWT"""
        approval = OwnerApproval(
            id="test-uuid-123",
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            approval_code="123456",
            expires_at=datetime.utcnow() - timedelta(minutes=1),  # Already expired
            created_at=datetime.utcnow() - timedelta(minutes=11)
        )

        jwt_token = generate_qr_jwt(approval)

        # Should raise HTTPException
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            verify_qr_jwt(jwt_token)


class TestApprovalResponse:
    """Test response formatting"""

    def test_approval_to_response_pending(self):
        """Should correctly format pending approval"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.role = Mock()
        mock_user.role.name = "accountant"

        approval = OwnerApproval(
            id="test-uuid-123",
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            risk_level=RiskLevel.HIGH,
            approval_code="123456",
            status=ApprovalStatus.PENDING,
            method=ApprovalMethod.PUSH,
            request_description="Test request",
            request_description_ar=None,  # Add optional field
            app_id=None,  # Add optional field
            device_info=None,  # Add optional field
            ip_address=None,  # Add optional field
            geolocation=None,  # Add optional field
            resolved_at=None,  # Add optional field
            resolved_by=None,  # Add optional field
            resolution_reason=None,  # Add optional field
            resolution_reason_ar=None,  # Add optional field
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            created_at=datetime.utcnow()
        )
        approval.requester = mock_user

        response = approval_to_response(approval)

        assert response.id == "test-uuid-123"
        assert response.requester.id == 1
        assert response.requester.name == "Test User"
        assert response.risk_level == RiskLevel.HIGH.value  # Compare to .value since response uses string
        assert response.status == ApprovalStatus.PENDING.value  # Compare to .value since response uses string
        assert response.is_expired is False
        assert response.time_remaining_seconds is not None
        assert response.time_remaining_seconds > 0

    def test_approval_to_response_expired(self):
        """Should correctly format expired approval"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.role = Mock()
        mock_user.role.name = "accountant"

        approval = OwnerApproval(
            id="test-uuid-123",
            requester_id=1,
            approval_type=ApprovalType.HIGH_VALUE_TRANSACTION,
            risk_level=RiskLevel.LOW,
            approval_code="123456",
            status=ApprovalStatus.PENDING,
            method=ApprovalMethod.PUSH,
            request_description="Test request",
            request_description_ar=None,  # Add optional field
            app_id=None,  # Add optional field
            device_info=None,  # Add optional field
            ip_address=None,  # Add optional field
            geolocation=None,  # Add optional field
            resolved_at=None,  # Add optional field
            resolved_by=None,  # Add optional field
            resolution_reason=None,  # Add optional field
            resolution_reason_ar=None,  # Add optional field
            expires_at=datetime.utcnow() - timedelta(minutes=1),  # Expired
            created_at=datetime.utcnow() - timedelta(minutes=11)
        )
        approval.requester = mock_user

        response = approval_to_response(approval)

        assert response.is_expired is True
        assert response.time_remaining_seconds is None


class TestRoleChecking:
    """Test role-based access control"""

    def test_owner_role_allowed(self):
        """Should allow owner role"""
        from app.routers.owner_approvals import require_owner_role

        mock_user = Mock()
        mock_user.role = Mock()
        mock_user.role.name = "owner"

        result = require_owner_role(mock_user)
        assert result == mock_user

    def test_admin_role_allowed(self):
        """Should allow admin role"""
        from app.routers.owner_approvals import require_owner_role

        mock_user = Mock()
        mock_user.role = Mock()
        mock_user.role.name = "admin"

        result = require_owner_role(mock_user)
        assert result == mock_user

    def test_director_role_allowed(self):
        """Should allow director role"""
        from app.routers.owner_approvals import require_owner_role

        mock_user = Mock()
        mock_user.role = Mock()
        mock_user.role.name = "director"

        result = require_owner_role(mock_user)
        assert result == mock_user

    def test_salesperson_role_denied(self):
        """Should deny non-owner roles"""
        from app.routers.owner_approvals import require_owner_role
        from fastapi import HTTPException

        mock_user = Mock()
        mock_user.role = Mock()
        mock_user.role.name = "salesperson"

        with pytest.raises(HTTPException) as exc_info:
            require_owner_role(mock_user)

        assert exc_info.value.status_code == 403

    def test_no_role_denied(self):
        """Should deny users without role"""
        from app.routers.owner_approvals import require_owner_role
        from fastapi import HTTPException

        mock_user = Mock()
        mock_user.role = None

        with pytest.raises(HTTPException) as exc_info:
            require_owner_role(mock_user)

        assert exc_info.value.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
