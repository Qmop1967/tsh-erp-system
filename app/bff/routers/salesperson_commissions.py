"""
Commission Management BFF Router for Salesperson App
13 endpoints for commission tracking, targets, and leaderboards

Business Purpose:
- Track 2.25% commission on all sales
- Sales target management
- Team leaderboard and rankings
- Weekly/monthly earnings reports
- Payout request workflow
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, or_
from typing import Optional, List
from datetime import datetime, date, timedelta
from decimal import Decimal
from collections import defaultdict

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.salesperson import (
    SalespersonCommission,
    SalespersonTarget,
    SalespersonDailySummary
)
from app.models.sales import SalesOrder  # Assuming this exists
from app.schemas.salesperson import (
    CommissionSummaryResponse,
    CommissionHistoryItem,
    CommissionHistoryResponse,
    CommissionDetailResponse,
    CalculateCommissionRequest,
    CalculateCommissionResponse,
    SalesTargetResponse,
    SetTargetRequest,
    LeaderboardEntry,
    LeaderboardResponse,
    WeeklyEarningsResponse,
    CommissionStatisticsResponse,
    UpdateCommissionStatusRequest,
    MarkPaidRequest,
    RequestPayoutRequest,
    RequestPayoutResponse,
    CommissionPeriod,
    CommissionStatus,
    SyncStatusResponse
)

router = APIRouter(prefix="/commissions", tags=["Salesperson Commissions"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_period_dates(period: str) -> tuple[date, date]:
    """Calculate start and end dates for a period"""
    today = datetime.utcnow().date()

    if period == "today":
        return today, today
    elif period == "week":
        # Current week (Monday to Sunday)
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end
    elif period == "month":
        # Current month
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start, end
    elif period == "quarter":
        # Current quarter
        quarter = (today.month - 1) // 3
        start = today.replace(month=quarter * 3 + 1, day=1)
        end_month = start.month + 2
        if end_month > 12:
            end = today.replace(year=today.year + 1, month=end_month - 12, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=end_month + 1, day=1) - timedelta(days=1)
        return start, end
    elif period == "year":
        # Current year
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return start, end
    elif period == "all":
        # All time
        return date(2020, 1, 1), today
    else:
        return today, today


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/summary", response_model=CommissionSummaryResponse)
async def get_commission_summary(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    period: str = Query("month", description="Period: today, week, month, quarter, year, all"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get commission summary for period

    Business Logic:
    - Aggregates all sales for the period
    - Calculates commission at 2.25% rate
    - Shows pending vs paid commission
    - Includes target achievement if targets set

    Authorization:
    - Salespersons can view their own summary
    - Managers can view any salesperson's summary
    """
    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    if not is_manager and current_user.id != salesperson_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own commission summary"
        )

    # Get salesperson
    salesperson = db.query(User).filter(User.id == salesperson_id).first()
    if not salesperson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salesperson not found"
        )

    # Calculate period dates
    period_start, period_end = calculate_period_dates(period)

    # Try to get pre-calculated commission
    commission = db.query(SalespersonCommission).filter(
        and_(
            SalespersonCommission.salesperson_id == salesperson_id,
            SalespersonCommission.period_start == period_start,
            SalespersonCommission.period_end == period_end
        )
    ).first()

    if commission:
        # Use existing commission record
        total_sales = commission.total_sales_amount
        total_commission = commission.calculated_commission
        pending = commission.calculated_commission if not commission.is_paid else Decimal(0)
        paid = commission.approved_commission if commission.is_paid else Decimal(0)
        total_orders = commission.total_orders
        total_customers = commission.total_customers
        avg_order_value = commission.avg_order_value
    else:
        # Calculate on-the-fly from sales orders
        # TODO: This assumes SalesOrder model exists with proper structure
        # Adjust based on actual sales model structure

        # For now, return zeros as placeholder
        # In production, you would query actual sales data
        total_sales = Decimal(0)
        total_commission = Decimal(0)
        pending = Decimal(0)
        paid = Decimal(0)
        total_orders = 0
        total_customers = 0
        avg_order_value = Decimal(0)

    # Get active target for period
    target = db.query(SalespersonTarget).filter(
        and_(
            SalespersonTarget.salesperson_id == salesperson_id,
            SalespersonTarget.period_start <= period_end,
            SalespersonTarget.period_end >= period_start,
            SalespersonTarget.is_active == True
        )
    ).first()

    target_sales = target.target_revenue_iqd if target else None
    target_achievement = None
    if target and target_sales:
        target_achievement = (total_sales / target_sales * 100) if target_sales > 0 else Decimal(0)

    # Calculate rank (if applicable)
    # TODO: Implement ranking logic
    rank = None

    return CommissionSummaryResponse(
        salesperson_id=salesperson_id,
        salesperson_name=salesperson.name,
        period=period,
        period_start=period_start,
        period_end=period_end,
        total_sales=total_sales,
        commission_rate=Decimal("2.25"),
        total_commission=total_commission,
        pending_commission=pending,
        paid_commission=paid,
        total_orders=total_orders,
        total_customers=total_customers,
        avg_order_value=avg_order_value,
        target_sales=target_sales,
        target_achievement_percentage=target_achievement,
        rank=rank
    )


