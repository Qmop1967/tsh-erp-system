"""
Money Transfers BFF Router for Salesperson App
12 endpoints for cash management and fraud prevention

Business Purpose:
- Track $35,000 USD weekly transfers from 12 travel salespersons
- Support ALTaif Bank, ZAIN Cash, SuperQi platforms
- Receipt photo upload and verification
- Cash box balance tracking
- Fraud prevention with automatic alerts
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, or_
from typing import Optional, List
from datetime import datetime, date, timedelta
from decimal import Decimal
import os
import uuid

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.money_transfer import MoneyTransfer
from app.models.customer import Customer
from app.schemas.money_transfer import (
    MoneyTransferCreate,
    MoneyTransferUpdate,
    MoneyTransferResponse,
    TransferStatus,
    TransferPlatform
)
from app.schemas.salesperson import BatchOperationResponse

router = APIRouter(prefix="/transfers", tags=["Salesperson Money Transfers"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_fraud_indicators(transfer: MoneyTransfer) -> tuple[bool, str]:
    """
    Check for fraud indicators in money transfer

    Red Flags:
    - Commission > 5% deviation from expected (2.25% rate)
    - Multiple transfers within short time
    - No GPS coordinates
    - Large amount (> $5000)
    - Weekend transfer
    """
    is_suspicious = False
    reasons = []

    # Check commission calculation
    expected_commission = transfer.gross_sales * 2.25 / 100
    deviation = abs(transfer.claimed_commission - expected_commission) / expected_commission
    if deviation > 0.05:  # > 5% deviation
        is_suspicious = True
        reasons.append(f"Commission deviation {deviation*100:.1f}%")

    # Check for GPS coordinates
    if not transfer.gps_latitude or not transfer.gps_longitude:
        is_suspicious = True
        reasons.append("No GPS location")

    # Check for large amount
    if transfer.amount_usd > 5000:
        is_suspicious = True
        reasons.append(f"Large amount: ${transfer.amount_usd:,.2f}")

    # Check for weekend transfer
    if transfer.transfer_datetime.weekday() >= 5:  # Saturday or Sunday
        is_suspicious = True
        reasons.append("Weekend transfer")

    return is_suspicious, "; ".join(reasons)


async def save_receipt_photo(file: UploadFile, transfer_id: int) -> str:
    """
    Save receipt photo to filesystem

    Returns: URL/path to saved photo
    TODO: Upload to S3 in production
    """
    # Create uploads directory if not exists
    upload_dir = "/var/www/tsh-erp/uploads/transfer_receipts"
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"transfer_{transfer_id}_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)

    # Save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Return URL path
    return f"/uploads/transfer_receipts/{unique_filename}"


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/", response_model=MoneyTransferResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    transfer: MoneyTransferCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new money transfer

    Business Logic:
    - Salesperson records transfer after sending money
    - Automatic commission calculation (2.25%)
    - Fraud detection checks
    - GPS location required
    - Receipt photo optional (can upload later)

    Authorization:
    - Only salespersons can create transfers for themselves
    """
    # Authorization
    if not current_user.is_salesperson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only salespersons can create transfers"
        )

    try:
        # Calculate commission
        calculated_commission = transfer.gross_sales * 2.25 / 100

        # Create transfer record
        money_transfer = MoneyTransfer(
            salesperson_id=current_user.id,
            salesperson_name=current_user.name,
            amount_usd=transfer.amount_usd,
            amount_iqd=transfer.amount_iqd,
            exchange_rate=transfer.exchange_rate,
            gross_sales=transfer.gross_sales,
            commission_rate=2.25,
            calculated_commission=calculated_commission,
            claimed_commission=transfer.claimed_commission,
            transfer_platform=transfer.transfer_platform.value,
            platform_reference=transfer.platform_reference,
            transfer_fee=transfer.transfer_fee,
            transfer_datetime=datetime.utcnow(),
            gps_latitude=transfer.gps_latitude,
            gps_longitude=transfer.gps_longitude,
            location_name=transfer.location_name,
            receipt_photo_url=transfer.receipt_photo_url,
            status="pending",
            money_received=False
        )

        # Run fraud checks
        is_suspicious, fraud_reasons = check_fraud_indicators(money_transfer)
        money_transfer.is_suspicious = is_suspicious
        money_transfer.fraud_alert_reason = fraud_reasons if is_suspicious else None
        money_transfer.manager_approval_required = is_suspicious

        db.add(money_transfer)
        db.commit()
        db.refresh(money_transfer)

        return money_transfer

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transfer: {str(e)}"
        )


