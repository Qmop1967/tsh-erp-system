"""Returns API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from prss.db import get_db
from prss.schemas.return_request import *
from prss.services.return_service import ReturnService
from prss.security.auth import get_current_user

router = APIRouter(prefix="/returns", tags=["returns"])


@router.post("/", response_model=ReturnRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_return_request(
    request: ReturnRequestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new return request"""
    service = ReturnService(db)
    return service.create_return(request, current_user.id)


@router.get("/{return_id}", response_model=ReturnRequestResponse)
async def get_return_request(
    return_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get return request by ID"""
    service = ReturnService(db)
    return service.get_return(return_id)


@router.post("/{return_id}/receive")
async def receive_return(
    return_id: int,
    request: ReturnReceiveRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark return as received"""
    service = ReturnService(db)
    return service.receive_return(return_id, request, current_user.id)


@router.get("/", response_model=List[ReturnRequestResponse])
async def list_returns(
    status: Optional[str] = None,
    serial_number: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List return requests with filters"""
    service = ReturnService(db)
    return service.list_returns(status=status, serial_number=serial_number, skip=skip, limit=limit)
