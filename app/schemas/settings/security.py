"""
Security & Permission Schemas
==============================

Pydantic models for security and permission management endpoints.
"""

from pydantic import BaseModel
from typing import Optional, List


class GrantPermissionRequest(BaseModel):
    """Request model for granting permissions"""
    user_id: int
    permission: str
    resource: Optional[str] = None


class RevokePermissionRequest(BaseModel):
    """Request model for revoking permissions"""
    user_id: int
    permission: str
    resource: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """Response model for system health check"""
    status: str
    database: bool
    cache: Optional[bool] = None
    storage: Optional[bool] = None
    errors: Optional[List[str]] = None
