"""Warranty schemas"""
from pydantic import BaseModel
from datetime import date
from typing import Optional


class WarrantyCaseCreate(BaseModel):
    """Create warranty case"""
    return_request_id: int
    purchase_date: date
    warranty_expiry_date: date
    policy_id: Optional[int] = None
