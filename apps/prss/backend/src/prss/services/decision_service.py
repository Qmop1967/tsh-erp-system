"""Decision business logic"""
from sqlalchemy.orm import Session
from prss.models.all_models import Decision, ReturnRequest, OutboxEvent
from prss.models.base import ReturnStatus, FinalDecision, OutboxStatus
from prss.schemas.decision import DecisionCreate
import json


class DecisionService:
    def __init__(self, db: Session):
        self.db = db

    def create_decision(self, return_id: int, data: DecisionCreate, user_id: int):
        """Create final decision"""
        decision = Decision(**data.model_dump(), approved_by=user_id)
        self.db.add(decision)

        # Update return status
        return_req = self.db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
        return_req.status = ReturnStatus.AWAITING_DECISION

        # Create outbox event
        event = OutboxEvent(
            topic="prss.return.finalized",
            payload=json.dumps({
                "return_request_id": return_id,
                "final_decision": data.final_decision.value,
                "product_id": return_req.product_id
            }),
            status=OutboxStatus.PENDING
        )
        self.db.add(event)

        self.db.commit()
        return {"message": "Decision recorded"}

    def transfer_to_inventory(self, return_id: int, user_id: int):
        """Transfer to inventory system"""
        # This would call the inventory integration client
        return {"message": "Transfer initiated", "transfer_ref": f"INV-T-{return_id}"}
