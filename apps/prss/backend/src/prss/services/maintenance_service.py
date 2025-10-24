"""Maintenance business logic"""
from sqlalchemy.orm import Session
from prss.models.all_models import MaintenanceJob, ReturnRequest
from prss.models.base import ReturnStatus
import secrets


class MaintenanceService:
    def __init__(self, db: Session):
        self.db = db

    def start_job(self, return_id: int, data, user_id: int):
        """Start maintenance job"""
        job_card_no = f"MNT-{secrets.token_hex(4).upper()}"
        job = MaintenanceJob(
            return_request_id=return_id,
            technician_id=user_id,
            job_card_no=job_card_no
        )
        self.db.add(job)

        # Update return status
        return_req = self.db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
        return_req.status = ReturnStatus.TO_REPAIR

        self.db.commit()
        return {"job_card_no": job_card_no}

    def complete_job(self, return_id: int, data, user_id: int):
        """Complete maintenance job"""
        job = self.db.query(MaintenanceJob).filter(
            MaintenanceJob.return_request_id == return_id
        ).first()

        if job:
            job.outcome = data.outcome
            job.parts_used = data.parts_used
            job.labor_minutes = data.labor_minutes
            job.actual_cost = data.actual_cost
            job.notes = data.notes

            self.db.commit()

        return {"message": "Maintenance job completed"}