@router.get("/", response_model=List[MoneyTransferResponse])
async def get_transfer_list(
    salesperson_id: Optional[int] = Query(None, description="Filter by salesperson"),
    status: Optional[str] = Query(None, description="Filter by status"),
    method: Optional[str] = Query(None, description="Filter by platform"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transfer list with filters

    Authorization:
    - Salespersons see only their own transfers
    - Managers/admins see all transfers
    """
    # Build query
    query = db.query(MoneyTransfer)

    # Authorization filter
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    if not is_manager:
        # Salespersons can only see their own
        query = query.filter(MoneyTransfer.salesperson_id == current_user.id)
    elif salesperson_id:
        # Managers can filter by salesperson
        query = query.filter(MoneyTransfer.salesperson_id == salesperson_id)

    # Apply filters
    if status:
        query = query.filter(MoneyTransfer.status == status)

    if method:
        query = query.filter(MoneyTransfer.transfer_platform == method)

    if start_date:
        query = query.filter(func.date(MoneyTransfer.transfer_datetime) >= start_date)

    if end_date:
        query = query.filter(func.date(MoneyTransfer.transfer_datetime) <= end_date)

    # Order and paginate
    transfers = query.order_by(
        desc(MoneyTransfer.transfer_datetime)
    ).offset(offset).limit(limit).all()

    return transfers


@router.get("/{transfer_id}", response_model=MoneyTransferResponse)
async def get_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transfer details

    Authorization:
    - Salespersons can view their own transfers
    - Managers can view any transfer
    """
    transfer = db.query(MoneyTransfer).filter(MoneyTransfer.id == transfer_id).first()

    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )

    # Authorization check
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    is_owner = transfer.salesperson_id == current_user.id

    if not is_manager and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own transfers"
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
    Update transfer

    Authorization:
    - Salespersons can update their own pending transfers
    - Managers can update any transfer
    """
    transfer = db.query(MoneyTransfer).filter(MoneyTransfer.id == transfer_id).first()

    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )

    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    is_owner = transfer.salesperson_id == current_user.id

    if not is_manager and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own transfers"
        )

    # Salespersons can only update pending transfers
    if is_owner and not is_manager and transfer.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update pending transfers"
        )

    # Apply updates
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(transfer, field, value)

    transfer.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(transfer)

    return transfer


@router.delete("/{transfer_id}", response_model=dict)
async def delete_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete transfer

    Authorization:
    - Only pending transfers can be deleted
    - Salespersons can delete their own pending transfers (within 24 hours)
    - Managers can delete any pending transfer
    """
    transfer = db.query(MoneyTransfer).filter(MoneyTransfer.id == transfer_id).first()

    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )

    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    is_owner = transfer.salesperson_id == current_user.id

    if not is_manager and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own transfers"
        )

    # Only pending transfers can be deleted
    if transfer.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete pending transfers"
        )

    # Check age restriction for salespersons
    if is_owner and not is_manager:
        age_hours = (datetime.utcnow() - transfer.created_at).total_seconds() / 3600
        if age_hours > 24:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete transfers older than 24 hours"
            )

    db.delete(transfer)
    db.commit()

    return {
        "success": True,
        "message": f"Transfer {transfer_id} deleted successfully"
    }


