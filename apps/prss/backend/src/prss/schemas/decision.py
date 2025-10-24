"""Decision schemas"""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from prss.models.base import FinalDecision


class DecisionCreate(BaseModel):
    """Create final decision"""
    return_request_id: int
    final_decision: FinalDecision
    approved_by: int
    reason: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    notes: Optional[str] = None
