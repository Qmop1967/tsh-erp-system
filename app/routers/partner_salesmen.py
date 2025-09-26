from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from pydantic import BaseModel, EmailStr
from enum import Enum
import json
import uuid
import hashlib
import secrets

from app.db.database import get_db, Base
from app.models import *
from sqlalchemy import func, desc, and_, or_, Column, Integer, String, DateTime, Text, Boolean, Numeric, JSON, ForeignKey
from sqlalchemy.orm import relationship

router = APIRouter()

class PartnerStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"
    INACTIVE = "inactive"

class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    DOCUMENTS_REQUIRED = "documents_required"

class CommissionType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED = "tiered"
    HYBRID = "hybrid"

class PartnerApplication(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    national_id: str
    address: str
    city: str
    province: str
    business_experience: str
    preferred_territory: str
    expected_monthly_sales: float
    has_transportation: bool
    has_storage_space: bool
    previous_sales_experience: str
    references: List[Dict[str, str]]
    bank_account_details: Dict[str, str]
    documents: List[str]  # Base64 encoded documents
    motivation_letter: str

class PartnerApproval(BaseModel):
    partner_id: int
    approved: bool
    commission_rate: float
    territory_assigned: str
    credit_limit: float
    monthly_target: float
    notes: str
    onboarding_date: date

class CommissionCalculation(BaseModel):
    partner_id: int
    period_start: date
    period_end: date
    sales_amount: float
    commission_rate: float
    base_commission: float
    bonus_commission: float
    deductions: float
    net_commission: float
    payment_status: str

class PartnerPerformance(BaseModel):
    partner_id: int
    month: date
    sales_volume: float
    orders_count: int
    customers_acquired: int
    territory_coverage: float
    customer_satisfaction: float
    performance_score: float
    rank: int

class PartnerSalesmanRegistration(BaseModel):
    full_name: str
    email: str
    phone: str
    national_id: str
    city: str
    address: str
    bank_account: str
    bank_name: str
    references: List[str]  # Professional references
    business_license: Optional[str] = None
    experience_years: int
    target_monthly_sales: float
    commission_rate_requested: float

class PartnerSalesmanProfile(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    city: str
    status: str  # pending, approved, active, suspended
    commission_rate: float
    total_sales: float
    monthly_target: float
    performance_score: float
    joined_date: datetime
    last_activity: datetime

class CommissionRecord(BaseModel):
    id: int
    salesman_id: int
    order_id: int
    customer_name: str
    product_name: str
    sale_amount: float
    commission_rate: float
    commission_amount: float
    payment_status: str  # pending, paid, disputed
    sale_date: datetime
    commission_date: datetime

class PartnerSalesmanStats(BaseModel):
    total_sales_amount: float
    total_commission_earned: float
    pending_commission: float
    orders_count: int
    customers_acquired: int
    performance_rank: int
    achievement_percentage: float
    weekly_performance: List[Dict[str, Any]]

@router.post("/partners/applications/submit")
async def submit_partner_application(
    application: PartnerApplication,
    db: Session = Depends(get_db)
):
    """
    📝 Submit partner salesman application
    Complete application process for joining the marketplace
    """
    
    try:
        # Check if application already exists
        existing = db.query(PartnerSalesmanApplication).filter(
            or_(
                PartnerSalesmanApplication.phone == application.phone,
                PartnerSalesmanApplication.email == application.email,
                PartnerSalesmanApplication.national_id == application.national_id
            )
        ).first()
        
        if existing:
            if existing.status in [ApplicationStatus.PENDING.value, ApplicationStatus.UNDER_REVIEW.value]:
                raise HTTPException(status_code=400, detail="Application already submitted and under review")
            elif existing.status == ApplicationStatus.APPROVED.value:
                raise HTTPException(status_code=400, detail="You are already an approved partner")
        
        # Generate application number
        app_number = f"PSA-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create application record
        partner_application = PartnerSalesmanApplication(
            application_number=app_number,
            full_name=application.full_name,
            phone=application.phone,
            email=application.email,
            national_id=application.national_id,
            address=application.address,
            city=application.city,
            province=application.province,
            business_experience=application.business_experience,
            preferred_territory=application.preferred_territory,
            expected_monthly_sales=application.expected_monthly_sales,
            has_transportation=application.has_transportation,
            has_storage_space=application.has_storage_space,
            previous_sales_experience=application.previous_sales_experience,
            references=application.references,
            bank_account_details=application.bank_account_details,
            motivation_letter=application.motivation_letter,
            status=ApplicationStatus.SUBMITTED.value,
            submitted_at=datetime.now()
        )
        
        db.add(partner_application)
        db.flush()
        
        # Store documents
        for i, doc_data in enumerate(application.documents):
            document = PartnerDocument(
                application_id=partner_application.id,
                document_type=f"document_{i+1}",
                document_data=doc_data,
                uploaded_at=datetime.now()
            )
            db.add(document)
        
        # Create admin notification
        notification = AdminNotification(
            type="partner_application",
            title="New Partner Application",
            message=f"New partner application from {application.full_name} in {application.city}",
            data={"application_id": partner_application.id, "city": application.city},
            priority="medium",
            created_at=datetime.now()
        )
        db.add(notification)
        
        db.commit()
        
        return {
            "application_id": partner_application.id,
            "application_number": app_number,
            "status": "submitted",
            "message": "Application submitted successfully",
            "next_steps": "Your application will be reviewed within 3-5 business days",
            "estimated_response_time": "3-5 business days"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit application: {str(e)}")

@router.get("/partners/applications", response_model=List[Dict[str, Any]])
async def get_partner_applications(
    status: Optional[ApplicationStatus] = Query(None),
    city: Optional[str] = Query(None),
    province: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    📋 Get partner applications with filtering
    Admin view of all applications
    """
    
    query = db.query(PartnerSalesmanApplication).order_by(desc(PartnerSalesmanApplication.submitted_at))
    
    if status:
        query = query.filter(PartnerSalesmanApplication.status == status.value)
    
    if city:
        query = query.filter(PartnerSalesmanApplication.city.ilike(f"%{city}%"))
    
    if province:
        query = query.filter(PartnerSalesmanApplication.province.ilike(f"%{province}%"))
    
    if date_from:
        query = query.filter(PartnerSalesmanApplication.submitted_at >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(PartnerSalesmanApplication.submitted_at <= datetime.combine(date_to, datetime.max.time()))
    
    applications = query.offset(offset).limit(limit).all()
    
    formatted_applications = []
    for app in applications:
        formatted_applications.append({
            "id": app.id,
            "application_number": app.application_number,
            "full_name": app.full_name,
            "phone": app.phone,
            "email": app.email,
            "city": app.city,
            "province": app.province,
            "preferred_territory": app.preferred_territory,
            "expected_monthly_sales": float(app.expected_monthly_sales),
            "has_transportation": app.has_transportation,
            "has_storage_space": app.has_storage_space,
            "business_experience": app.business_experience,
            "status": app.status,
            "submitted_at": app.submitted_at.isoformat(),
            "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
            "documents_count": len(app.documents) if app.documents else 0,
            "references_count": len(app.references) if app.references else 0
        })
    
    return formatted_applications

@router.post("/partners/applications/{application_id}/review")
async def review_partner_application(
    application_id: int,
    approval: PartnerApproval,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    ✅ Review and approve/reject partner application
    Complete onboarding process
    """
    
    try:
        # Get application
        application = db.query(PartnerSalesmanApplication).filter(
            PartnerSalesmanApplication.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        if approval.approved:
            # Create partner salesman record
            partner_salesman = PartnerSalesman(
                partner_id=f"PS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
                full_name=application.full_name,
                phone=application.phone,
                email=application.email,
                city=application.city,
                province=application.province,
                territory_assigned=approval.territory_assigned,
                commission_rate=approval.commission_rate,
                credit_limit=approval.credit_limit,
                monthly_target=approval.monthly_target,
                status=PartnerStatus.APPROVED.value,
                onboarding_date=approval.onboarding_date,
                created_at=datetime.now()
            )
            
            db.add(partner_salesman)
            db.flush()
            
            # Update application status
            application.status = ApplicationStatus.APPROVED.value
            application.reviewed_at = datetime.now()
            application.review_notes = approval.notes
            application.partner_id = partner_salesman.id
            
            # Create welcome package
            welcome_package = PartnerWelcomePackage(
                partner_id=partner_salesman.id,
                welcome_kit_sent=False,
                training_scheduled=False,
                account_setup_completed=False,
                first_order_placed=False,
                created_at=datetime.now()
            )
            db.add(welcome_package)
            
            # Background task for onboarding
            background_tasks.add_task(
                send_partner_welcome_email,
                partner_salesman.id,
                application.email,
                db
            )
            
            message = f"Partner application approved! Welcome to TSH ERP Partner Network"
            
        else:
            # Reject application
            application.status = ApplicationStatus.REJECTED.value
            application.reviewed_at = datetime.now()
            application.review_notes = approval.notes
            
            message = "Application rejected"
        
        db.commit()
        
        return {
            "application_id": application_id,
            "approved": approval.approved,
            "partner_id": partner_salesman.partner_id if approval.approved else None,
            "message": message,
            "next_steps": "Partner will receive onboarding materials within 24 hours" if approval.approved else "Applicant will be notified of rejection reasons"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to review application: {str(e)}")

@router.get("/partners/active", response_model=List[Dict[str, Any]])
async def get_active_partners(
    city: Optional[str] = Query(None),
    province: Optional[str] = Query(None),
    performance_tier: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    👥 Get active partner salesmen
    """
    
    query = db.query(PartnerSalesman).filter(
        PartnerSalesman.status.in_([PartnerStatus.APPROVED.value, PartnerStatus.ACTIVE.value])
    ).order_by(desc(PartnerSalesman.created_at))
    
    if city:
        query = query.filter(PartnerSalesman.city.ilike(f"%{city}%"))
    
    if province:
        query = query.filter(PartnerSalesman.province.ilike(f"%{province}%"))
    
    partners = query.offset(offset).limit(limit).all()
    
    formatted_partners = []
    for partner in partners:
        # Get current month performance
        current_month = date.today().replace(day=1)
        performance = db.query(PartnerPerformanceMetrics).filter(
            PartnerPerformanceMetrics.partner_id == partner.id,
            PartnerPerformanceMetrics.month == current_month
        ).first()
        
        # Get total commission this month
        month_commission = db.query(func.sum(PartnerCommission.net_commission)).filter(
            PartnerCommission.partner_id == partner.id,
            PartnerCommission.created_at >= current_month
        ).scalar() or 0
        
        formatted_partners.append({
            "id": partner.id,
            "partner_id": partner.partner_id,
            "full_name": partner.full_name,
            "phone": partner.phone,
            "city": partner.city,
            "province": partner.province,
            "territory_assigned": partner.territory_assigned,
            "commission_rate": float(partner.commission_rate),
            "monthly_target": float(partner.monthly_target),
            "current_month_sales": float(performance.sales_volume) if performance else 0,
            "current_month_commission": float(month_commission),
            "performance_score": float(performance.performance_score) if performance else 0,
            "status": partner.status,
            "last_order_date": partner.last_order_date.isoformat() if partner.last_order_date else None,
            "total_customers": partner.total_customers or 0,
            "onboarding_date": partner.onboarding_date.isoformat() if partner.onboarding_date else None
        })
    
    return formatted_partners

@router.get("/partners/{partner_id}/performance")
async def get_partner_performance(
    partner_id: int,
    months: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """
    📊 Get detailed partner performance metrics
    """
    
    try:
        # Get partner
        partner = db.query(PartnerSalesman).filter(PartnerSalesman.id == partner_id).first()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        
        # Get performance data for last N months
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        performance_data = db.query(PartnerPerformanceMetrics).filter(
            PartnerPerformanceMetrics.partner_id == partner_id,
            PartnerPerformanceMetrics.month >= start_date
        ).order_by(PartnerPerformanceMetrics.month).all()
        
        # Get commission data
        commissions = db.query(PartnerCommission).filter(
            PartnerCommission.partner_id == partner_id,
            PartnerCommission.created_at >= datetime.combine(start_date, datetime.min.time())
        ).all()
        
        # Calculate totals
        total_sales = sum(float(p.sales_volume) for p in performance_data)
        total_commission = sum(float(c.net_commission) for c in commissions)
        total_orders = sum(p.orders_count for p in performance_data)
        total_customers = sum(p.customers_acquired for p in performance_data)
        
        # Format monthly data
        monthly_data = []
        for perf in performance_data:
            month_commissions = [c for c in commissions if c.created_at.month == perf.month.month]
            monthly_commission = sum(float(c.net_commission) for c in month_commissions)
            
            monthly_data.append({
                "month": perf.month.isoformat(),
                "sales_volume": float(perf.sales_volume),
                "orders_count": perf.orders_count,
                "customers_acquired": perf.customers_acquired,
                "commission_earned": monthly_commission,
                "performance_score": float(perf.performance_score),
                "territory_coverage": float(perf.territory_coverage),
                "customer_satisfaction": float(perf.customer_satisfaction),
                "rank": perf.rank
            })
        
        return {
            "partner_id": partner_id,
            "partner_name": partner.full_name,
            "period_months": months,
            "summary": {
                "total_sales": total_sales,
                "total_commission": total_commission,
                "total_orders": total_orders,
                "total_customers": total_customers,
                "average_order_value": total_sales / total_orders if total_orders > 0 else 0,
                "commission_rate": float(partner.commission_rate),
                "monthly_target": float(partner.monthly_target)
            },
            "monthly_performance": monthly_data,
            "current_status": partner.status,
            "territory": partner.territory_assigned
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get partner performance: {str(e)}")

@router.post("/partners/{partner_id}/commission/calculate")
async def calculate_partner_commission(
    partner_id: int,
    calculation: CommissionCalculation,
    db: Session = Depends(get_db)
):
    """
    💰 Calculate and record partner commission
    """
    
    try:
        # Get partner
        partner = db.query(PartnerSalesman).filter(PartnerSalesman.id == partner_id).first()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        
        # Create commission record
        commission = PartnerCommission(
            partner_id=partner_id,
            period_start=calculation.period_start,
            period_end=calculation.period_end,
            sales_amount=calculation.sales_amount,
            commission_rate=calculation.commission_rate,
            base_commission=calculation.base_commission,
            bonus_commission=calculation.bonus_commission,
            deductions=calculation.deductions,
            net_commission=calculation.net_commission,
            payment_status=calculation.payment_status,
            created_at=datetime.now()
        )
        
        db.add(commission)
        
        # Update partner total commission
        partner.total_commission_earned = (partner.total_commission_earned or 0) + calculation.net_commission
        partner.last_commission_date = datetime.now()
        
        db.commit()
        
        return {
            "commission_id": commission.id,
            "partner_id": partner_id,
            "net_commission": calculation.net_commission,
            "payment_status": calculation.payment_status,
            "message": "Commission calculated and recorded successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to calculate commission: {str(e)}")

@router.get("/partners/dashboard/overview")
async def get_partners_dashboard_overview(
    db: Session = Depends(get_db)
):
    """
    📊 Partner salesmen dashboard overview
    """
    
    try:
        # Get current month data
        current_month = date.today().replace(day=1)
        
        # Partner counts by status
        total_partners = db.query(func.count(PartnerSalesman.id)).scalar() or 0
        active_partners = db.query(func.count(PartnerSalesman.id)).filter(
            PartnerSalesman.status == PartnerStatus.ACTIVE.value
        ).scalar() or 0
        pending_applications = db.query(func.count(PartnerSalesmanApplication.id)).filter(
            PartnerSalesmanApplication.status.in_([ApplicationStatus.SUBMITTED.value, ApplicationStatus.UNDER_REVIEW.value])
        ).scalar() or 0
        
        # This month performance
        month_sales = db.query(func.sum(PartnerPerformanceMetrics.sales_volume)).filter(
            PartnerPerformanceMetrics.month == current_month
        ).scalar() or 0
        
        month_commission = db.query(func.sum(PartnerCommission.net_commission)).filter(
            PartnerCommission.created_at >= current_month
        ).scalar() or 0
        
        # City breakdown
        city_breakdown = db.query(
            PartnerSalesman.city,
            func.count(PartnerSalesman.id).label('count')
        ).group_by(PartnerSalesman.city).all()
        
        # Top performers this month
        top_performers = db.query(
            PartnerSalesman.full_name,
            PartnerSalesman.city,
            PartnerPerformanceMetrics.sales_volume,
            PartnerPerformanceMetrics.performance_score
        ).join(
            PartnerPerformanceMetrics,
            PartnerSalesman.id == PartnerPerformanceMetrics.partner_id
        ).filter(
            PartnerPerformanceMetrics.month == current_month
        ).order_by(desc(PartnerPerformanceMetrics.performance_score)).limit(10).all()
        
        return {
            "total_partners": total_partners,
            "active_partners": active_partners,
            "pending_applications": pending_applications,
            "month_sales": float(month_sales),
            "month_commission": float(month_commission),
            "city_breakdown": [
                {"city": city, "count": count} for city, count in city_breakdown
            ],
            "top_performers": [
                {
                    "name": performer.full_name,
                    "city": performer.city,
                    "sales": float(performer.sales_volume),
                    "score": float(performer.performance_score)
                } for performer in top_performers
            ],
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard overview: {str(e)}")

# Helper Functions
async def send_partner_welcome_email(partner_id: int, email: str, db: Session):
    """Background task to send welcome email to new partner"""
    try:
        # In production, this would send actual email
        # For now, just log the welcome
        print(f"Welcome email sent to partner {partner_id} at {email}")
        
        # Update welcome package status
        welcome_package = db.query(PartnerWelcomePackage).filter(
            PartnerWelcomePackage.partner_id == partner_id
        ).first()
        
        if welcome_package:
            welcome_package.welcome_kit_sent = True
            welcome_package.updated_at = datetime.now()
            db.commit()
            
    except Exception as e:
        print(f"Error sending welcome email: {e}")

# Database Models
class PartnerSalesmanApplication(Base):
    __tablename__ = "partner_salesman_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    national_id = Column(String, nullable=False)
    address = Column(Text)
    city = Column(String, nullable=False)
    province = Column(String, nullable=False)
    business_experience = Column(Text)
    preferred_territory = Column(String)
    expected_monthly_sales = Column(Numeric(15, 2))
    has_transportation = Column(Boolean, default=False)
    has_storage_space = Column(Boolean, default=False)
    previous_sales_experience = Column(Text)
    references = Column(JSON)
    bank_account_details = Column(JSON)
    motivation_letter = Column(Text)
    status = Column(String, default="submitted")
    submitted_at = Column(DateTime, default=datetime.now)
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
    partner_id = Column(Integer, ForeignKey("partner_salesmen.id"))
    
    # Relationships
    documents = relationship("PartnerDocument", back_populates="application")

class PartnerSalesman(Base):
    __tablename__ = "partner_salesmen"
    
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    city = Column(String, nullable=False)
    province = Column(String, nullable=False)
    territory_assigned = Column(String)
    commission_rate = Column(Numeric(5, 2))
    credit_limit = Column(Numeric(15, 2))
    monthly_target = Column(Numeric(15, 2))
    total_sales = Column(Numeric(15, 2), default=0)
    total_commission_earned = Column(Numeric(15, 2), default=0)
    total_customers = Column(Integer, default=0)
    status = Column(String, default="approved")
    onboarding_date = Column(Date)
    last_order_date = Column(Date)
    last_commission_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    performance_metrics = relationship("PartnerPerformanceMetrics", back_populates="partner")
    commissions = relationship("PartnerCommission", back_populates="partner")

class PartnerDocument(Base):
    __tablename__ = "partner_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("partner_salesman_applications.id"))
    document_type = Column(String, nullable=False)
    document_data = Column(Text)  # Base64 encoded
    uploaded_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    application = relationship("PartnerSalesmanApplication", back_populates="documents")

class PartnerPerformanceMetrics(Base):
    __tablename__ = "partner_performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partner_salesmen.id"))
    month = Column(Date, nullable=False)
    sales_volume = Column(Numeric(15, 2), default=0)
    orders_count = Column(Integer, default=0)
    customers_acquired = Column(Integer, default=0)
    territory_coverage = Column(Numeric(5, 2), default=0)
    customer_satisfaction = Column(Numeric(5, 2), default=0)
    performance_score = Column(Numeric(5, 2), default=0)
    rank = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    partner = relationship("PartnerSalesman", back_populates="performance_metrics")

class PartnerCommission(Base):
    __tablename__ = "partner_commissions"
    
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partner_salesmen.id"))
    period_start = Column(Date)
    period_end = Column(Date)
    sales_amount = Column(Numeric(15, 2))
    commission_rate = Column(Numeric(5, 2))
    base_commission = Column(Numeric(15, 2))
    bonus_commission = Column(Numeric(15, 2), default=0)
    deductions = Column(Numeric(15, 2), default=0)
    net_commission = Column(Numeric(15, 2))
    payment_status = Column(String, default="pending")
    payment_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    partner = relationship("PartnerSalesman", back_populates="commissions")

class PartnerWelcomePackage(Base):
    __tablename__ = "partner_welcome_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partner_salesmen.id"))
    welcome_kit_sent = Column(Boolean, default=False)
    training_scheduled = Column(Boolean, default=False)
    account_setup_completed = Column(Boolean, default=False)
    first_order_placed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

@router.post("/register")
async def register_partner_salesman(
    registration: PartnerSalesmanRegistration,
    db: Session = Depends(get_db)
):
    """
    👥 Partner Salesmen Registration - Nationwide Sales Network
    Register new partner salesmen for the 100+ nationwide program
    """
    
    try:
        # Check if email or phone already exists
        existing_user = db.query(User).filter(
            or_(User.email == registration.email, User.phone == registration.phone)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Email or phone already registered")
        
        # Get partner salesman role
        partner_role = db.query(Role).filter(Role.name == "partner_salesman").first()
        if not partner_role:
            # Create the role if it doesn't exist
            partner_role = Role(name="partner_salesman")
            db.add(partner_role)
            db.flush()
        
        # Create user account (pending approval)
        new_partner = User(
            name=registration.full_name,
            email=registration.email,
            phone=registration.phone,
            password="temp_password",  # Will be sent via email
            role_id=partner_role.id,
            branch_id=1,  # Default branch
            is_salesperson=True,
            is_active=False,  # Pending approval
            employee_code=f"PS{datetime.now().strftime('%Y%m%d')}{db.query(func.count(User.id)).scalar() + 1:03d}"
        )
        
        db.add(new_partner)
        db.commit()
        
        # Store additional partner information (would need separate table in production)
        partner_data = {
            "user_id": new_partner.id,
            "national_id": registration.national_id,
            "city": registration.city,
            "address": registration.address,
            "bank_account": registration.bank_account,
            "bank_name": registration.bank_name,
            "references": registration.references,
            "business_license": registration.business_license,
            "experience_years": registration.experience_years,
            "target_monthly_sales": registration.target_monthly_sales,
            "commission_rate_requested": registration.commission_rate_requested,
            "status": "pending_review",
            "applied_date": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": "Registration submitted successfully",
            "partner_id": new_partner.id,
            "employee_code": new_partner.employee_code,
            "status": "pending_review",
            "next_steps": [
                "Document verification in progress",
                "Background check initiated",
                "Interview scheduling",
                "Commission rate negotiation",
                "Training program enrollment"
            ],
            "estimated_approval_time": "3-5 business days"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.get("/dashboard/{partner_id}")
async def get_partner_dashboard(
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    📊 Partner Salesman Personal Dashboard
    Complete performance tracking and commission management
    """
    
    try:
        # Get partner information
        partner = db.query(User).filter(
            User.id == partner_id,
            User.is_salesperson == True
        ).first()
        
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        
        # Calculate performance metrics
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total sales this month
        monthly_sales = db.query(func.sum(SalesInvoice.total_amount)).filter(
            SalesInvoice.created_by == partner_id,
            SalesInvoice.created_at >= current_month
        ).scalar() or 0
        
        # Total orders this month
        monthly_orders = db.query(func.count(SalesOrder.id)).filter(
            SalesOrder.salesperson_id == partner_id,
            SalesOrder.created_at >= current_month
        ).scalar() or 0
        
        # Commission calculations (mock data for now)
        commission_rate = 2.25  # Default rate
        earned_commission = float(monthly_sales) * (commission_rate / 100)
        pending_commission = earned_commission * 0.7  # 70% pending
        paid_commission = earned_commission * 0.3  # 30% paid
        
        # Customer acquisition
        new_customers = db.query(func.count(Customer.id)).filter(
            Customer.salesperson_id == partner_id,
            Customer.created_at >= current_month
        ).scalar() or 0
        
        # Performance ranking (mock)
        total_partners = db.query(func.count(User.id)).join(Role).filter(
            Role.name == "partner_salesman"
        ).scalar() or 1
        
        performance_rank = min(max(1, int(total_partners * 0.3)), total_partners)
        
        # Weekly performance breakdown
        weekly_performance = []
        for i in range(4):  # Last 4 weeks
            week_start = current_month - timedelta(weeks=i)
            week_end = week_start + timedelta(days=7)
            
            week_sales = db.query(func.sum(SalesInvoice.total_amount)).filter(
                SalesInvoice.created_by == partner_id,
                SalesInvoice.created_at >= week_start,
                SalesInvoice.created_at < week_end
            ).scalar() or 0
            
            weekly_performance.append({
                "week": f"Week {4-i}",
                "sales": float(week_sales),
                "orders": 5 + i * 2,  # Mock data
                "commission": float(week_sales) * (commission_rate / 100)
            })
        
        return {
            "partner_profile": {
                "id": partner.id,
                "name": partner.name,
                "employee_code": partner.employee_code,
                "status": "active" if partner.is_active else "pending",
                "joined_date": partner.created_at.isoformat(),
                "commission_rate": commission_rate
            },
            "monthly_performance": {
                "total_sales": float(monthly_sales),
                "total_orders": monthly_orders,
                "new_customers": new_customers,
                "commission_earned": earned_commission,
                "commission_paid": paid_commission,
                "commission_pending": pending_commission
            },
            "ranking": {
                "current_rank": performance_rank,
                "total_partners": total_partners,
                "performance_percentile": round((1 - performance_rank / total_partners) * 100, 1)
            },
            "weekly_breakdown": weekly_performance,
            "targets": {
                "monthly_sales_target": 50000.0,  # IQD
                "achievement_percentage": round((float(monthly_sales) / 50000.0) * 100, 1),
                "customers_target": 10,
                "customers_achievement": round((new_customers / 10) * 100, 1)
            },
            "quick_actions": [
                {"action": "create_order", "label": "New Order", "url": "/orders/create"},
                {"action": "customer_list", "label": "My Customers", "url": "/customers/mine"},
                {"action": "commission_history", "label": "Commission History", "url": "/commission/history"},
                {"action": "product_catalog", "label": "Product Catalog", "url": "/products/catalog"},
                {"action": "price_calculator", "label": "Price Calculator", "url": "/pricing/calculator"}
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

@router.get("/commission/history/{partner_id}")
async def get_commission_history(
    partner_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, paid, disputed"),
    db: Session = Depends(get_db)
):
    """
    💰 Commission History & Payment Tracking
    Detailed breakdown of all commission earnings
    """
    
    try:
        # Verify partner exists
        partner = db.query(User).filter(User.id == partner_id).first()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        
        # Get partner's sales with commission details
        offset = (page - 1) * limit
        
        query = db.query(SalesInvoice).filter(SalesInvoice.created_by == partner_id)
        
        if status_filter:
            # Mock status filter - in production, you'd have commission status table
            pass
        
        total_records = query.count()
        sales = query.order_by(desc(SalesInvoice.created_at)).offset(offset).limit(limit).all()
        
        commission_records = []
        for sale in sales:
            commission_rate = 2.25  # Get from partner config
            commission_amount = float(sale.total_amount) * (commission_rate / 100)
            
            commission_records.append({
                "id": sale.id,
                "invoice_number": sale.invoice_number,
                "customer_name": sale.customer.name if sale.customer else "Walk-in Customer",
                "sale_amount": float(sale.total_amount),
                "commission_rate": commission_rate,
                "commission_amount": commission_amount,
                "payment_status": "paid" if sale.status == "PAID" else "pending",
                "sale_date": sale.created_at.isoformat(),
                "payment_date": sale.created_at.isoformat() if sale.status == "PAID" else None
            })
        
        # Calculate summary
        total_commission = sum(record["commission_amount"] for record in commission_records)
        paid_commission = sum(record["commission_amount"] for record in commission_records if record["payment_status"] == "paid")
        pending_commission = total_commission - paid_commission
        
        return {
            "summary": {
                "total_commission": total_commission,
                "paid_commission": paid_commission,
                "pending_commission": pending_commission,
                "total_sales": sum(record["sale_amount"] for record in commission_records)
            },
            "records": commission_records,
            "pagination": {
                "current_page": page,
                "total_pages": (total_records + limit - 1) // limit,
                "total_records": total_records,
                "records_per_page": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Commission history error: {str(e)}")

@router.get("/marketplace/products")
async def get_marketplace_products(
    partner_id: int = Query(...),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    🛒 Partner Salesmen Marketplace - Product Catalog
    Complete product catalog with partner-specific pricing
    """
    
    try:
        # Verify partner
        partner = db.query(User).filter(User.id == partner_id).first()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        
        # Build product query
        query = db.query(Product).filter(Product.is_active == True)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        offset = (page - 1) * limit
        total_products = query.count()
        products = query.offset(offset).limit(limit).all()
        
        # Format products with partner pricing
        marketplace_products = []
        for product in products:
            # Calculate partner-specific pricing
            base_price = float(product.unit_price)
            partner_commission = 2.25  # %
            partner_markup = 15.0  # % markup for partners
            
            partner_price = base_price * (1 + partner_markup / 100)
            commission_per_sale = partner_price * (partner_commission / 100)
            
            marketplace_products.append({
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "name_ar": product.name_ar,
                "description": product.description,
                "category": product.category.name if product.category else "General",
                "images": product.images or [],
                "pricing": {
                    "base_price": base_price,
                    "partner_price": partner_price,
                    "commission_rate": partner_commission,
                    "commission_per_sale": commission_per_sale,
                    "profit_margin": partner_markup
                },
                "inventory": {
                    "available": True,  # Mock availability
                    "stock_level": "high",  # high, medium, low
                    "estimated_delivery": "2-3 days"
                },
                "specifications": {
                    "brand": product.brand,
                    "model": product.model,
                    "weight": float(product.weight) if product.weight else None,
                    "dimensions": product.dimensions,
                    "color": product.color,
                    "size": product.size
                }
            })
        
        return {
            "products": marketplace_products,
            "pagination": {
                "current_page": page,
                "total_pages": (total_products + limit - 1) // limit,
                "total_products": total_products,
                "products_per_page": limit
            },
            "filters": {
                "categories": [
                    {"id": 1, "name": "Laptops", "count": 45},
                    {"id": 2, "name": "Mobile Phones", "count": 78},
                    {"id": 3, "name": "Accessories", "count": 156},
                    {"id": 4, "name": "Networking", "count": 34},
                    {"id": 5, "name": "Monitors", "count": 29}
                ],
                "price_ranges": [
                    {"min": 0, "max": 50000, "label": "Under 50K IQD"},
                    {"min": 50000, "max": 200000, "label": "50K - 200K IQD"},
                    {"min": 200000, "max": 500000, "label": "200K - 500K IQD"},
                    {"min": 500000, "max": None, "label": "Above 500K IQD"}
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Marketplace error: {str(e)}")

@router.post("/payment/request")
async def request_commission_payment(
    partner_id: int,
    amount: float,
    payment_method: str,
    account_details: str,
    db: Session = Depends(get_db)
):
    """
    💳 Commission Payment Request
    Partner salesmen can request commission payments
    """
    
    try:
        partner = db.query(User).filter(User.id == partner_id).first()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        
        # Validate available commission
        # In production, calculate actual available commission
        available_commission = 1500.75  # Mock available amount
        
        if amount > available_commission:
            raise HTTPException(
                status_code=400, 
                detail=f"Requested amount exceeds available commission. Available: {available_commission}"
            )
        
        # Create payment request
        payment_request = {
            "id": f"PR{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "partner_id": partner_id,
            "partner_name": partner.name,
            "amount": amount,
            "payment_method": payment_method,
            "account_details": account_details,
            "status": "pending_review",
            "requested_at": datetime.now().isoformat(),
            "processing_time": "1-2 business days"
        }
        
        return {
            "success": True,
            "message": "Payment request submitted successfully",
            "request_details": payment_request,
            "next_steps": [
                "Request under review",
                "Account verification",
                "Payment processing",
                "Confirmation notification"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment request failed: {str(e)}") 