@router.post("/{transfer_id}/receipt", response_model=dict)
async def upload_receipt(
    transfer_id: int,
    receipt_photo: UploadFile = File(..., description="Receipt photo (JPG/PNG)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload receipt photo for transfer

    Business Logic:
    - Photos stored in filesystem (TODO: S3 in production)
    - Supports JPG, PNG formats
    - Max size: 10 MB

    Authorization:
    - Salespersons can upload to their own transfers
    - Managers can upload to any transfer
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if receipt_photo.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG and PNG images are allowed"
        )

    # Get transfer
    transfer = db.query(MoneyTransfer).filter(MoneyTransfer.id == transfer_id).first()

    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )

    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    is_owner = transfer.salesperson_id == current_user.id

    if not is_manager and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload receipts to your own transfers"
        )

    try:
        # Save photo
        photo_url = await save_receipt_photo(receipt_photo, transfer_id)

        # Update transfer
        transfer.receipt_photo_url = photo_url
        transfer.updated_at = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "photo_url": photo_url,
            "uploaded_at": datetime.utcnow()
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload receipt: {str(e)}"
        )


@router.post("/{transfer_id}/verify", response_model=MoneyTransferResponse)
async def verify_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify transfer (manager action)

    Business Logic:
    - Changes status from pending to verified
    - Checks fraud indicators
    - Requires manager role

    Authorization:
    - Only managers/admins can verify
    """
    # Authorization
    if not current_user.role.name.lower() in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can verify transfers"
        )

    transfer = db.query(MoneyTransfer).filter(MoneyTransfer.id == transfer_id).first()

    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )

    # Update status
    transfer.status = "verified"
    transfer.receipt_verified = True
    transfer.commission_verified = True
    transfer.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(transfer)

    return transfer


@router.post("/{transfer_id}/complete", response_model=MoneyTransferResponse)
async def complete_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete transfer (mark money received)

    Business Logic:
    - Changes status to received
    - Records received datetime
    - Requires manager role

    Authorization:
    - Only managers/admins can complete
    """
    # Authorization
    if not current_user.role.name.lower() in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can complete transfers"
        )

    transfer = db.query(MoneyTransfer).filter(MoneyTransfer.id == transfer_id).first()

    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )

    # Update status
    transfer.status = "received"
    transfer.money_received = True
    transfer.received_datetime = datetime.utcnow()
    transfer.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(transfer)

    return transfer


