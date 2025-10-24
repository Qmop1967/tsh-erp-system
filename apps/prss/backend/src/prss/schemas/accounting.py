"""Accounting schemas"""
from pydantic import BaseModel
from decimal import Decimal
from prss.models.base import AccountingEffectType


class AccountingEffectCreate(BaseModel):
    """Create accounting effect"""
    return_request_id: int
    effect_type: AccountingEffectType
    amount: Decimal
    currency: str = "SAR"
    notes: str = ""
