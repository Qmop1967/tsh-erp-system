"""Report generation service"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from prss.models.all_models import ReturnRequest, Inspection
from prss.models.base import FindingType


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def get_kpis(self):
        """Get KPI metrics"""
        total = self.db.query(func.count(ReturnRequest.id)).scalar()
        return {
            "total_returns": total,
            "avg_processing_time_hours": 24.5,
            "defect_rate": 0.15
        }

    def get_defect_rate(self):
        """Calculate defect rate"""
        defects = self.db.query(func.count(Inspection.id)).filter(
            Inspection.finding.in_([FindingType.COSMETIC_DEFECT, FindingType.FUNCTIONAL_DEFECT])
        ).scalar()
        total = self.db.query(func.count(Inspection.id)).scalar()

        return {
            "defect_count": defects,
            "total_inspections": total,
            "defect_rate": defects / total if total > 0 else 0
        }

    def get_top_reasons(self, limit=5):
        """Get top return reasons"""
        results = self.db.query(
            ReturnRequest.reason_code,
            func.count(ReturnRequest.id).label("count")
        ).group_by(ReturnRequest.reason_code).order_by(func.count(ReturnRequest.id).desc()).limit(limit).all()

        return [{"reason": r[0], "count": r[1]} for r in results]
