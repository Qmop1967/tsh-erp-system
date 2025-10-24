"""Reports API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from prss.db import get_db
from prss.services.report_service import ReportService
from prss.security.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/kpis")
async def get_kpis(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get KPI metrics"""
    service = ReportService(db)
    return service.get_kpis()


@router.get("/defect-rate")
async def get_defect_rate(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get defect rate analysis"""
    service = ReportService(db)
    return service.get_defect_rate()


@router.get("/top-reasons")
async def get_top_return_reasons(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get top return reasons"""
    service = ReportService(db)
    return service.get_top_reasons(limit)
