"""
Data Investigation Reports Router
==================================

API endpoints for viewing daily data investigation reports.
واجهة برمجية لعرض تقارير التحقيق اليومي للبيانات

Author: TSH ERP Team
Date: November 7, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.data_investigation import DataInvestigationReport
from pydantic import BaseModel


router = APIRouter(
    prefix="/api/data-investigation",
    tags=["Data Investigation"]
)


# Pydantic models for responses
class InvestigationReportResponse(BaseModel):
    """Investigation report response schema"""
    id: int
    report_date: datetime
    entity_type: str
    zoho_count: int
    tsh_erp_count: int
    difference: int
    difference_percentage: str
    status: str
    is_critical: bool
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class InvestigationSummaryResponse(BaseModel):
    """Summary of investigation reports"""
    total_reports: int
    matched: int
    mismatched: int
    critical: int
    errors: int
    last_investigation: Optional[datetime] = None


@router.get("/reports", response_model=List[InvestigationReportResponse])
async def get_investigation_reports(
    days: int = Query(7, description="Number of days to retrieve reports for"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    status: Optional[str] = Query(None, description="Filter by status: matched, mismatch, error"),
    critical_only: bool = Query(False, description="Show only critical mismatches"),
    db: Session = Depends(get_db)
):
    """
    Get data investigation reports

    التحقيق اليومي للبيانات - عرض التقارير

    **Parameters:**
    - **days**: Number of days to retrieve (default: 7)
    - **entity_type**: Filter by entity type (products, customers, etc.)
    - **status**: Filter by status (matched, mismatch, error)
    - **critical_only**: Show only critical mismatches

    **Returns:**
    - List of investigation reports
    """
    try:
        # Build query
        query = db.query(DataInvestigationReport)

        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(DataInvestigationReport.report_date >= cutoff_date)

        # Apply filters
        if entity_type:
            query = query.filter(DataInvestigationReport.entity_type == entity_type)

        if status:
            query = query.filter(DataInvestigationReport.status == status)

        if critical_only:
            query = query.filter(DataInvestigationReport.is_critical == True)

        # Order by date descending
        query = query.order_by(desc(DataInvestigationReport.report_date))

        # Execute query
        reports = query.all()

        return reports

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")


@router.get("/summary", response_model=InvestigationSummaryResponse)
async def get_investigation_summary(
    days: int = Query(7, description="Number of days to summarize"),
    db: Session = Depends(get_db)
):
    """
    Get summary of investigation reports

    ملخص تقارير التحقيق اليومي

    **Parameters:**
    - **days**: Number of days to summarize (default: 7)

    **Returns:**
    - Summary statistics of investigation reports
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get all reports in date range
        reports = db.query(DataInvestigationReport).filter(
            DataInvestigationReport.report_date >= cutoff_date
        ).all()

        # Calculate summary
        total = len(reports)
        matched = sum(1 for r in reports if r.status == 'matched')
        mismatched = sum(1 for r in reports if r.status == 'mismatch')
        critical = sum(1 for r in reports if r.is_critical)
        errors = sum(1 for r in reports if r.status == 'error')

        # Get last investigation date
        last_report = db.query(DataInvestigationReport).order_by(
            desc(DataInvestigationReport.report_date)
        ).first()

        return {
            "total_reports": total,
            "matched": matched,
            "mismatched": mismatched,
            "critical": critical,
            "errors": errors,
            "last_investigation": last_report.report_date if last_report else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {str(e)}")


@router.get("/latest", response_model=List[InvestigationReportResponse])
async def get_latest_investigation(
    db: Session = Depends(get_db)
):
    """
    Get latest investigation report (all entities from most recent run)

    أحدث تقرير تحقيق

    **Returns:**
    - List of reports from the latest investigation run
    """
    try:
        # Get the most recent report date
        latest_report = db.query(DataInvestigationReport).order_by(
            desc(DataInvestigationReport.report_date)
        ).first()

        if not latest_report:
            return []

        # Get all reports from that date (within 1 hour window)
        time_window = latest_report.report_date - timedelta(hours=1)

        reports = db.query(DataInvestigationReport).filter(
            DataInvestigationReport.report_date >= time_window
        ).order_by(DataInvestigationReport.entity_type).all()

        return reports

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching latest report: {str(e)}")


@router.get("/critical", response_model=List[InvestigationReportResponse])
async def get_critical_mismatches(
    days: int = Query(7, description="Number of days to check"),
    db: Session = Depends(get_db)
):
    """
    Get all critical mismatches

    عرض الحالات الحرجة فقط

    **Parameters:**
    - **days**: Number of days to check (default: 7)

    **Returns:**
    - List of critical mismatch reports
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        reports = db.query(DataInvestigationReport).filter(
            and_(
                DataInvestigationReport.report_date >= cutoff_date,
                DataInvestigationReport.is_critical == True
            )
        ).order_by(desc(DataInvestigationReport.report_date)).all()

        return reports

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching critical mismatches: {str(e)}")


@router.get("/entity/{entity_type}/history", response_model=List[InvestigationReportResponse])
async def get_entity_history(
    entity_type: str,
    days: int = Query(30, description="Number of days of history"),
    db: Session = Depends(get_db)
):
    """
    Get historical investigation reports for specific entity type

    تاريخ التحقيق لنوع معين من البيانات

    **Parameters:**
    - **entity_type**: Entity type (products, customers, etc.)
    - **days**: Number of days of history (default: 30)

    **Returns:**
    - Historical reports for the entity
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        reports = db.query(DataInvestigationReport).filter(
            and_(
                DataInvestigationReport.entity_type == entity_type,
                DataInvestigationReport.report_date >= cutoff_date
            )
        ).order_by(desc(DataInvestigationReport.report_date)).all()

        return reports

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching history for {entity_type}: {str(e)}"
        )
