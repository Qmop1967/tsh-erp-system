from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import json

from app.db.database import get_db
from app.models.hr import (
    Employee, Department, Position, PayrollRecord, AttendanceRecord,
    LeaveRequest, PerformanceReview, EmploymentStatus, PayrollStatus,
    LeaveType, LeaveStatus, AttendanceStatus
)
from app.services.hr_service import HRService
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()

# Dependency function for getting current user
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(lambda: "fake_token")):
    """Dependency function to get current user - simplified for testing"""
    # For testing purposes, return a mock user
    # In production, this would validate the JWT token
    return User(id=1, email="admin@tsh.com", role="admin")

# HR Dashboard Endpoints
@router.get("/dashboard", response_model=Dict[str, Any])
async def get_hr_dashboard(
    date_filter: Optional[date] = Query(None, description="Date for metrics (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get HR dashboard metrics including employee count, attendance, payroll, and performance data.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: لوحة تحكم إدارة الموارد البشرية - إحصائيات شاملة للموظفين والحضور والرواتب والأداء
    """
    try:
        metrics = HRService.get_employee_dashboard_metrics(db, date_filter)
        return {
            "success": True,
            "data": metrics,
            "message": "HR dashboard metrics retrieved successfully",
            "message_ar": "تم جلب إحصائيات لوحة تحكم الموارد البشرية بنجاح"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving HR dashboard metrics: {str(e)}"
        )

# Employee Management Endpoints
@router.get("/employees", response_model=Dict[str, Any])
async def get_employees(
    department_id: Optional[int] = Query(None, description="Filter by department"),
    position_id: Optional[int] = Query(None, description="Filter by position"),
    employment_status: Optional[str] = Query(None, description="Filter by employment status"),
    search: Optional[str] = Query(None, description="Search employees by name, email, or code"),
    skip: int = Query(0, ge=0, description="Skip number of records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit number of records"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of employees with optional filters.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: قائمة الموظفين مع إمكانية التصفية والبحث
    """
    try:
        employment_status_enum = None
        if employment_status:
            employment_status_enum = EmploymentStatus(employment_status)
        
        employees = HRService.get_employees(
            db, department_id, position_id, employment_status_enum, search, skip, limit
        )
        
        employees_data = []
        for emp in employees:
            employees_data.append({
                "id": emp.id,
                "employee_code": emp.employee_code,
                "full_name_en": emp.full_name_en,
                "full_name_ar": emp.full_name_ar,
                "email": emp.email,
                "phone": emp.phone,
                "department": emp.department.name_en if emp.department else None,
                "position": emp.position.title_en if emp.position else None,
                "employment_status": emp.employment_status.value,
                "hire_date": emp.hire_date.isoformat(),
                "base_salary": emp.base_salary,
                "is_active": emp.is_active
            })
        
        return {
            "success": True,
            "data": employees_data,
            "total": len(employees_data),
            "message": "Employees retrieved successfully",
            "message_ar": "تم جلب قائمة الموظفين بنجاح"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving employees: {str(e)}"
        )

@router.post("/employees", response_model=Dict[str, Any])
async def create_employee(
    employee_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new employee record.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: إنشاء ملف موظف جديد
    """
    try:
        employee = HRService.create_employee(db, employee_data, current_user.id)
        
        return {
            "success": True,
            "data": {
                "id": employee.id,
                "employee_code": employee.employee_code,
                "full_name_en": employee.full_name_en,
                "full_name_ar": employee.full_name_ar,
                "email": employee.email,
                "employment_status": employee.employment_status.value
            },
            "message": "Employee created successfully",
            "message_ar": "تم إنشاء ملف الموظف بنجاح"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating employee: {str(e)}"
        )

@router.get("/employees/{employee_id}", response_model=Dict[str, Any])
async def get_employee_details(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific employee.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: تفاصيل الموظف الكاملة
    """
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        employee_data = {
            "id": employee.id,
            "employee_code": employee.employee_code,
            "personal_info": {
                "first_name_en": employee.first_name_en,
                "first_name_ar": employee.first_name_ar,
                "last_name_en": employee.last_name_en,
                "last_name_ar": employee.last_name_ar,
                "email": employee.email,
                "phone": employee.phone,
                "emergency_contact": employee.emergency_contact,
                "address_en": employee.address_en,
                "address_ar": employee.address_ar,
                "birth_date": employee.birth_date.isoformat() if employee.birth_date else None,
                "gender": employee.gender,
                "marital_status": employee.marital_status,
                "national_id": employee.national_id,
                "passport_number": employee.passport_number
            },
            "employment_info": {
                "department": employee.department.name_en if employee.department else None,
                "position": employee.position.title_en if employee.position else None,
                "employment_status": employee.employment_status.value,
                "hire_date": employee.hire_date.isoformat(),
                "termination_date": employee.termination_date.isoformat() if employee.termination_date else None,
                "direct_manager": employee.direct_manager.full_name_en if employee.direct_manager else None
            },
            "salary_info": {
                "base_salary": employee.base_salary,
                "currency": employee.currency,
                "is_commission_eligible": employee.is_commission_eligible,
                "commission_rate": employee.commission_rate,
                "working_hours_per_day": employee.working_hours_per_day,
                "working_days_per_week": employee.working_days_per_week
            },
            "is_active": employee.is_active,
            "created_at": employee.created_at.isoformat(),
            "updated_at": employee.updated_at.isoformat()
        }
        
        return {
            "success": True,
            "data": employee_data,
            "message": "Employee details retrieved successfully",
            "message_ar": "تم جلب تفاصيل الموظف بنجاح"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving employee details: {str(e)}"
        )

# Attendance Management Endpoints
@router.post("/attendance/check-in", response_model=Dict[str, Any])
async def check_in_employee(
    employee_id: int,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    location: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process employee check-in with GPS location tracking.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: تسجيل دخول الموظف مع تتبع الموقع الجغرافي
    """
    try:
        attendance = HRService.process_attendance(
            db, employee_id, "check_in", latitude, longitude, location, notes
        )
        
        return {
            "success": True,
            "data": {
                "attendance_id": attendance.id,
                "employee_id": attendance.employee_id,
                "date": attendance.date.isoformat(),
                "check_in_time": attendance.check_in_time.isoformat() if attendance.check_in_time else None,
                "location": attendance.check_in_location,
                "is_late": attendance.is_late,
                "late_minutes": attendance.late_minutes,
                "status": attendance.status.value
            },
            "message": "Check-in processed successfully",
            "message_ar": "تم تسجيل الدخول بنجاح"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing check-in: {str(e)}"
        )

@router.post("/attendance/check-out", response_model=Dict[str, Any])
async def check_out_employee(
    employee_id: int,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    location: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process employee check-out with GPS location tracking.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: تسجيل خروج الموظف مع تتبع الموقع الجغرافي
    """
    try:
        attendance = HRService.process_attendance(
            db, employee_id, "check_out", latitude, longitude, location, notes
        )
        
        return {
            "success": True,
            "data": {
                "attendance_id": attendance.id,
                "employee_id": attendance.employee_id,
                "date": attendance.date.isoformat(),
                "check_out_time": attendance.check_out_time.isoformat() if attendance.check_out_time else None,
                "total_hours": attendance.total_hours,
                "regular_hours": attendance.regular_hours,
                "overtime_hours": attendance.overtime_hours,
                "location": attendance.check_out_location,
                "status": attendance.status.value
            },
            "message": "Check-out processed successfully",
            "message_ar": "تم تسجيل الخروج بنجاح"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing check-out: {str(e)}"
        )

@router.get("/attendance/report", response_model=Dict[str, Any])
async def get_attendance_report(
    employee_id: Optional[int] = Query(None, description="Filter by employee"),
    start_date: Optional[date] = Query(None, description="Start date for report"),
    end_date: Optional[date] = Query(None, description="End date for report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get attendance report for employees.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: تقرير الحضور والغياب للموظفين
    """
    try:
        query = db.query(AttendanceRecord)
        
        if employee_id:
            query = query.filter(AttendanceRecord.employee_id == employee_id)
        
        if start_date:
            query = query.filter(AttendanceRecord.date >= start_date)
        
        if end_date:
            query = query.filter(AttendanceRecord.date <= end_date)
        
        attendance_records = query.all()
        
        report_data = []
        for record in attendance_records:
            report_data.append({
                "id": record.id,
                "employee_id": record.employee_id,
                "employee_name": record.employee.full_name_en if record.employee else None,
                "date": record.date.isoformat(),
                "check_in_time": record.check_in_time.isoformat() if record.check_in_time else None,
                "check_out_time": record.check_out_time.isoformat() if record.check_out_time else None,
                "total_hours": record.total_hours,
                "regular_hours": record.regular_hours,
                "overtime_hours": record.overtime_hours,
                "status": record.status.value,
                "is_late": record.is_late,
                "late_minutes": record.late_minutes,
                "check_in_location": record.check_in_location,
                "check_out_location": record.check_out_location
            })
        
        return {
            "success": True,
            "data": report_data,
            "total": len(report_data),
            "message": "Attendance report retrieved successfully",
            "message_ar": "تم جلب تقرير الحضور بنجاح"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving attendance report: {str(e)}"
        )

# Leave Management Endpoints
@router.post("/leave/request", response_model=Dict[str, Any])
async def create_leave_request(
    leave_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new leave request.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: إنشاء طلب إجازة جديد
    """
    try:
        # Get employee ID from current user
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee profile not found for current user"
            )
        
        # Convert string dates to date objects
        if isinstance(leave_data.get("start_date"), str):
            leave_data["start_date"] = datetime.fromisoformat(leave_data["start_date"]).date()
        if isinstance(leave_data.get("end_date"), str):
            leave_data["end_date"] = datetime.fromisoformat(leave_data["end_date"]).date()
        
        leave_request = HRService.create_leave_request(db, employee.id, leave_data)
        
        return {
            "success": True,
            "data": {
                "id": leave_request.id,
                "employee_id": leave_request.employee_id,
                "leave_type": leave_request.leave_type.value,
                "start_date": leave_request.start_date.isoformat(),
                "end_date": leave_request.end_date.isoformat(),
                "total_days": leave_request.total_days,
                "status": leave_request.status.value,
                "request_date": leave_request.request_date.isoformat()
            },
            "message": "Leave request created successfully",
            "message_ar": "تم إنشاء طلب الإجازة بنجاح"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating leave request: {str(e)}"
        )

@router.put("/leave/approve/{leave_request_id}", response_model=Dict[str, Any])
async def approve_leave_request(
    leave_request_id: int,
    manager_comments: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve a leave request.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: الموافقة على طلب الإجازة
    """
    try:
        # Get employee ID from current user
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee profile not found for current user"
            )
        
        leave_request = HRService.approve_leave_request(
            db, leave_request_id, employee.id, manager_comments
        )
        
        return {
            "success": True,
            "data": {
                "id": leave_request.id,
                "status": leave_request.status.value,
                "approved_by": leave_request.approved_by,
                "approval_date": leave_request.approval_date.isoformat() if leave_request.approval_date else None,
                "manager_comments": leave_request.manager_comments
            },
            "message": "Leave request approved successfully",
            "message_ar": "تم الموافقة على طلب الإجازة بنجاح"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving leave request: {str(e)}"
        )

# Payroll Management Endpoints
@router.post("/payroll/generate", response_model=Dict[str, Any])
async def generate_payroll(
    employee_id: int,
    payroll_month: int,
    payroll_year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate payroll for an employee for a specific month.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: إنشاء كشف راتب للموظف
    """
    try:
        payroll_record = HRService.generate_payroll(
            db, employee_id, payroll_month, payroll_year, current_user.id
        )
        
        return {
            "success": True,
            "data": {
                "id": payroll_record.id,
                "employee_id": payroll_record.employee_id,
                "payroll_month": payroll_record.payroll_month,
                "payroll_year": payroll_record.payroll_year,
                "base_salary": payroll_record.base_salary,
                "gross_salary": payroll_record.gross_salary,
                "total_deductions": payroll_record.total_deductions,
                "net_salary": payroll_record.net_salary,
                "overtime_amount": payroll_record.overtime_amount,
                "actual_working_days": payroll_record.actual_working_days,
                "total_hours_worked": payroll_record.total_hours_worked,
                "status": payroll_record.status.value
            },
            "message": "Payroll generated successfully",
            "message_ar": "تم إنشاء كشف الراتب بنجاح"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating payroll: {str(e)}"
        )

@router.get("/payroll/summary", response_model=Dict[str, Any])
async def get_payroll_summary(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get payroll summary for a specific month.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: ملخص الرواتب للشهر المحدد
    """
    try:
        summary = HRService.get_payroll_summary(db, month, year)
        
        return {
            "success": True,
            "data": summary,
            "message": "Payroll summary retrieved successfully",
            "message_ar": "تم جلب ملخص الرواتب بنجاح"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving payroll summary: {str(e)}"
        )

# Performance Review Endpoints
@router.post("/performance/review", response_model=Dict[str, Any])
async def create_performance_review(
    review_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a performance review for an employee.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: إنشاء تقييم أداء للموظف
    """
    try:
        # Get employee ID from current user
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee profile not found for current user"
            )
        
        # Convert string dates to date objects
        if isinstance(review_data.get("review_period_start"), str):
            review_data["review_period_start"] = datetime.fromisoformat(review_data["review_period_start"]).date()
        if isinstance(review_data.get("review_period_end"), str):
            review_data["review_period_end"] = datetime.fromisoformat(review_data["review_period_end"]).date()
        if isinstance(review_data.get("review_date"), str):
            review_data["review_date"] = datetime.fromisoformat(review_data["review_date"]).date()
        
        performance_review = HRService.create_performance_review(
            db, review_data["employee_id"], review_data, employee.id
        )
        
        return {
            "success": True,
            "data": {
                "id": performance_review.id,
                "employee_id": performance_review.employee_id,
                "review_type": performance_review.review_type,
                "overall_rating": performance_review.overall_rating,
                "review_date": performance_review.review_date.isoformat(),
                "is_completed": performance_review.is_completed,
                "salary_increase_recommended": performance_review.salary_increase_recommended,
                "recommended_increase_percentage": performance_review.recommended_increase_percentage
            },
            "message": "Performance review created successfully",
            "message_ar": "تم إنشاء تقييم الأداء بنجاح"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating performance review: {str(e)}"
        )

# Department Analytics Endpoints
@router.get("/analytics/department/{department_id}", response_model=Dict[str, Any])
async def get_department_analytics(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive analytics for a specific department.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: تحليلات شاملة للقسم المحدد
    """
    try:
        analytics = HRService.get_department_analytics(db, department_id)
        
        return {
            "success": True,
            "data": analytics,
            "message": "Department analytics retrieved successfully",
            "message_ar": "تم جلب تحليلات القسم بنجاح"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving department analytics: {str(e)}"
        )

# Mock Data Endpoints for Testing
@router.get("/mock-data/dashboard", response_model=Dict[str, Any])
async def get_mock_hr_dashboard():
    """
    Get mock HR dashboard data for testing purposes.
    
    **TSH ERP HR Management System - Phase 3 Implementation**
    
    **Arabic**: بيانات تجريبية للوحة تحكم الموارد البشرية
    """
    return {
        "success": True,
        "data": {
            "total_employees": 19,
            "active_employees": 18,
            "new_hires_month": 2,
            "terminations_month": 1,
            "attendance_rate": 92.5,
            "late_arrivals_today": 3,
            "pending_leave_requests": 5,
            "total_payroll_amount": 850000000.0,  # 850M IQD
            "average_salary": 47222222.0,  # ~47M IQD
            "departments": {
                "sales": {"employees": 12, "attendance_rate": 94.2},
                "warehouse": {"employees": 4, "attendance_rate": 89.1},
                "admin": {"employees": 3, "attendance_rate": 96.7}
            },
            "performance_metrics": {
                "average_rating": 4.2,
                "completed_reviews": 15,
                "pending_reviews": 4
            },
            "payroll_breakdown": {
                "total_gross": 950000000.0,  # 950M IQD
                "total_deductions": 100000000.0,  # 100M IQD
                "total_net": 850000000.0,  # 850M IQD
                "overtime_cost": 50000000.0  # 50M IQD
            },
            "system_status": {
                "hr_system": "operational",
                "payroll_system": "operational",
                "attendance_system": "operational",
                "performance_system": "operational"
            },
            "last_updated": datetime.now().isoformat()
        },
        "message": "Mock HR dashboard data retrieved successfully",
        "message_ar": "تم جلب البيانات التجريبية للوحة تحكم الموارد البشرية بنجاح"
    } 