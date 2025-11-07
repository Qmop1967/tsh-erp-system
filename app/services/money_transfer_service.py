"""
Money Transfer Service for TSH ERP System
CRITICAL: Business logic for fraud prevention and transfer tracking
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from app.models.money_transfer import MoneyTransfer, TransferPlatform
from app.models.user import User
from app.schemas.money_transfer import (
    MoneyTransferCreate, MoneyTransferUpdate, MoneyTransferResponse,
    MoneyTransferSummary, WeeklyCommissionReport, DashboardStats,
    FraudAlert, TransferStatus
)


class MoneyTransferService:
    """Service class for money transfer operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_transfer(self, transfer_data: MoneyTransferCreate, salesperson_id: int) -> MoneyTransferResponse:
        """
        Create a new money transfer with automatic fraud detection
        """
        # Get salesperson information
        salesperson = self.db.query(User).filter(User.id == salesperson_id).first()
        if not salesperson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salesperson not found"
            )
        
        # Calculate expected commission
        expected_commission = (transfer_data.gross_sales * 2.25) / 100
        
        # Create transfer record
        transfer = MoneyTransfer(
            salesperson_id=salesperson_id,
            salesperson_name=salesperson.name,
            amount_usd=transfer_data.amount_usd,
            amount_iqd=transfer_data.amount_iqd,
            exchange_rate=transfer_data.exchange_rate,
            gross_sales=transfer_data.gross_sales,
            calculated_commission=expected_commission,
            claimed_commission=transfer_data.claimed_commission,
            transfer_platform=transfer_data.transfer_platform.value,
            platform_reference=transfer_data.platform_reference,
            transfer_fee=transfer_data.transfer_fee,
            transfer_datetime=datetime.utcnow(),
            gps_latitude=transfer_data.gps_latitude,
            gps_longitude=transfer_data.gps_longitude,
            location_name=transfer_data.location_name,
            receipt_photo_url=transfer_data.receipt_photo_url
        )
        
        # Automatic fraud detection
        self._detect_fraud(transfer)
        
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        
        # Log critical fraud alerts
        if transfer.is_suspicious:
            self._log_fraud_alert(transfer)
        
        return MoneyTransferResponse.model_validate(transfer)
    
    def get_transfer_by_id(self, transfer_id: int) -> Optional[MoneyTransferResponse]:
        """Get transfer by ID"""
        transfer = self.db.query(MoneyTransfer).filter(MoneyTransfer.id == transfer_id).first()
        if not transfer:
            return None
        return MoneyTransferResponse.model_validate(transfer)
    
    def get_salesperson_transfers(self, salesperson_id: int, limit: int = 100) -> List[MoneyTransferResponse]:
        """Get all transfers for a salesperson"""
        transfers = self.db.query(MoneyTransfer)\
            .filter(MoneyTransfer.salesperson_id == salesperson_id)\
            .order_by(desc(MoneyTransfer.created_at))\
            .limit(limit).all()
        
        return [MoneyTransferResponse.model_validate(t) for t in transfers]
    
    def update_transfer(self, transfer_id: int, update_data: MoneyTransferUpdate) -> MoneyTransferResponse:
        """Update transfer status and verification"""
        transfer = self.db.query(MoneyTransfer).filter(MoneyTransfer.id == transfer_id).first()
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            if hasattr(transfer, field):
                setattr(transfer, field, value)
        
        # Update timestamp
        transfer.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transfer)
        
        return MoneyTransferResponse.model_validate(transfer)
    
    def get_dashboard_stats(self) -> DashboardStats:
        """Get comprehensive dashboard statistics"""
        today = date.today()
        
        # Basic stats
        total_pending = self.db.query(func.sum(MoneyTransfer.amount_usd))\
            .filter(MoneyTransfer.status == TransferStatus.PENDING.value).scalar() or 0
        
        total_received_today = self.db.query(func.sum(MoneyTransfer.amount_usd))\
            .filter(
                and_(
                    MoneyTransfer.money_received.is_(True),
                    func.date(MoneyTransfer.received_datetime) == today
                )
            ).scalar() or 0
        
        suspicious_count = self.db.query(func.count(MoneyTransfer.id))\
            .filter(MoneyTransfer.is_suspicious.is_(True)).scalar() or 0
        
        pending_count = self.db.query(func.count(MoneyTransfer.id))\
            .filter(MoneyTransfer.status == TransferStatus.PENDING.value).scalar() or 0
        
        # Salesperson summaries
        salesperson_summaries = self._get_salesperson_summaries()
        
        # Platform breakdown
        platform_breakdown = self._get_platform_breakdown()
        
        return DashboardStats(
            total_pending_amount=total_pending,
            total_received_today=total_received_today,
            suspicious_transfers_count=suspicious_count,
            pending_transfers_count=pending_count,
            salesperson_summaries=salesperson_summaries,
            platform_breakdown=platform_breakdown
        )
    
    def get_fraud_alerts(self, limit: int = 50) -> List[FraudAlert]:
        """Get recent fraud alerts"""
        suspicious_transfers = self.db.query(MoneyTransfer)\
            .filter(MoneyTransfer.is_suspicious == True)\
            .order_by(desc(MoneyTransfer.created_at))\
            .limit(limit).all()
        
        alerts = []
        for transfer in suspicious_transfers:
            priority = "high" if transfer.amount_usd > 10000 else "medium"
            alerts.append(FraudAlert(
                transfer_id=transfer.id,
                salesperson_name=transfer.salesperson_name,
                alert_reason=transfer.fraud_alert_reason or "Suspicious activity detected",
                amount_usd=transfer.amount_usd,
                created_at=transfer.created_at,
                priority=priority
            ))
        
        return alerts
    
    def get_weekly_commission_report(self, salesperson_id: int, week_start: date) -> WeeklyCommissionReport:
        """Generate weekly commission report for salesperson"""
        week_end = week_start + timedelta(days=6)
        
        # Get transfers for the week
        transfers = self.db.query(MoneyTransfer)\
            .filter(
                and_(
                    MoneyTransfer.salesperson_id == salesperson_id,
                    func.date(MoneyTransfer.transfer_datetime) >= week_start,
                    func.date(MoneyTransfer.transfer_datetime) <= week_end
                )
            ).all()
        
        # Calculate totals
        total_sales = sum(t.gross_sales for t in transfers)
        calculated_commission = sum(t.calculated_commission for t in transfers)
        commission_taken = sum(t.claimed_commission for t in transfers)
        total_transferred = sum(t.amount_usd for t in transfers)
        
        # Get salesperson name
        salesperson = self.db.query(User).filter(User.id == salesperson_id).first()
        
        return WeeklyCommissionReport(
            salesperson_id=salesperson_id,
            salesperson_name=salesperson.name if salesperson else "Unknown",
            week_start=datetime.combine(week_start, datetime.min.time()),
            week_end=datetime.combine(week_end, datetime.max.time()),
            total_sales=total_sales,
            calculated_commission=calculated_commission,
            commission_taken=commission_taken,
            commission_difference=commission_taken - calculated_commission,
            transfer_count=len(transfers),
            total_transferred=total_transferred,
            is_approved=False  # Manual approval required
        )
    
    def _detect_fraud(self, transfer: MoneyTransfer):
        """Internal fraud detection logic"""
        fraud_reasons = []
        
        # Check commission calculation
        commission_difference = abs(transfer.claimed_commission - transfer.calculated_commission)
        if commission_difference > (transfer.calculated_commission * 0.05):  # 5% tolerance
            fraud_reasons.append(f"Commission mismatch: Expected {transfer.calculated_commission:.2f}, Claimed {transfer.claimed_commission:.2f}")
            transfer.is_suspicious = True
        
        # Check for large amounts
        if transfer.amount_usd > 15000:
            fraud_reasons.append(f"Large transfer amount: ${transfer.amount_usd:,.2f}")
            transfer.manager_approval_required = True
        
        # Check for unusual patterns (multiple transfers same day)
        today_transfers = self.db.query(func.count(MoneyTransfer.id))\
            .filter(
                and_(
                    MoneyTransfer.salesperson_id == transfer.salesperson_id,
                    func.date(MoneyTransfer.transfer_datetime) == date.today()
                )
            ).scalar() or 0
        
        if today_transfers >= 3:
            fraud_reasons.append(f"Multiple transfers today: {today_transfers + 1}")
            transfer.is_suspicious = True
        
        # Store fraud reasons
        if fraud_reasons:
            transfer.fraud_alert_reason = "; ".join(fraud_reasons)
    
    def _get_salesperson_summaries(self) -> List[MoneyTransferSummary]:
        """Get summary statistics for each salesperson"""
        # Get all salespersons with transfers
        salespersons = self.db.query(User)\
            .join(MoneyTransfer)\
            .filter(User.is_salesperson == True)\
            .distinct().all()
        
        summaries = []
        for salesperson in salespersons:
            transfers = self.db.query(MoneyTransfer)\
                .filter(MoneyTransfer.salesperson_id == salesperson.id).all()
            
            total_amount_usd = sum(t.amount_usd for t in transfers)
            total_amount_iqd = sum(t.amount_iqd for t in transfers)
            pending_transfers = len([t for t in transfers if t.status == TransferStatus.PENDING.value])
            suspicious_transfers = len([t for t in transfers if t.is_suspicious])
            total_commission = sum(t.claimed_commission for t in transfers)
            last_transfer_date = max([t.transfer_datetime for t in transfers], default=None)
            
            summaries.append(MoneyTransferSummary(
                salesperson_id=salesperson.id,
                salesperson_name=salesperson.name,
                total_transfers=len(transfers),
                total_amount_usd=total_amount_usd,
                total_amount_iqd=total_amount_iqd,
                pending_transfers=pending_transfers,
                suspicious_transfers=suspicious_transfers,
                total_commission=total_commission,
                last_transfer_date=last_transfer_date
            ))
        
        return summaries
    
    def _get_platform_breakdown(self) -> Dict[str, Any]:
        """Get breakdown by transfer platform"""
        platform_stats = self.db.query(
            MoneyTransfer.transfer_platform,
            func.count(MoneyTransfer.id).label('count'),
            func.sum(MoneyTransfer.amount_usd).label('total_amount')
        ).group_by(MoneyTransfer.transfer_platform).all()
        
        breakdown = {}
        for platform, count, total_amount in platform_stats:
            breakdown[platform] = {
                'count': count,
                'total_amount': float(total_amount or 0)
            }
        
        return breakdown
    
    def _log_fraud_alert(self, transfer: MoneyTransfer):
        """Log fraud alert for monitoring"""
        # In a real system, this would send notifications, log to security system, etc.
        print(f"🚨 FRAUD ALERT: Transfer {transfer.id} from {transfer.salesperson_name}")
        print(f"   Amount: ${transfer.amount_usd:,.2f}")
        print(f"   Reason: {transfer.fraud_alert_reason}")
        print(f"   Time: {transfer.created_at}")
        print("   ⚠️  IMMEDIATE ATTENTION REQUIRED ⚠️")


# ============================================================================
# Dependency for FastAPI
# ============================================================================

from app.db.database import get_db
from fastapi import Depends


def get_money_transfer_service(db: Session = Depends(get_db)) -> MoneyTransferService:
    """
    Dependency to get MoneyTransferService instance.

    Usage in routers:
        @router.post("/transfers")
        def create_transfer(
            service: MoneyTransferService = Depends(get_money_transfer_service)
        ):
            transfer = service.create_transfer(...)
            return transfer
    """
    return MoneyTransferService(db) 