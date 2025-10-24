"""Inspection schemas"""
from pydantic import BaseModel
from typing import Optional
from prss.models.base import FindingType, RecommendationType


class InspectionCreate(BaseModel):
    """Create inspection"""
    return_request_id: int
    inspector_id: int
    checklists: dict = {}
    finding: FindingType
    recommendation: RecommendationType
    inspection_photos: list = []
    notes: Optional[str] = None


class InspectionResponse(BaseModel):
    """Inspection response"""
    id: int
    return_request_id: int
    finding: FindingType
    recommendation: RecommendationType

    class Config:
        from_attributes = True
