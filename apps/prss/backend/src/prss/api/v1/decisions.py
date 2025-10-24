"""Decision API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from prss.db import get_db
from prss.schemas.decision import *
from prss.services.decision_service import DecisionService
from prss.security.auth import get_current_user, require_role

router = APIRouter(prefix="/returns", tags=["decisions"])


@router.post("/{return_id}/decide", dependencies=[Depends(require_role(["admin", "warranty_officer"]))])
async def make_decision(
    return_id: int,
    decision: DecisionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Make final decision on return"""
    service = DecisionService(db)
    return service.create_decision(return_id, decision, current_user.id)


@router.post("/{return_id}/transfer-to-inventory", dependencies=[Depends(require_role(["admin"]))])
async def transfer_to_inventory(
    return_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Transfer approved return to main inventory"""
    service = DecisionService(db)
    return service.transfer_to_inventory(return_id, current_user.id)
