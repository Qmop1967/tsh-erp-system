"""Inspection business logic"""
from sqlalchemy.orm import Session
from prss.models.all_models import Inspection, ReturnRequest
from prss.models.base import ReturnStatus
from prss.schemas.inspection import InspectionCreate


class InspectionService:
    def __init__(self, db: Session):
        self.db = db

    def create_inspection(self, return_id: int, data: InspectionCreate, user_id: int):
        """Create inspection record"""
        inspection = Inspection(**data.model_dump())
        self.db.add(inspection)

        # Update return status
        return_req = self.db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
        return_req.status = ReturnStatus.INSPECTING

        self.db.commit()
        return {"message": "Inspection recorded"}