@router.post("/batch-sync", response_model=BatchOperationResponse)
async def batch_sync_transfers(
    transfers: List[MoneyTransferCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Batch sync offline transfers

    Business Logic:
    - Used when salesperson comes back online
    - Mobile app stores transfers locally during offline
    - Syncs all pending transfers in one batch
    """
    # Authorization
    if not current_user.is_salesperson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only salespersons can sync transfers"
        )

    synced = 0
    failed = 0
    errors = []
    transfer_ids = []

    for idx, transfer_data in enumerate(transfers):
        try:
            # Calculate commission
            calculated_commission = transfer_data.gross_sales * 2.25 / 100

            # Create transfer
            money_transfer = MoneyTransfer(
                salesperson_id=current_user.id,
                salesperson_name=current_user.name,
                amount_usd=transfer_data.amount_usd,
                amount_iqd=transfer_data.amount_iqd,
                exchange_rate=transfer_data.exchange_rate,
                gross_sales=transfer_data.gross_sales,
                commission_rate=2.25,
                calculated_commission=calculated_commission,
                claimed_commission=transfer_data.claimed_commission,
                transfer_platform=transfer_data.transfer_platform.value,
                platform_reference=transfer_data.platform_reference,
                transfer_fee=transfer_data.transfer_fee,
                transfer_datetime=datetime.utcnow(),
                gps_latitude=transfer_data.gps_latitude,
                gps_longitude=transfer_data.gps_longitude,
                location_name=transfer_data.location_name,
                receipt_photo_url=transfer_data.receipt_photo_url,
                status="pending",
                money_received=False
            )

            # Run fraud checks
            is_suspicious, fraud_reasons = check_fraud_indicators(money_transfer)
            money_transfer.is_suspicious = is_suspicious
            money_transfer.fraud_alert_reason = fraud_reasons if is_suspicious else None
            money_transfer.manager_approval_required = is_suspicious

            db.add(money_transfer)
            db.flush()

            transfer_ids.append(money_transfer.id)
            synced += 1

        except Exception as e:
            failed += 1
            errors.append({
                "index": idx,
                "error": str(e),
                "transfer": transfer_data.dict()
            })

    db.commit()

    return BatchOperationResponse(
        success=failed == 0,
        total=len(transfers),
        uploaded=synced,
        failed=failed,
        errors=errors,
        ids=transfer_ids
    )


@router.get("/statistics", response_model=dict)
async def get_transfer_statistics(
    salesperson_id: Optional[int] = Query(None, description="Filter by salesperson"),
    period: str = Query("month", description="Period: today, week, month, year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transfer statistics

    Returns:
    - Total transfers
    - Total amount
    - Pending/verified/received counts
    - Average transfer amount
    - Platform breakdown
    """
    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    if not is_manager:
        salesperson_id = current_user.id

    # Calculate date range
    today = datetime.utcnow().date()
    if period == "today":
        start_date = today
    elif period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today - timedelta(days=30)
    elif period == "year":
        start_date = today - timedelta(days=365)
    else:
        start_date = None

    # Build query
    query = db.query(MoneyTransfer)

    if salesperson_id:
        query = query.filter(MoneyTransfer.salesperson_id == salesperson_id)

    if start_date:
        query = query.filter(func.date(MoneyTransfer.transfer_datetime) >= start_date)

    # Get statistics
    all_transfers = query.all()

    total_count = len(all_transfers)
    total_usd = sum(t.amount_usd for t in all_transfers)
    total_iqd = sum(t.amount_iqd for t in all_transfers)

    pending_count = len([t for t in all_transfers if t.status == "pending"])
    verified_count = len([t for t in all_transfers if t.status == "verified"])
    received_count = len([t for t in all_transfers if t.status == "received"])

    avg_amount_usd = total_usd / total_count if total_count > 0 else 0

    # Platform breakdown
    platform_breakdown = {}
    for transfer in all_transfers:
        platform = transfer.transfer_platform
        if platform not in platform_breakdown:
            platform_breakdown[platform] = {"count": 0, "total_usd": 0}
        platform_breakdown[platform]["count"] += 1
        platform_breakdown[platform]["total_usd"] += transfer.amount_usd

    return {
        "period": period,
        "total_transfers": total_count,
        "total_amount_usd": total_usd,
        "total_amount_iqd": total_iqd,
        "pending_count": pending_count,
        "verified_count": verified_count,
        "received_count": received_count,
        "average_amount_usd": avg_amount_usd,
        "platform_breakdown": platform_breakdown
    }


@router.get("/cash-box", response_model=dict)
async def get_cash_box_balance(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cash box balance by payment method

    Business Logic:
    - Calculates current cash on hand
    - Groups by payment method (Cash IQD, Cash USD, ALTaif, ZAIN Cash, SuperQi)
    - Shows pending transfers not yet sent
    - Critical for cash management

    Returns:
    - cashIQD: Physical IQD cash
    - cashUSD: Physical USD cash
    - altaifIQD: ALTaif balance
    - zainCashIQD: ZAIN Cash balance
    - superQiIQD: SuperQi balance
    - totalIQD: Total in IQD equivalent
    """
    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    if not is_manager and current_user.id != salesperson_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own cash box"
        )

    # Get all transfers for salesperson
    transfers = db.query(MoneyTransfer).filter(
        MoneyTransfer.salesperson_id == salesperson_id
    ).all()

    # Calculate balances by platform
    balances = {
        "cashIQD": 0,
        "cashUSD": 0,
        "altaifIQD": 0,
        "zainCashIQD": 0,
        "superQiIQD": 0,
        "totalIQD": 0,
        "totalUSD": 0
    }

    # TODO: This is simplified - need actual cash collection tracking
    # For now, showing pending transfers as "cash on hand"

    pending_transfers = [t for t in transfers if t.status == "pending"]

    for transfer in pending_transfers:
        if "ALTaif" in transfer.transfer_platform:
            balances["altaifIQD"] += transfer.amount_iqd
        elif "ZAIN" in transfer.transfer_platform:
            balances["zainCashIQD"] += transfer.amount_iqd
        elif "SuperQi" in transfer.transfer_platform:
            balances["superQiIQD"] += transfer.amount_iqd

    balances["totalIQD"] = (
        balances["cashIQD"] +
        balances["altaifIQD"] +
        balances["zainCashIQD"] +
        balances["superQiIQD"]
    )

    balances["totalUSD"] = balances["cashUSD"]

    return balances


@router.post("/reconcile", response_model=dict)
async def reconcile_transfers(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    date: date = Query(..., description="Reconciliation date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reconcile transfers for a specific date

    Business Logic:
    - Managers reconcile daily transfers
    - Matches transfers with bank statements
    - Marks all as verified if reconciled

    Authorization:
    - Only managers can reconcile
    """
    # Authorization
    if not current_user.role.name.lower() in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can reconcile transfers"
        )

    # Get transfers for date
    transfers = db.query(MoneyTransfer).filter(
        and_(
            MoneyTransfer.salesperson_id == salesperson_id,
            func.date(MoneyTransfer.transfer_datetime) == date
        )
    ).all()

    reconciled_count = 0
    for transfer in transfers:
        if transfer.status == "pending":
            transfer.status = "verified"
            transfer.updated_at = datetime.utcnow()
            reconciled_count += 1

    db.commit()

    return {
        "success": True,
        "date": date,
        "salesperson_id": salesperson_id,
        "total_transfers": len(transfers),
        "reconciled_count": reconciled_count
    }


@router.get("/../customers", response_model=List[dict])
async def get_customers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(100, le=500, description="Maximum customers to return"),
    search: Optional[str] = Query(None, description="Search by name or phone")
):
    """
    Get list of customers assigned to the current salesperson

    Business Logic:
    - Only returns customers assigned to the logged-in salesperson
    - Filters by salesperson_id from customers table
    - Supports search by name or phone number
    - Returns customer details needed for POS sales

    Authorization:
    - Only salespersons can access their assigned customers
    - Returns empty list if no customers assigned
    """
    # Build query for customers assigned to this salesperson
    query = db.query(Customer).filter(
        and_(
            Customer.salesperson_id == current_user.id,
            Customer.is_active == True
        )
    )

    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Customer.name.ilike(search_term),
                Customer.name_ar.ilike(search_term),
                Customer.phone.ilike(search_term),
                Customer.company_name.ilike(search_term)
            )
        )

    # Execute query with limit
    customers = query.order_by(Customer.name).limit(limit).all()

    # Format response for mobile app
    customer_list = []
    for customer in customers:
        customer_list.append({
            "id": str(customer.id),
            "name": customer.name_ar or customer.name,  # Prefer Arabic name
            "phone": customer.phone or "لا يوجد رقم",
            "email": customer.email or f"customer{customer.id}@tsh.sale",
            "company_name": customer.company_name_ar or customer.company_name,
            "credit_limit": float(customer.credit_limit) if customer.credit_limit else 0.0,
            "payment_terms": customer.payment_terms,
            "currency": customer.currency,
            "city": customer.city,
            "is_active": customer.is_active
        })

    return customer_list


@router.get("/exchange-rate")
async def get_exchange_rate(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current IQD/USD exchange rate

    Business Logic:
    - Returns current exchange rate for currency conversion
    - Used for money transfer calculations
    - Default: 1 USD = 1,310 IQD (as of Nov 2025)

    TODO: Integrate with real-time exchange rate API
    """
    # TODO: Query from exchange_rates table or external API
    # For now, return static rate
    return {
        "base_currency": "USD",
        "target_currency": "IQD",
        "rate": 1310.0,
        "last_updated": datetime.utcnow().isoformat(),
        "source": "static"  # TODO: Change to "database" or "api"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for money transfers service"""
    return {
        "status": "healthy",
        "service": "money-transfers-bff",
        "version": "1.0.0"
    }
