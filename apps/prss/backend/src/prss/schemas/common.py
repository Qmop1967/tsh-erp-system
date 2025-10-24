"""Common schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[dict] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)


class PhotoUpload(BaseModel):
    """Photo upload data"""
    url: str
    filename: str
    size: int
    uploaded_at: datetime
