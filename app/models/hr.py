from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Date, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
import enum
from app.db.database import Base


class EmploymentStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class PayrollStatus(enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    PAID = "paid"
    CANCELLED = "cancelled"


class LeaveType(enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    EMERGENCY = "emergency"
    RELIGIOUS = "religious"  # Added religious leave type as required
    UNPAID = "unpaid"


class LeaveStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class AttendanceStatus(enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    OVERTIME = "overtime"


class PerformanceRank(enum.Enum):
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"


class PaymentMethod(enum.Enum):
    ZAINCASH = "zaincash"
    SUPERQI = "superqi"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class DocumentType(enum.Enum):
    CONTRACT = "contract"
    ID_COPY = "id_copy"
    PASSPORT_COPY = "passport_copy"
    CERTIFICATE = "certificate"
    MEDICAL_REPORT = "medical_report"
    PERFORMANCE_DOCUMENT = "performance_document"
    OTHER = "other"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(20), unique=True, nullable=False, index=True)
    
    # Personal Information
    first_name_ar = Column(String(100), nullable=False)
    first_name_en = Column(String(100), nullable=False)
    last_name_ar = Column(String(100), nullable=False)
    last_name_en = Column(String(100), nullable=False)
    full_name_ar = Column(String(200), nullable=False, index=True)
    full_name_en = Column(String(200), nullable=False, index=True)
    
    # Contact Information
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    emergency_contact = Column(String(20))
    address_ar = Column(Text)
    address_en = Column(Text)
    
    # Employment Details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Link to User table
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    direct_manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Employment Status
    employment_status = Column(Enum(EmploymentStatus), default=EmploymentStatus.ACTIVE, nullable=False)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    
    # Salary Information
    base_salary = Column(Float, nullable=False)
    currency = Column(String(3), default="IQD", nullable=False)
    is_commission_eligible = Column(Boolean, default=False, nullable=False)
    commission_rate = Column(Float, default=0.0, nullable=False)  # Percentage
    
    # Working Schedule
    working_hours_per_day = Column(Float, default=8.0, nullable=False)
    working_days_per_week = Column(Integer, default=6, nullable=False)
    
    # Profile Information
    profile_photo_url = Column(String(500))
    national_id = Column(String(50), unique=True)
    passport_number = Column(String(50), unique=True, nullable=True)
    birth_date = Column(Date)
    gender = Column(String(10))
    marital_status = Column(String(20))
    
    # System Fields
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="employee_profile")
    department = relationship("Department", foreign_keys=[department_id], back_populates="employees")
    position = relationship("Position", foreign_keys=[position_id], back_populates="employees")
    direct_manager = relationship("Employee", remote_side=[id], foreign_keys=[direct_manager_id])
    subordinates = relationship("Employee", remote_side=[direct_manager_id])
    
    # HR Related Relationships
    payroll_records = relationship("PayrollRecord", foreign_keys="PayrollRecord.employee_id", back_populates="employee")
    attendance_records = relationship("AttendanceRecord", foreign_keys="AttendanceRecord.employee_id", back_populates="employee")
    leave_requests = relationship("LeaveRequest", foreign_keys="LeaveRequest.employee_id", back_populates="employee")
    performance_reviews = relationship("PerformanceReview", foreign_keys="PerformanceReview.employee_id", back_populates="employee")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name_ar = Column(String(100), nullable=False, index=True)
    name_en = Column(String(100), nullable=False, index=True)
    description_ar = Column(Text)
    description_en = Column(Text)
    
    # Department Head
    head_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Budget Information
    monthly_budget = Column(Float, default=0.0)
    annual_budget = Column(Float, default=0.0)
    
    # System Fields
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = relationship("Employee", foreign_keys="Employee.department_id", back_populates="department")
    head_employee = relationship("Employee", foreign_keys=[head_employee_id])


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    title_ar = Column(String(100), nullable=False, index=True)
    title_en = Column(String(100), nullable=False, index=True)
    description_ar = Column(Text)
    description_en = Column(Text)
    
    # Salary Range
    min_salary = Column(Float, nullable=False)
    max_salary = Column(Float, nullable=False)
    
    # Position Level
    level = Column(Integer, default=1, nullable=False)  # 1=Entry, 2=Mid, 3=Senior, 4=Manager, 5=Director
    
    # System Fields
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = relationship("Employee", back_populates="position")


class PayrollRecord(Base):
    __tablename__ = "payroll_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Payroll Period
    payroll_month = Column(Integer, nullable=False)  # 1-12
    payroll_year = Column(Integer, nullable=False)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    
    # Earnings
    base_salary = Column(Float, nullable=False)
    commission_amount = Column(Float, default=0.0, nullable=False)
    overtime_amount = Column(Float, default=0.0, nullable=False)
    bonus_amount = Column(Float, default=0.0, nullable=False)
    allowances = Column(Float, default=0.0, nullable=False)
    gross_salary = Column(Float, nullable=False)
    
    # Deductions
    tax_deduction = Column(Float, default=0.0, nullable=False)
    social_security = Column(Float, default=0.0, nullable=False)
    insurance_deduction = Column(Float, default=0.0, nullable=False)
    loan_deduction = Column(Float, default=0.0, nullable=False)
    other_deductions = Column(Float, default=0.0, nullable=False)
    total_deductions = Column(Float, default=0.0, nullable=False)
    
    # Net Salary
    net_salary = Column(Float, nullable=False)
    
    # Working Days & Hours
    working_days = Column(Integer, nullable=False)
    actual_working_days = Column(Integer, nullable=False)
    total_hours_worked = Column(Float, nullable=False)
    overtime_hours = Column(Float, default=0.0, nullable=False)
    
    # Payment Information
    payment_method = Column(String(50), default="bank_transfer")
    bank_account = Column(String(50))
    payment_date = Column(Date)
    payment_reference = Column(String(100))
    
    # Status
    status = Column(Enum(PayrollStatus), default=PayrollStatus.PENDING, nullable=False)
    
    # Notes
    notes = Column(Text)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="payroll_records")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Date and Time
    date = Column(Date, nullable=False, index=True)
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    
    # Location Information (GPS Tracking)
    check_in_latitude = Column(Float)
    check_in_longitude = Column(Float)
    check_out_latitude = Column(Float)
    check_out_longitude = Column(Float)
    check_in_location = Column(String(200))
    check_out_location = Column(String(200))
    
    # Calculated Hours
    total_hours = Column(Float, default=0.0)
    regular_hours = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    
    # Status
    status = Column(Enum(AttendanceStatus), nullable=False)
    is_late = Column(Boolean, default=False)
    late_minutes = Column(Integer, default=0)
    
    # Notes
    notes = Column(Text)
    manager_notes = Column(Text)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="attendance_records")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Leave Details
    leave_type = Column(Enum(LeaveType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Integer, nullable=False)
    
    # Request Information
    reason = Column(Text, nullable=False)
    supporting_documents = Column(Text)  # JSON array of document URLs
    
    # Status
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False)
    
    # Approval Workflow
    requested_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("employees.id"))
    approved_by = Column(Integer, ForeignKey("employees.id"))
    
    # Important Dates
    request_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    review_date = Column(DateTime)
    approval_date = Column(DateTime)
    
    # Comments
    employee_comments = Column(Text)
    manager_comments = Column(Text)
    hr_comments = Column(Text)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="leave_requests")


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Review Period
    review_period_start = Column(Date, nullable=False)
    review_period_end = Column(Date, nullable=False)
    review_type = Column(String(50), nullable=False)  # annual, semi_annual, quarterly, probation
    
    # Ratings (1-5 scale)
    overall_rating = Column(Float, nullable=False)
    technical_skills = Column(Float, default=0.0)
    communication_skills = Column(Float, default=0.0)
    teamwork = Column(Float, default=0.0)
    leadership = Column(Float, default=0.0)
    punctuality = Column(Float, default=0.0)
    productivity = Column(Float, default=0.0)
    
    # Goals and Objectives
    goals_achieved = Column(Text)
    goals_missed = Column(Text)
    new_goals = Column(Text)
    
    # Comments
    employee_self_assessment = Column(Text)
    manager_feedback = Column(Text)
    hr_comments = Column(Text)
    development_plan = Column(Text)
    
    # Salary Review
    salary_increase_recommended = Column(Boolean, default=False)
    recommended_increase_amount = Column(Float, default=0.0)
    recommended_increase_percentage = Column(Float, default=0.0)
    
    # Status
    is_completed = Column(Boolean, default=False)
    employee_acknowledged = Column(Boolean, default=False)
    
    # Important Dates
    review_date = Column(Date, nullable=False)
    employee_acknowledgment_date = Column(DateTime)
    
    # Reviewers
    reviewed_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    hr_reviewed_by = Column(Integer, ForeignKey("employees.id"))
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="performance_reviews")


