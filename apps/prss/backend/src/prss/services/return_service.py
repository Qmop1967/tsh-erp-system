"""Return request business logic"""
from sqlalchemy.orm import Session
from prss.models.all_models import ReturnRequest, ReturnInventoryMove
from prss.models.base import ReturnStatus, InventoryZone
from prss.schemas.return_request import ReturnRequestCreate
from fastapi import HTTPException


class ReturnService:
    def __init__(self, db: Session):
        self.db = db

    def create_return(self, data: ReturnRequestCreate, user_id: int):
        """Create new return request"""
        return_req = ReturnRequest(
            **data.model_dump(),
            created_by=user_id,
            status=ReturnStatus.SUBMITTED
        )
        self.db.add(return_req)
        self.db.commit()
        self.db.refresh(return_req)

        # Create initial inventory move
        move = ReturnInventoryMove(
            return_request_id=return_req.id,
            to_zone=InventoryZone.RECEIVED,
            qty=1,
            moved_by=user_id
        )
        self.db.add(move)
        self.db.commit()

        return return_req

    def get_return(self, return_id: int):
        """Get return by ID"""
        return_req = self.db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
        if not return_req:
            raise HTTPException(status_code=404, detail="Return request not found")
        return return_req

    def receive_return(self, return_id: int, data, user_id: int):
        """Mark return as received"""
        return_req = self.get_return(return_id)
        return_req.status = ReturnStatus.RECEIVED
        self.db.commit()
        return {"message": "Return marked as received"}

    def list_returns(self, status=None, serial_number=None, skip=0, limit=50):
        """List returns with filters"""
        query = self.db.query(ReturnRequest)
        if status:
            query = query.filter(ReturnRequest.status == status)
        if serial_number:
            query = query.filter(ReturnRequest.serial_number == serial_number)
        return query.offset(skip).limit(limit).all()