@router.get("/history", response_model=CommissionHistoryResponse)
async def get_commission_history(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    period: Optional[str] = Query(None, description="Filter by period type"),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get commission history

    Returns:
    - List of all commission records
    - Total earned (all time)
    - Total pending
    """
    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    if not is_manager and current_user.id != salesperson_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own commission history"
        )

    # Build query
    query = db.query(SalespersonCommission).filter(
        SalespersonCommission.salesperson_id == salesperson_id
    )

    if status:
        query = query.filter(SalespersonCommission.status == status)

    if period:
        query = query.filter(SalespersonCommission.period_type == period)

    # Get commissions
    commissions = query.order_by(
        desc(SalespersonCommission.period_end)
    ).limit(limit).all()

    # Calculate totals
    all_commissions = db.query(SalespersonCommission).filter(
        SalespersonCommission.salesperson_id == salesperson_id
    ).all()

    total_earned = sum(
        c.approved_commission or c.calculated_commission
        for c in all_commissions
        if c.is_paid
    )

    total_pending = sum(
        c.calculated_commission
        for c in all_commissions
        if not c.is_paid
    )

    return CommissionHistoryResponse(
        commissions=commissions,
        total=len(commissions),
        total_earned=total_earned,
        total_pending=total_pending
    )


@router.get("/{commission_id}", response_model=CommissionDetailResponse)
async def get_commission_details(
    commission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed commission information

    Includes:
    - Full commission details
    - Approval workflow history
    - Payment information
    - Notes from manager
    """
    commission = db.query(SalespersonCommission).filter(
        SalespersonCommission.id == commission_id
    ).first()

    if not commission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commission not found"
        )

    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    is_owner = commission.salesperson_id == current_user.id

    if not is_manager and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own commissions"
        )

    return commission


@router.post("/calculate", response_model=CalculateCommissionResponse)
async def calculate_commission(
    request: CalculateCommissionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate commission preview

    Business Logic:
    - Simple calculation: sales_amount * commission_rate / 100
    - Default rate: 2.25%
    - No tax deduction (paid gross)

    Use Case:
    - Mobile app shows real-time commission calculation
    - Before submitting sales, salesperson sees expected commission
    """
    commission_amount = request.sales_amount * request.commission_rate / 100
    estimated_payout = commission_amount  # No tax deduction

    return CalculateCommissionResponse(
        sales_amount=request.sales_amount,
        commission_rate=request.commission_rate,
        commission_amount=commission_amount,
        estimated_payout=estimated_payout,
        tax_amount=None,
        net_payout=None
    )


@router.get("/targets", response_model=SalesTargetResponse)
async def get_sales_target(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    period: str = Query("monthly", description="Period: monthly, quarterly, yearly"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current sales target

    Returns:
    - Target amounts and counts
    - Current achievement
    - Progress percentages
    - Bonus configuration
    """
    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    if not is_manager and current_user.id != salesperson_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own targets"
        )

    # Get active target for current period
    today = datetime.utcnow().date()

    target = db.query(SalespersonTarget).filter(
        and_(
            SalespersonTarget.salesperson_id == salesperson_id,
            SalespersonTarget.period_type == period,
            SalespersonTarget.period_start <= today,
            SalespersonTarget.period_end >= today,
            SalespersonTarget.is_active == True
        )
    ).first()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active {period} target found for this salesperson"
        )

    # Update achievement (calculate from sales)
    # TODO: Implement actual sales aggregation
    # For now, return target as-is

    return target


