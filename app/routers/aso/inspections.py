"""Inspection API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from prss.db import get_db
from prss.schemas.inspection import *
from prss.services.inspection_service import InspectionService
from prss.security.auth import get_current_user, require_role

router = APIRouter(prefix="/returns", tags=["inspections"])


@router.post("/{return_id}/inspect", dependencies=[Depends(require_role(["admin", "inspector"]))])
async def create_inspection(
    return_id: int,
    inspection: InspectionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit inspection result"""
    service = InspectionService(db)
    return service.create_inspection(return_id, inspection, current_user.id)
