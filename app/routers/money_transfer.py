"""
Money Transfer API Router for TSH ERP System
CRITICAL: API endpoints for fraud prevention and transfer tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.db.database import get_db
from app.services.money_transfer_service import MoneyTransferService
from app.schemas.money_transfer import (
    MoneyTransferCreate, MoneyTransferUpdate, MoneyTransferResponse,
    MoneyTransferSummary, WeeklyCommissionReport, DashboardStats,
    FraudAlert, TransferPlatformConfig
)
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/money-transfers", tags=["Money Transfers - FRAUD PREVENTION"])


@router.post("/", response_model=MoneyTransferResponse, status_code=status.HTTP_201_CREATED)
async def create_money_transfer(
    transfer_data: MoneyTransferCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🚨 CRITICAL: Create new money transfer with automatic fraud detection
    
    This endpoint is essential for preventing fraud in your $35K weekly transfers.
    Every transfer is automatically checked for suspicious patterns.
    """
    service = MoneyTransferService(db)
    
    # Only salespersons can create transfers for themselves
    # Managers can create transfers for any salesperson
    if current_user.role.name == "salesperson":
        salesperson_id = current_user.id
    else:
        # For managers/admins, they can specify the salesperson
        salesperson_id = current_user.id  # Default to current user if not specified
    
    try:
        transfer = service.create_transfer(transfer_data, salesperson_id)
        return transfer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create transfer: {str(e)}"
        )


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📊 Get comprehensive dashboard statistics
    
    Critical for monitoring all money transfers and fraud alerts.
    Shows real-time status of your $35K weekly transfers.
    """
    service = MoneyTransferService(db)
    return service.get_dashboard_stats()


@router.get("/fraud-alerts", response_model=List[FraudAlert])
async def get_fraud_alerts(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🚨 Get fraud alerts - IMMEDIATE ATTENTION REQUIRED
    
    Lists all suspicious transfers that need your review.
    Critical for preventing financial losses.
    """
    service = MoneyTransferService(db)
    return service.get_fraud_alerts(limit)


@router.get("/salesperson/{salesperson_id}", response_model=List[MoneyTransferResponse])
async def get_salesperson_transfers(
    salesperson_id: int,
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all transfers for a specific salesperson
    
    Shows complete transfer history for tracking and verification.
    """
    service = MoneyTransferService(db)
    
    # Salespersons can only see their own transfers
    if current_user.role.name == "salesperson" and current_user.id != salesperson_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own transfers"
        )
    
    return service.get_salesperson_transfers(salesperson_id, limit)


@router.get("/my-transfers", response_model=List[MoneyTransferResponse])
async def get_my_transfers(
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's transfers
    
    For salespersons to view their own transfer history.
    """
    service = MoneyTransferService(db)
    return service.get_salesperson_transfers(current_user.id, limit)


@router.get("/{transfer_id}", response_model=MoneyTransferResponse)
async def get_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific transfer details
    
    Shows complete information about a single transfer.
    """
    service = MoneyTransferService(db)
    transfer = service.get_transfer_by_id(transfer_id)
    
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )
    
    # Check permissions
    if current_user.role.name == "salesperson" and transfer.salesperson_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own transfers"
        )
    
    return transfer


@router.put("/{transfer_id}", response_model=MoneyTransferResponse)
async def update_transfer(
    transfer_id: int,
    update_data: MoneyTransferUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update transfer status and verification
    
    Used by managers to verify transfers and update their status.
    """
    # Only managers/admins can update transfers
    if current_user.role.name == "salesperson":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can update transfers"
        )
    
    service = MoneyTransferService(db)
    try:
        return service.update_transfer(transfer_id, update_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update transfer: {str(e)}"
        )


@router.get("/reports/weekly-commission/{salesperson_id}", response_model=WeeklyCommissionReport)
async def get_weekly_commission_report(
    salesperson_id: int,
    week_start: date = Query(..., description="Start date of the week (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📋 Generate weekly commission report
    
    Critical for verifying salesperson commissions and preventing fraud.
    Shows expected vs claimed commissions.
    """
    service = MoneyTransferService(db)
    
    # Check permissions
    if current_user.role.name == "salesperson" and current_user.id != salesperson_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own commission reports"
        )
    
    return service.get_weekly_commission_report(salesperson_id, week_start)


@router.post("/{transfer_id}/verify-receipt")
async def verify_receipt(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify transfer receipt
    
    Marks receipt as verified by manager.
    """
    # Only managers can verify receipts
    if current_user.role.name == "salesperson":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can verify receipts"
        )
    
    service = MoneyTransferService(db)
    update_data = MoneyTransferUpdate(receipt_verified=True)
    
    try:
        return service.update_transfer(transfer_id, update_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to verify receipt: {str(e)}"
        )


@router.post("/{transfer_id}/confirm-received")
async def confirm_money_received(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm money has been received
    
    Marks transfer as complete when money is actually received.
    """
    # Only managers can confirm receipt
    if current_user.role.name == "salesperson":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can confirm money receipt"
        )
    
    service = MoneyTransferService(db)
    from app.schemas.money_transfer import TransferStatus
    update_data = MoneyTransferUpdate(
        money_received=True,
        received_datetime=datetime.utcnow(),
        status=TransferStatus.RECEIVED
    )
    
    try:
        return service.update_transfer(transfer_id, update_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to confirm receipt: {str(e)}"
        )


@router.get("/summary/all", response_model=List[MoneyTransferSummary])
async def get_all_salesperson_summaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary for all salespersons
    
    Overview of all salesperson transfer activities.
    """
    service = MoneyTransferService(db)
    stats = service.get_dashboard_stats()
    return stats.salesperson_summaries 