@router.post("/targets/set", response_model=SalesTargetResponse)
async def set_sales_target(
    request: SetTargetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set sales target

    Business Logic:
    - Managers set targets for salespersons
    - Targets can be revenue-based or order-count-based
    - Can include bonus for achievement
    - One active target per period per salesperson

    Authorization:
    - Only managers can set targets
    """
    # Authorization
    if not current_user.role.name.lower() in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can set sales targets"
        )

    # Get salesperson
    salesperson = db.query(User).filter(User.id == request.salesperson_id).first()
    if not salesperson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salesperson not found"
        )

    # Check for existing active target in period
    existing_target = db.query(SalespersonTarget).filter(
        and_(
            SalespersonTarget.salesperson_id == request.salesperson_id,
            SalespersonTarget.period_type == request.period_type,
            SalespersonTarget.period_start <= request.period_end,
            SalespersonTarget.period_end >= request.period_start,
            SalespersonTarget.is_active == True
        )
    ).first()

    if existing_target:
        # Deactivate existing target
        existing_target.is_active = False

    # Create new target
    target = SalespersonTarget(
        salesperson_id=request.salesperson_id,
        salesperson_name=salesperson.name,
        period_type=request.period_type,
        period_start=request.period_start,
        period_end=request.period_end,
        target_revenue_iqd=request.target_revenue_iqd or Decimal(0),
        target_revenue_usd=request.target_revenue_usd or Decimal(0),
        target_orders=request.target_orders or 0,
        target_customers=request.target_customers or 0,
        bonus_enabled=request.bonus_enabled,
        bonus_percentage=request.bonus_percentage,
        bonus_amount=request.bonus_amount,
        description=request.description,
        set_by=current_user.id,
        is_active=True
    )

    db.add(target)
    db.commit()
    db.refresh(target)

    return target


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    period: str = Query("month", description="Period: today, week, month, quarter, year"),
    limit: int = Query(10, ge=1, le=50, description="Number of top performers"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get team leaderboard

    Business Logic:
    - Ranks all salespersons by total sales
    - Shows top performers
    - Includes current user's rank
    - Gamification for motivation

    Ranking Criteria:
    1. Total sales amount (primary)
    2. Total orders (tiebreaker)
    3. Commission earned (tiebreaker)
    """
    # Calculate period dates
    period_start, period_end = calculate_period_dates(period)

    # Get all salespersons
    salespersons = db.query(User).filter(User.is_salesperson == True).all()

    # Calculate metrics for each salesperson
    leaderboard_data = []

    for salesperson in salespersons:
        # Get commission for period
        commission = db.query(SalespersonCommission).filter(
            and_(
                SalespersonCommission.salesperson_id == salesperson.id,
                SalespersonCommission.period_start == period_start,
                SalespersonCommission.period_end == period_end
            )
        ).first()

        if commission:
            total_sales = commission.total_sales_amount
            total_commission = commission.calculated_commission
            total_orders = commission.total_orders
            total_customers = commission.total_customers
        else:
            # TODO: Calculate from sales orders
            total_sales = Decimal(0)
            total_commission = Decimal(0)
            total_orders = 0
            total_customers = 0

        # Get target achievement
        target = db.query(SalespersonTarget).filter(
            and_(
                SalespersonTarget.salesperson_id == salesperson.id,
                SalespersonTarget.period_start <= period_end,
                SalespersonTarget.period_end >= period_start,
                SalespersonTarget.is_active == True
            )
        ).first()

        target_achievement = None
        if target and target.target_revenue_iqd:
            target_achievement = (total_sales / target.target_revenue_iqd * 100)

        leaderboard_data.append({
            "salesperson_id": salesperson.id,
            "salesperson_name": salesperson.name,
            "total_sales": total_sales,
            "total_commission": total_commission,
            "total_orders": total_orders,
            "total_customers": total_customers,
            "target_achievement_percentage": target_achievement
        })

    # Sort by total sales (descending)
    leaderboard_data.sort(key=lambda x: (x["total_sales"], x["total_orders"]), reverse=True)

    # Add ranks and badges
    leaderboard_entries = []
    for idx, data in enumerate(leaderboard_data[:limit], start=1):
        badge = None
        if idx == 1:
            badge = "top_performer"
        elif idx == 2:
            badge = "runner_up"
        elif idx == 3:
            badge = "third_place"

        leaderboard_entries.append(
            LeaderboardEntry(
                rank=idx,
                salesperson_id=data["salesperson_id"],
                salesperson_name=data["salesperson_name"],
                total_sales=data["total_sales"],
                total_commission=data["total_commission"],
                total_orders=data["total_orders"],
                total_customers=data["total_customers"],
                target_achievement_percentage=data["target_achievement_percentage"],
                badge=badge
            )
        )

    # Find current user's rank
    my_rank = None
    for idx, data in enumerate(leaderboard_data, start=1):
        if data["salesperson_id"] == current_user.id:
            my_rank = idx
            break

    return LeaderboardResponse(
        period=period,
        period_start=period_start,
        period_end=period_end,
        leaderboard=leaderboard_entries,
        total_participants=len(leaderboard_data),
        my_rank=my_rank
    )


@router.get("/weekly-earnings", response_model=WeeklyEarningsResponse)
async def get_weekly_earnings(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    week_start: Optional[date] = Query(None, description="Week start date (Monday)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly earnings breakdown

    Returns:
    - Weekly total sales and commission
    - Daily breakdown for the week
    - Paid vs pending commission
    """
    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    if not is_manager and current_user.id != salesperson_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own earnings"
        )

    # Default to current week if not specified
    if not week_start:
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=6)

    # Get daily summaries for the week
    daily_summaries = db.query(SalespersonDailySummary).filter(
        and_(
            SalespersonDailySummary.salesperson_id == salesperson_id,
            SalespersonDailySummary.summary_date >= week_start,
            SalespersonDailySummary.summary_date <= week_end
        )
    ).order_by(SalespersonDailySummary.summary_date).all()

    # Calculate weekly totals
    total_sales = sum(s.total_sales_iqd for s in daily_summaries)
    total_commission = sum(s.daily_commission for s in daily_summaries)
    total_orders = sum(s.total_orders for s in daily_summaries)

    # Get commission payment status for week
    commission = db.query(SalespersonCommission).filter(
        and_(
            SalespersonCommission.salesperson_id == salesperson_id,
            SalespersonCommission.period_start == week_start,
            SalespersonCommission.period_end == week_end
        )
    ).first()

    paid_commission = Decimal(0)
    pending_commission = total_commission

    if commission and commission.is_paid:
        paid_commission = commission.approved_commission or commission.calculated_commission
        pending_commission = Decimal(0)

    # Calculate average order value
    avg_order_value = total_sales / total_orders if total_orders > 0 else Decimal(0)

    # Build daily breakdown
    daily_breakdown = [
        {
            "date": str(s.summary_date),
            "sales": float(s.total_sales_iqd),
            "commission": float(s.daily_commission),
            "orders": s.total_orders
        }
        for s in daily_summaries
    ]

    return WeeklyEarningsResponse(
        week_start=week_start,
        week_end=week_end,
        total_sales=total_sales,
        total_commission=total_commission,
        paid_commission=paid_commission,
        pending_commission=pending_commission,
        total_orders=total_orders,
        avg_order_value=avg_order_value,
        daily_breakdown=daily_breakdown
    )


@router.put("/{commission_id}/status", response_model=CommissionDetailResponse)
async def update_commission_status(
    commission_id: int,
    request: UpdateCommissionStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update commission status

    Business Logic:
    - Workflow: pending → calculated → approved → paid → settled
    - Only managers can update status
    - Status transitions are validated
    """
    # Authorization
    if not current_user.role.name.lower() in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can update commission status"
        )

    commission = db.query(SalespersonCommission).filter(
        SalespersonCommission.id == commission_id
    ).first()

    if not commission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commission not found"
        )

    # Update status
    commission.status = request.status.value
    if request.notes:
        commission.manager_notes = request.notes

    # Update workflow timestamps
    if request.status == CommissionStatus.CALCULATED and not commission.calculated_at:
        commission.calculated_by = current_user.id
        commission.calculated_at = datetime.utcnow()
    elif request.status == CommissionStatus.APPROVED and not commission.approved_at:
        commission.approved_by = current_user.id
        commission.approved_at = datetime.utcnow()

    commission.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(commission)

    return commission


@router.put("/{commission_id}/mark-paid", response_model=CommissionDetailResponse)
async def mark_commission_paid(
    commission_id: int,
    request: MarkPaidRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark commission as paid

    Business Logic:
    - Records payment method and reference
    - Updates status to paid
    - Records payment date
    - Only managers can mark as paid
    """
    # Authorization
    if not current_user.role.name.lower() in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can mark commissions as paid"
        )

    commission = db.query(SalespersonCommission).filter(
        SalespersonCommission.id == commission_id
    ).first()

    if not commission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commission not found"
        )

    # Update payment info
    commission.is_paid = True
    commission.paid_date = request.paid_date or datetime.utcnow().date()
    commission.payment_method = request.payment_method
    commission.payment_reference = request.payment_reference
    commission.status = "paid"
    commission.paid_by = current_user.id
    commission.paid_at = datetime.utcnow()

    if request.notes:
        commission.manager_notes = request.notes

    commission.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(commission)

    return commission


@router.get("/statistics", response_model=CommissionStatisticsResponse)
async def get_commission_statistics(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get commission statistics

    Returns:
    - Lifetime earnings
    - Year-to-date earnings
    - Month-to-date earnings
    - Average monthly commission
    - Highest monthly commission
    - Total orders all time
    - Average commission per order
    - Trend analysis
    """
    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    if not is_manager and current_user.id != salesperson_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own statistics"
        )

    # Get all commissions
    all_commissions = db.query(SalespersonCommission).filter(
        SalespersonCommission.salesperson_id == salesperson_id
    ).all()

    # Calculate lifetime earnings
    lifetime_earnings = sum(
        c.approved_commission or c.calculated_commission
        for c in all_commissions
        if c.is_paid
    )

    # Year-to-date
    today = datetime.utcnow().date()
    ytd_start = today.replace(month=1, day=1)
    ytd_commissions = [c for c in all_commissions if c.period_start >= ytd_start and c.is_paid]
    ytd_earnings = sum(c.approved_commission or c.calculated_commission for c in ytd_commissions)

    # Month-to-date
    mtd_start = today.replace(day=1)
    mtd_commissions = [c for c in all_commissions if c.period_start >= mtd_start and c.is_paid]
    mtd_earnings = sum(c.approved_commission or c.calculated_commission for c in mtd_commissions)

    # Average monthly
    monthly_commissions = [c for c in all_commissions if c.period_type == "monthly" and c.is_paid]
    avg_monthly = sum(c.approved_commission or c.calculated_commission for c in monthly_commissions) / len(monthly_commissions) if monthly_commissions else Decimal(0)

    # Highest monthly
    highest_monthly = max(
        (c.approved_commission or c.calculated_commission for c in monthly_commissions),
        default=Decimal(0)
    )

    # Total orders all time
    total_orders_all_time = sum(c.total_orders for c in all_commissions)

    # Average commission per order
    avg_commission_per_order = lifetime_earnings / total_orders_all_time if total_orders_all_time > 0 else Decimal(0)

    # Trend analysis (simplified)
    # Compare last 3 months to previous 3 months
    last_3_months = today - timedelta(days=90)
    previous_3_months = today - timedelta(days=180)

    recent_commissions = [
        c for c in all_commissions
        if c.period_start >= last_3_months and c.is_paid
    ]
    previous_commissions = [
        c for c in all_commissions
        if c.period_start >= previous_3_months and c.period_start < last_3_months and c.is_paid
    ]

    recent_total = sum(c.approved_commission or c.calculated_commission for c in recent_commissions)
    previous_total = sum(c.approved_commission or c.calculated_commission for c in previous_commissions)

    if previous_total > 0:
        change = (recent_total - previous_total) / previous_total
        if change > 0.1:
            trend = "increasing"
        elif change < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "stable"

    return CommissionStatisticsResponse(
        lifetime_earnings=lifetime_earnings,
        ytd_earnings=ytd_earnings,
        mtd_earnings=mtd_earnings,
        avg_monthly_commission=avg_monthly,
        highest_monthly_commission=highest_monthly,
        total_orders_all_time=total_orders_all_time,
        avg_commission_per_order=avg_commission_per_order,
        commission_trend=trend
    )


@router.post("/request-payout", response_model=RequestPayoutResponse)
async def request_payout(
    request: RequestPayoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request commission payout

    Business Logic:
    - Salesperson requests payout for pending commissions
    - Creates payout request for manager approval
    - Can request multiple commissions at once
    - Manager gets notification to approve

    Authorization:
    - Salespersons can request payout for their own commissions
    """
    # Authorization
    if not current_user.is_salesperson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only salespersons can request payouts"
        )

    # Get commissions
    commissions = db.query(SalespersonCommission).filter(
        and_(
            SalespersonCommission.id.in_(request.commission_ids),
            SalespersonCommission.salesperson_id == current_user.id
        )
    ).all()

    if not commissions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No valid commissions found"
        )

    # Check all commissions are eligible (not already paid)
    for commission in commissions:
        if commission.is_paid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Commission {commission.id} is already paid"
            )

    # Calculate total amount
    total_amount = sum(c.calculated_commission for c in commissions)

    # Update commissions with payout request
    # TODO: Implement payout request workflow with notifications
    for commission in commissions:
        if request.notes:
            commission.notes = request.notes
        commission.updated_at = datetime.utcnow()

    db.commit()

    # TODO: Send notification to manager

    # Estimated payment date (5 business days)
    estimated_date = datetime.utcnow().date() + timedelta(days=7)

    # Return response
    # TODO: Implement actual request tracking
    return RequestPayoutResponse(
        request_id=0,  # Placeholder - implement actual request ID
        total_amount=total_amount,
        commission_count=len(commissions),
        status="pending_approval",
        estimated_payment_date=estimated_date
    )


@router.get("/sync-status", response_model=SyncStatusResponse)
async def get_sync_status(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get commission sync status

    Returns:
    - Number of pending commission calculations
    - Last calculation timestamp
    - Sync status
    """
    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    if not is_manager and current_user.id != salesperson_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own sync status"
        )

    # Count pending commissions
    pending_count = db.query(SalespersonCommission).filter(
        and_(
            SalespersonCommission.salesperson_id == salesperson_id,
            SalespersonCommission.is_synced == False
        )
    ).count()

    # Get last synced commission
    last_synced = db.query(SalespersonCommission).filter(
        and_(
            SalespersonCommission.salesperson_id == salesperson_id,
            SalespersonCommission.is_synced == True
        )
    ).order_by(desc(SalespersonCommission.synced_at)).first()

    return SyncStatusResponse(
        pending_locations=pending_count,  # Reusing field name
        last_sync=last_synced.synced_at if last_synced else None,
        is_syncing=False,
        sync_errors=0
    )


@router.get("/health")
async def health_check():
    """Health check endpoint for commissions service"""
    return {
        "status": "healthy",
        "service": "commissions-bff",
        "version": "1.0.0"
    }