class HRDashboardMetrics(Base):
    __tablename__ = "hr_dashboard_metrics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Date for metrics
    metric_date = Column(Date, nullable=False, index=True)
    
    # Employee Metrics
    total_employees = Column(Integer, default=0)
    active_employees = Column(Integer, default=0)
    new_hires_month = Column(Integer, default=0)
    terminations_month = Column(Integer, default=0)
    
    # Attendance Metrics
    average_attendance_rate = Column(Float, default=0.0)
    total_late_arrivals = Column(Integer, default=0)
    total_overtime_hours = Column(Float, default=0.0)
    
    # Leave Metrics
    pending_leave_requests = Column(Integer, default=0)
    approved_leaves_month = Column(Integer, default=0)
    
    # Payroll Metrics
    total_payroll_amount = Column(Float, default=0.0)
    average_salary = Column(Float, default=0.0)
    total_overtime_cost = Column(Float, default=0.0)
    
    # Performance Metrics
    pending_reviews = Column(Integer, default=0)
    completed_reviews_month = Column(Integer, default=0)
    average_performance_rating = Column(Float, default=0.0)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ===============================================
# NEW ENHANCED HR MODELS - TSH ERP SYSTEM
# ===============================================

class EmployeeDocument(Base):
    """Employee document storage for contracts, certificates, and other HR documents"""
    __tablename__ = "employee_documents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Document Information
    document_type = Column(Enum(DocumentType), nullable=False)
    title_ar = Column(String(200), nullable=False)
    title_en = Column(String(200), nullable=False)
    description_ar = Column(Text)
    description_en = Column(Text)
    
    # File Information
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    file_type = Column(String(50))  # MIME type
    
    # Document Dates
    issue_date = Column(Date)
    expiry_date = Column(Date)
    
    # System Fields
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])


