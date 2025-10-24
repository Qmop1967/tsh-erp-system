"""Maintenance schemas"""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class MaintenanceJobStart(BaseModel):
    """Start maintenance job"""
    return_request_id: int
    technician_id: int
    cost_estimate: Optional[Decimal] = None


class MaintenanceJobComplete(BaseModel):
    """Complete maintenance job"""
    outcome: str
    parts_used: list = []
    labor_minutes: int = 0
    actual_cost: Optional[Decimal] = None
    notes: Optional[str] = None
