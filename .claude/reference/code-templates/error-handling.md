# Error Handling Templates

**Purpose:** Production-ready error response patterns with bilingual support for TSH ERP
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/code-templates/error-handling.md

---

## ❌ Template 6.1: Standardized Error Response

**Reasoning Context:**
- Consistent error format helps frontend handle errors uniformly
- HTTP status codes indicate error type (400, 401, 403, 404, 500)
- Error messages must be user-friendly (Arabic for TSH ERP users)
- Include request_id for debugging and support
- Validation errors need field-specific details

**When to Use:**
- All API endpoints
- Custom exception handlers
- Validation errors
- Business logic errors

**Code Template:**

```python
# app/schemas/errors.py
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = None  # For validation errors
    message: str
    message_ar: Optional[str] = None  # Arabic error message
    code: Optional[str] = None  # Error code for client handling

class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: bool = True
    status_code: int
    message: str
    message_ar: Optional[str] = None
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "status_code": 400,
                "message": "Invalid product data",
                "message_ar": "بيانات المنتج غير صحيحة",
                "details": [
                    {
                        "field": "unit_price",
                        "message": "Unit price must be greater than cost price",
                        "message_ar": "يجب أن يكون سعر البيع أكبر من سعر التكلفة",
                        "code": "PRICE_BELOW_COST"
                    }
                ],
                "request_id": "req_abc123xyz",
                "timestamp": "2025-11-12T10:30:00Z"
            }
        }

# Exception handler
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uuid

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""

    # Convert Pydantic errors to our format
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        details.append(ErrorDetail(
            field=field,
            message=error["msg"],
            code=error["type"]
        ))

    error_response = ErrorResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        message="Validation error",
        message_ar="خطأ في التحقق من البيانات",
        details=details,
        request_id=str(uuid.uuid4())
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.dict()
    )

# Custom exception
class BusinessLogicError(Exception):
    """Base exception for business logic errors."""

    def __init__(
        self,
        message: str,
        message_ar: str = None,
        status_code: int = 400,
        code: str = None
    ):
        self.message = message
        self.message_ar = message_ar or message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)

# Usage in endpoint
@router.post("/orders")
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # Business logic validation
    if order_data.total_amount > client.credit_limit:
        raise BusinessLogicError(
            message=f"Order amount exceeds credit limit of {client.credit_limit}",
            message_ar=f"مبلغ الطلب يتجاوز الحد الائتماني {client.credit_limit}",
            code="CREDIT_LIMIT_EXCEEDED",
            status_code=400
        )

    # Create order...
```

**Exception Handler for Business Logic Errors:**

```python
# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.schemas.errors import ErrorResponse, BusinessLogicError
import uuid

app = FastAPI()

@app.exception_handler(BusinessLogicError)
async def business_logic_exception_handler(request: Request, exc: BusinessLogicError):
    """Handle business logic exceptions."""

    error_response = ErrorResponse(
        status_code=exc.status_code,
        message=exc.message,
        message_ar=exc.message_ar,
        request_id=str(uuid.uuid4()),
        details=[{
            "message": exc.message,
            "message_ar": exc.message_ar,
            "code": exc.code
        }] if exc.code else None
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )
```

**Common Error Messages (Bilingual):**

```python
# app/constants/errors.py

ERROR_MESSAGES = {
    "NOT_FOUND": {
        "en": "Resource not found",
        "ar": "المورد غير موجود"
    },
    "UNAUTHORIZED": {
        "en": "Authentication required",
        "ar": "المصادقة مطلوبة"
    },
    "FORBIDDEN": {
        "en": "You don't have permission to access this resource",
        "ar": "ليس لديك إذن للوصول إلى هذا المورد"
    },
    "VALIDATION_ERROR": {
        "en": "Invalid input data",
        "ar": "بيانات إدخال غير صحيحة"
    },
    "DUPLICATE_SKU": {
        "en": "Product with this SKU already exists",
        "ar": "المنتج برقم SKU هذا موجود بالفعل"
    },
    "CREDIT_LIMIT_EXCEEDED": {
        "en": "Order amount exceeds credit limit",
        "ar": "مبلغ الطلب يتجاوز الحد الائتماني"
    },
    "INSUFFICIENT_STOCK": {
        "en": "Insufficient stock for this product",
        "ar": "مخزون غير كافٍ لهذا المنتج"
    }
}

def get_error_message(code: str, lang: str = 'ar') -> str:
    """Get error message in specified language."""
    return ERROR_MESSAGES.get(code, {}).get(lang, code)
```

**Frontend Error Handling (Flutter):**

```dart
// Flutter error handling example
class ApiException implements Exception {
  final int statusCode;
  final String message;
  final String messageAr;
  final String? code;

  ApiException({
    required this.statusCode,
    required this.message,
    required this.messageAr,
    this.code,
  });

  factory ApiException.fromJson(Map<String, dynamic> json) {
    return ApiException(
      statusCode: json['status_code'],
      message: json['message'],
      messageAr: json['message_ar'] ?? json['message'],
      code: json['details']?[0]?['code'],
    );
  }

  String getLocalizedMessage(String lang) {
    return lang == 'ar' ? messageAr : message;
  }
}

// Usage in API client
Future<Product> createProduct(ProductData data) async {
  try {
    final response = await http.post('/api/products/', body: data.toJson());

    if (response.statusCode == 201) {
      return Product.fromJson(response.data);
    } else {
      throw ApiException.fromJson(response.data);
    }
  } catch (e) {
    if (e is ApiException) {
      // Show error in user's language
      showError(e.getLocalizedMessage(currentLanguage));
    }
    rethrow;
  }
}
```

**Related Patterns:**
- Authentication errors: @docs/reference/code-templates/authentication.md
- Arabic support: @docs/reference/code-templates/arabic-bilingual.md

---

## 🚨 Error Handling Best Practices

```yaml
HTTP Status Codes:
200: Success
201: Created
204: No Content (successful delete)
400: Bad Request (validation error)
401: Unauthorized (authentication required)
403: Forbidden (insufficient permissions)
404: Not Found
409: Conflict (duplicate resource)
500: Internal Server Error

Always Include:
✅ HTTP status code
✅ Error message (English)
✅ Error message (Arabic)
✅ Request ID for debugging
✅ Timestamp
✅ Field-specific details (for validation)

Never Include:
❌ Stack traces (security risk)
❌ Database errors (security risk)
❌ Internal system details
❌ Sensitive user data
```

---

**Related Documentation:**
- Authentication: @docs/reference/code-templates/authentication.md
- Arabic support: @docs/reference/code-templates/arabic-bilingual.md
- Security patterns: @docs/core/architecture.md