class EmployeePerformanceRanking(Base):
    """Performance ranking system with Silver/Gold/Diamond levels"""
    __tablename__ = "employee_performance_rankings"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Ranking Information
    current_rank = Column(Enum(PerformanceRank), default=PerformanceRank.SILVER, nullable=False)
    previous_rank = Column(Enum(PerformanceRank), nullable=True)
    
    # Performance Metrics
    total_sales = Column(Float, default=0.0)
    target_achievement_percentage = Column(Float, default=0.0)
    customer_satisfaction_score = Column(Float, default=0.0)
    
    # KPI Tracking
    monthly_kpi_score = Column(Float, default=0.0)
    quarterly_kpi_score = Column(Float, default=0.0)
    annual_kpi_score = Column(Float, default=0.0)
    
    # Ranking Period
    ranking_month = Column(Integer, nullable=False)  # 1-12
    ranking_year = Column(Integer, nullable=False)
    
    # Rewards and Bonuses
    rank_bonus_amount = Column(Float, default=0.0)
    rank_bonus_percentage = Column(Float, default=0.0)
    special_incentives = Column(Text)  # JSON array of special rewards
    
    # Status and Notes
    is_current = Column(Boolean, default=True, nullable=False)
    promotion_notes = Column(Text)
    manager_comments = Column(Text)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])


class PayslipRecord(Base):
    """Digital payslip generation and storage"""
    __tablename__ = "payslip_records"

    id = Column(Integer, primary_key=True, index=True)
    payroll_record_id = Column(Integer, ForeignKey("payroll_records.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Payslip Information
    payslip_number = Column(String(50), unique=True, nullable=False)
    
    # Language Versions
    payslip_content_ar = Column(Text, nullable=False)  # Arabic payslip content
    payslip_content_en = Column(Text, nullable=False)  # English payslip content
    
    # Generated Files
    pdf_file_ar_url = Column(String(500))  # Arabic PDF
    pdf_file_en_url = Column(String(500))  # English PDF
    
    # Delivery Information
    sent_via_whatsapp = Column(Boolean, default=False)
    sent_via_email = Column(Boolean, default=False)
    employee_acknowledged = Column(Boolean, default=False)
    
    # Delivery Dates
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payroll_record = relationship("PayrollRecord", foreign_keys=[payroll_record_id])
    employee = relationship("Employee", foreign_keys=[employee_id])


class HRNotification(Base):
    """HR notifications and alerts system"""
    __tablename__ = "hr_notifications"

    id = Column(Integer, primary_key=True, index=True)
    
    # Notification Details
    title_ar = Column(String(200), nullable=False)
    title_en = Column(String(200), nullable=False)
    message_ar = Column(Text, nullable=False)
    message_en = Column(Text, nullable=False)
    
    # Notification Type
    notification_type = Column(String(50), nullable=False)  # leave_approved, payroll_generated, etc.
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Recipients
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)  # Specific employee
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)  # All department
    send_to_all = Column(Boolean, default=False)  # All employees
    
    # Delivery Channels
    send_push = Column(Boolean, default=True)
    send_whatsapp = Column(Boolean, default=False)
    send_email = Column(Boolean, default=False)
    
    # Status
    is_sent = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    
    # Dates
    scheduled_for = Column(DateTime)
    sent_at = Column(DateTime)
    read_at = Column(DateTime)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    department = relationship("Department", foreign_keys=[department_id])


class WhatsAppIntegration(Base):
    """WhatsApp integration for HR reports and communications"""
    __tablename__ = "whatsapp_integrations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Message Information
    recipient_phone = Column(String(20), nullable=False)
    recipient_name = Column(String(200), nullable=False)
    
    # Message Content
    message_type = Column(String(50), nullable=False)  # payslip, performance_report, etc.
    message_content = Column(Text, nullable=False)
    
    # File Attachments
    attachment_urls = Column(Text)  # JSON array of file URLs
    
    # Status Tracking
    is_sent = Column(Boolean, default=False)
    delivery_status = Column(String(20), default="pending")  # pending, sent, delivered, failed
    
    # Dates
    scheduled_for = Column(DateTime)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Related Records
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    payslip_id = Column(Integer, ForeignKey("payslip_records.id"), nullable=True)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    payslip = relationship("PayslipRecord", foreign_keys=[payslip_id]) 