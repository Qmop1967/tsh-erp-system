"""Maintenance API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from prss.db import get_db
from prss.schemas.maintenance import *
from prss.services.maintenance_service import MaintenanceService
from prss.security.auth import get_current_user, require_role

router = APIRouter(prefix="/returns", tags=["maintenance"])


@router.post("/{return_id}/maintenance/start", dependencies=[Depends(require_role(["admin", "technician"]))])
async def start_maintenance(
    return_id: int,
    job_data: MaintenanceJobStart,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start maintenance job"""
    service = MaintenanceService(db)
    return service.start_job(return_id, job_data, current_user.id)


@router.post("/{return_id}/maintenance/complete", dependencies=[Depends(require_role(["admin", "technician"]))])
async def complete_maintenance(
    return_id: int,
    job_data: MaintenanceJobComplete,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Complete maintenance job"""
    service = MaintenanceService(db)
    return service.complete_job(return_id, job_data, current_user.id)
