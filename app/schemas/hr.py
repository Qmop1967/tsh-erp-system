from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum


# ===============================================
# ENUMS FOR HR SCHEMAS
# ===============================================

class EmploymentStatusSchema(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class PayrollStatusSchema(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    PAID = "paid"
    CANCELLED = "cancelled"


class LeaveTypeSchema(str, Enum):
    ANNUAL = "annual"
    SICK = "sick"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    EMERGENCY = "emergency"
    RELIGIOUS = "religious"
    UNPAID = "unpaid"


class LeaveStatusSchema(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class AttendanceStatusSchema(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    OVERTIME = "overtime"


class PerformanceRankSchema(str, Enum):
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"


class PaymentMethodSchema(str, Enum):
    ZAINCASH = "zaincash"
    SUPERQI = "superqi"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class DocumentTypeSchema(str, Enum):
    CONTRACT = "contract"
    ID_COPY = "id_copy"
    PASSPORT_COPY = "passport_copy"
    CERTIFICATE = "certificate"
    MEDICAL_REPORT = "medical_report"
    PERFORMANCE_DOCUMENT = "performance_document"
    OTHER = "other"


# ===============================================
# EMPLOYEE SCHEMAS
# ===============================================

class EmployeeBase(BaseModel):
    first_name_ar: str = Field(..., min_length=1, max_length=100)
    first_name_en: str = Field(..., min_length=1, max_length=100)
    last_name_ar: str = Field(..., min_length=1, max_length=100)
    last_name_en: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    phone: str = Field(..., min_length=10, max_length=20)
    emergency_contact: Optional[str] = Field(None, max_length=20)
    address_ar: Optional[str] = None
    address_en: Optional[str] = None
    department_id: int = Field(..., gt=0)
    position_id: int = Field(..., gt=0)
    direct_manager_id: Optional[int] = Field(None, gt=0)
    employment_status: EmploymentStatusSchema = EmploymentStatusSchema.ACTIVE
    hire_date: date
    base_salary: float = Field(..., gt=0)
    currency: str = Field(default="IQD", max_length=3)
    is_commission_eligible: bool = False
    commission_rate: float = Field(default=0.0, ge=0, le=100)
    working_hours_per_day: float = Field(default=8.0, gt=0)
    working_days_per_week: int = Field(default=6, ge=1, le=7)
    national_id: Optional[str] = Field(None, max_length=50)
    passport_number: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    marital_status: Optional[str] = Field(None, max_length=20)


class EmployeeCreate(EmployeeBase):
    employee_code: Optional[str] = Field(None, max_length=20)
    termination_date: Optional[date] = None


class EmployeeUpdate(BaseModel):
    first_name_ar: Optional[str] = Field(None, min_length=1, max_length=100)
    first_name_en: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name_ar: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name_en: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, regex=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    emergency_contact: Optional[str] = Field(None, max_length=20)
    address_ar: Optional[str] = None
    address_en: Optional[str] = None
    department_id: Optional[int] = Field(None, gt=0)
    position_id: Optional[int] = Field(None, gt=0)
    direct_manager_id: Optional[int] = Field(None, gt=0)
    employment_status: Optional[EmploymentStatusSchema] = None
    base_salary: Optional[float] = Field(None, gt=0)
    is_commission_eligible: Optional[bool] = None
    commission_rate: Optional[float] = Field(None, ge=0, le=100)
    working_hours_per_day: Optional[float] = Field(None, gt=0)
    working_days_per_week: Optional[int] = Field(None, ge=1, le=7)
    termination_date: Optional[date] = None


class EmployeeResponse(EmployeeBase):
    id: int
    employee_code: str
    full_name_ar: str
    full_name_en: str
    profile_photo_url: Optional[str] = None
    termination_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===============================================
# ATTENDANCE SCHEMAS
# ===============================================

class AttendanceRecordCreate(BaseModel):
    employee_id: int = Field(..., gt=0)
    date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    check_in_latitude: Optional[float] = Field(None, ge=-90, le=90)
    check_in_longitude: Optional[float] = Field(None, ge=-180, le=180)
    check_out_latitude: Optional[float] = Field(None, ge=-90, le=90)
    check_out_longitude: Optional[float] = Field(None, ge=-180, le=180)
    check_in_location: Optional[str] = Field(None, max_length=200)
    check_out_location: Optional[str] = Field(None, max_length=200)
    status: AttendanceStatusSchema
    notes: Optional[str] = None


class AttendanceRecordResponse(AttendanceRecordCreate):
    id: int
    total_hours: float
    regular_hours: float
    overtime_hours: float
    is_late: bool
    late_minutes: int
    manager_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===============================================
# LEAVE REQUEST SCHEMAS
# ===============================================

class LeaveRequestCreate(BaseModel):
    employee_id: int = Field(..., gt=0)
    leave_type: LeaveTypeSchema
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=10)
    supporting_documents: Optional[List[str]] = None
    employee_comments: Optional[str] = None

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class LeaveRequestResponse(LeaveRequestCreate):
    id: int
    total_days: int
    status: LeaveStatusSchema
    request_date: datetime
    review_date: Optional[datetime] = None
    approval_date: Optional[datetime] = None
    manager_comments: Optional[str] = None
    hr_comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaveRequestApproval(BaseModel):
    manager_comments: Optional[str] = None
    hr_comments: Optional[str] = None


# ===============================================
# PERFORMANCE REVIEW SCHEMAS
# ===============================================

class PerformanceReviewCreate(BaseModel):
    employee_id: int = Field(..., gt=0)
    review_period_start: date
    review_period_end: date
    review_type: str = Field(..., max_length=50)
    overall_rating: float = Field(..., ge=1, le=5)
    technical_skills: Optional[float] = Field(None, ge=1, le=5)
    communication_skills: Optional[float] = Field(None, ge=1, le=5)
    teamwork: Optional[float] = Field(None, ge=1, le=5)
    leadership: Optional[float] = Field(None, ge=1, le=5)
    punctuality: Optional[float] = Field(None, ge=1, le=5)
    productivity: Optional[float] = Field(None, ge=1, le=5)
    goals_achieved: Optional[str] = None
    goals_missed: Optional[str] = None
    new_goals: Optional[str] = None
    employee_self_assessment: Optional[str] = None
    manager_feedback: Optional[str] = None
    development_plan: Optional[str] = None
    salary_increase_recommended: bool = False
    recommended_increase_amount: Optional[float] = Field(None, ge=0)
    recommended_increase_percentage: Optional[float] = Field(None, ge=0, le=100)
    review_date: date


class PerformanceReviewResponse(PerformanceReviewCreate):
    id: int
    is_completed: bool
    employee_acknowledged: bool
    employee_acknowledgment_date: Optional[datetime] = None
    hr_comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===============================================
# PAYROLL SCHEMAS
# ===============================================

class PayrollRecordCreate(BaseModel):
    employee_id: int = Field(..., gt=0)
    payroll_month: int = Field(..., ge=1, le=12)
    payroll_year: int = Field(..., ge=2020, le=2030)
    pay_period_start: date
    pay_period_end: date
    base_salary: float = Field(..., gt=0)
    commission_amount: float = Field(default=0.0, ge=0)
    overtime_amount: float = Field(default=0.0, ge=0)
    bonus_amount: float = Field(default=0.0, ge=0)
    allowances: float = Field(default=0.0, ge=0)
    social_security: float = Field(default=0.0, ge=0)
    tax_deduction: float = Field(default=0.0, ge=0)
    insurance_deduction: float = Field(default=0.0, ge=0)
    loan_deduction: float = Field(default=0.0, ge=0)
    other_deductions: float = Field(default=0.0, ge=0)
    working_days: int = Field(..., ge=1, le=31)
    actual_working_days: int = Field(..., ge=0, le=31)
    total_hours_worked: float = Field(..., ge=0)
    overtime_hours: float = Field(default=0.0, ge=0)
    payment_method: PaymentMethodSchema = PaymentMethodSchema.CASH
    payment_reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class PayrollRecordResponse(PayrollRecordCreate):
    id: int
    gross_salary: float
    total_deductions: float
    net_salary: float
    status: PayrollStatusSchema
    payment_date: Optional[date] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===============================================
# NEW ENHANCED SCHEMAS
# ===============================================

class EmployeeDocumentCreate(BaseModel):
    employee_id: int = Field(..., gt=0)
    document_type: DocumentTypeSchema
    title_ar: str = Field(..., min_length=1, max_length=200)
    title_en: str = Field(..., min_length=1, max_length=200)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    file_url: str = Field(..., min_length=1, max_length=500)
    file_name: str = Field(..., min_length=1, max_length=200)
    file_size: Optional[int] = Field(None, gt=0)
    file_type: Optional[str] = Field(None, max_length=50)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None


class EmployeeDocumentResponse(EmployeeDocumentCreate):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PerformanceRankingCreate(BaseModel):
    employee_id: int = Field(..., gt=0)
    current_rank: PerformanceRankSchema
    total_sales: float = Field(default=0.0, ge=0)
    target_achievement_percentage: float = Field(default=0.0, ge=0, le=200)
    customer_satisfaction_score: float = Field(default=0.0, ge=0, le=10)
    monthly_kpi_score: float = Field(default=0.0, ge=0, le=100)
    quarterly_kpi_score: float = Field(default=0.0, ge=0, le=100)
    annual_kpi_score: float = Field(default=0.0, ge=0, le=100)
    ranking_month: int = Field(..., ge=1, le=12)
    ranking_year: int = Field(..., ge=2020, le=2030)
    rank_bonus_amount: float = Field(default=0.0, ge=0)
    rank_bonus_percentage: float = Field(default=0.0, ge=0, le=100)
    special_incentives: Optional[List[str]] = None
    promotion_notes: Optional[str] = None
    manager_comments: Optional[str] = None


class PerformanceRankingResponse(PerformanceRankingCreate):
    id: int
    previous_rank: Optional[PerformanceRankSchema] = None
    is_current: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PayslipRecordCreate(BaseModel):
    payroll_record_id: int = Field(..., gt=0)
    employee_id: int = Field(..., gt=0)
    payslip_content_ar: str = Field(..., min_length=1)
    payslip_content_en: str = Field(..., min_length=1)
    pdf_file_ar_url: Optional[str] = Field(None, max_length=500)
    pdf_file_en_url: Optional[str] = Field(None, max_length=500)
    sent_via_whatsapp: bool = False
    sent_via_email: bool = False


class PayslipRecordResponse(PayslipRecordCreate):
    id: int
    payslip_number: str
    employee_acknowledged: bool
    generated_at: datetime
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HRNotificationCreate(BaseModel):
    title_ar: str = Field(..., min_length=1, max_length=200)
    title_en: str = Field(..., min_length=1, max_length=200)
    message_ar: str = Field(..., min_length=1)
    message_en: str = Field(..., min_length=1)
    notification_type: str = Field(..., max_length=50)
    priority: str = Field(default="normal", regex=r'^(low|normal|high|urgent)$')
    employee_id: Optional[int] = Field(None, gt=0)
    department_id: Optional[int] = Field(None, gt=0)
    send_to_all: bool = False
    send_push: bool = True
    send_whatsapp: bool = False
    send_email: bool = False
    scheduled_for: Optional[datetime] = None


class HRNotificationResponse(HRNotificationCreate):
    id: int
    is_sent: bool
    is_read: bool
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===============================================
# DASHBOARD SCHEMAS
# ===============================================

class HRDashboardMetricsResponse(BaseModel):
    total_employees: int
    active_employees: int
    new_hires_month: int
    terminations_month: int
    average_attendance_rate: float
    total_late_arrivals: int
    total_overtime_hours: float
    pending_leave_requests: int
    approved_leaves_month: int
    total_payroll_amount: float
    average_salary: float
    total_overtime_cost: float
    pending_reviews: int
    completed_reviews_month: int
    average_performance_rating: float
    metric_date: date

    class Config:
        from_attributes = True


class EmployeeStatusSummary(BaseModel):
    employee_id: int
    employee_code: str
    full_name_en: str
    full_name_ar: str
    department: str
    position: str
    profile_photo_url: Optional[str] = None
    employment_status: EmploymentStatusSchema
    current_rank: Optional[PerformanceRankSchema] = None
    last_seen: Optional[datetime] = None
    is_present_today: bool
    performance_rating: Optional[float] = None

    class Config:
        from_attributes = True


class HRComprehensiveDashboard(BaseModel):
    metrics: HRDashboardMetricsResponse
    employee_status_list: List[EmployeeStatusSummary]
    recent_activities: List[Dict[str, Any]]
    pending_approvals: Dict[str, int]
    performance_rankings: List[PerformanceRankingResponse]

    class Config:
        from_attributes = True 