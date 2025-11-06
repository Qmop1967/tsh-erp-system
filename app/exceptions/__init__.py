"""
Custom Exception Classes for TSH ERP System

Standardizes error handling across 263 HTTPException usages.
Provides consistent, bilingual error responses.

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 4 - Error Handling Standardization
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class TSHException(HTTPException):
    """
    Base exception for TSH ERP system.

    All custom exceptions inherit from this.
    Provides consistent error response format.
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        detail_ar: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize TSH exception.

        Args:
            status_code: HTTP status code
            detail: Error message in English
            detail_ar: Optional error message in Arabic
            headers: Optional HTTP headers
        """
        self.detail_ar = detail_ar
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class EntityNotFoundError(TSHException):
    """
    Raised when an entity is not found by ID.

    Replaces 80+ occurrences of:
    HTTPException(status_code=404, detail="Not found")

    Usage:
        raise EntityNotFoundError("Product", product_id)
    """

    def __init__(
        self,
        entity_name: str,
        entity_id: Optional[Any] = None
    ):
        detail = f"{entity_name} not found"
        if entity_id:
            detail = f"{entity_name} with ID {entity_id} not found"

        detail_ar = f"{entity_name} غير موجود"
        if entity_id:
            detail_ar = f"{entity_name} برقم {entity_id} غير موجود"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            detail_ar=detail_ar
        )


class DuplicateEntityError(TSHException):
    """
    Raised when trying to create entity with duplicate unique field.

    Replaces duplicate uniqueness validation errors.

    Usage:
        raise DuplicateEntityError("Product", "SKU", sku_value)
    """

    def __init__(
        self,
        entity_name: str,
        field_name: str,
        field_value: Optional[Any] = None
    ):
        detail = f"{entity_name} with {field_name}"
        if field_value:
            detail += f" '{field_value}'"
        detail += " already exists"

        detail_ar = f"{entity_name} مع {field_name}"
        if field_value:
            detail_ar += f" '{field_value}'"
        detail_ar += " موجود بالفعل"

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            detail_ar=detail_ar
        )


class ValidationError(TSHException):
    """
    Raised when validation fails.

    Usage:
        raise ValidationError("Invalid email format")
    """

    def __init__(
        self,
        detail: str,
        detail_ar: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            detail_ar=detail_ar
        )


class UnauthorizedError(TSHException):
    """
    Raised when authentication fails.

    Usage:
        raise UnauthorizedError("Invalid token")
    """

    def __init__(
        self,
        detail: str = "Could not validate credentials",
        detail_ar: str = "لا يمكن التحقق من بيانات الاعتماد"
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            detail_ar=detail_ar,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(TSHException):
    """
    Raised when user doesn't have permission.

    Usage:
        raise ForbiddenError("You don't have permission to delete users")
    """

    def __init__(
        self,
        detail: str = "Forbidden",
        detail_ar: str = "غير مصرح"
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            detail_ar=detail_ar
        )


class InactiveUserError(ForbiddenError):
    """
    Raised when user account is inactive.

    Usage:
        raise InactiveUserError()
    """

    def __init__(self):
        super().__init__(
            detail="User account is inactive",
            detail_ar="حساب المستخدم غير نشط"
        )


class TokenBlacklistedError(UnauthorizedError):
    """
    Raised when token has been revoked.

    Usage:
        raise TokenBlacklistedError()
    """

    def __init__(self):
        super().__init__(
            detail="Token has been revoked",
            detail_ar="تم إلغاء الرمز"
        )


class BusinessLogicError(TSHException):
    """
    Raised when business logic validation fails.

    Usage:
        raise BusinessLogicError("Cannot delete customer with active orders")
    """

    def __init__(
        self,
        detail: str,
        detail_ar: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            detail_ar=detail_ar
        )


class InsufficientStockError(BusinessLogicError):
    """
    Raised when trying to sell more than available stock.

    Usage:
        raise InsufficientStockError("Product X", requested=10, available=5)
    """

    def __init__(
        self,
        product_name: str,
        requested: int,
        available: int
    ):
        detail = f"Insufficient stock for {product_name}. Requested: {requested}, Available: {available}"
        detail_ar = f"مخزون غير كافٍ لـ {product_name}. المطلوب: {requested}، المتاح: {available}"

        super().__init__(detail=detail, detail_ar=detail_ar)


class ExternalServiceError(TSHException):
    """
    Raised when external service (Zoho, payment gateway, etc.) fails.

    Usage:
        raise ExternalServiceError("Zoho API", "Connection timeout")
    """

    def __init__(
        self,
        service_name: str,
        error_detail: str
    ):
        detail = f"{service_name} error: {error_detail}"
        detail_ar = f"خطأ في {service_name}: {error_detail}"

        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            detail_ar=detail_ar
        )


class ConfigurationError(TSHException):
    """
    Raised when system configuration is invalid.

    Usage:
        raise ConfigurationError("Missing ZOHO_CLIENT_ID environment variable")
    """

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {detail}",
            detail_ar=f"خطأ في الإعدادات: {detail}"
        )


# ============================================================================
# Error Response Schema
# ============================================================================

class ErrorResponse:
    """
    Standard error response format.

    Used by global exception handler to format all errors consistently.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        message_ar: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.message_ar = message_ar
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response = {
            "success": False,
            "error": {
                "code": self.status_code,
                "message": self.message,
            }
        }

        if self.message_ar:
            response["error"]["message_ar"] = self.message_ar

        if self.details:
            response["error"]["details"] = self.details

        return response


# ============================================================================
# Usage Examples
# ============================================================================

"""
BEFORE (inconsistent, duplicated 263 times):

    # In routers (different patterns)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        result = do_something()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    existing = db.query(Product).filter(Product.sku == sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")


AFTER (consistent, centralized):

    # In services
    product = self.repo.get(product_id)
    if not product:
        raise EntityNotFoundError("Product", product_id)

    if self.repo.exists({"sku": sku}):
        raise DuplicateEntityError("Product", "SKU", sku)

    if stock < requested:
        raise InsufficientStockError(product.name, requested, stock)

    try:
        zoho_result = await zoho_service.sync()
    except Exception as e:
        raise ExternalServiceError("Zoho API", str(e))


BENEFITS:
✅ Consistent error format across all APIs
✅ Bilingual error messages (English + Arabic)
✅ Type-safe exception handling
✅ Better error categorization
✅ Easier to test
✅ Self-documenting code
"""
