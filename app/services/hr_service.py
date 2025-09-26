from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

from app.models.hr import (
    Employee, Department, Position, PayrollRecord, AttendanceRecord,
    LeaveRequest, PerformanceReview, HRDashboardMetrics,
    EmploymentStatus, PayrollStatus, LeaveType, LeaveStatus, AttendanceStatus
)
from app.models.user import User


class HRService:
    
    @staticmethod
    def get_employee_dashboard_metrics(db: Session, date_filter: Optional[date] = None) -> Dict[str, Any]:
        """Get HR dashboard metrics for the specified date"""
        if not date_filter:
            date_filter = date.today()
        
        # Employee Metrics
        total_employees = db.query(Employee).filter(Employee.is_active.is_(True)).count()
        active_employees = db.query(Employee).filter(
            Employee.employment_status == EmploymentStatus.ACTIVE
        ).count()
        
        # New hires this month
        start_of_month = date_filter.replace(day=1)
        new_hires_month = db.query(Employee).filter(
            Employee.hire_date >= start_of_month,
            Employee.hire_date <= date_filter
        ).count()
        
        # Terminations this month
        terminations_month = db.query(Employee).filter(
            Employee.termination_date >= start_of_month,
            Employee.termination_date <= date_filter
        ).count()
        
        # Attendance Metrics
        attendance_today = db.query(AttendanceRecord).filter(
            AttendanceRecord.date == date_filter
        ).all()
        
        total_attendance_today = len(attendance_today)
        late_arrivals_today = len([a for a in attendance_today if a.is_late])
        
        attendance_rate = (total_attendance_today / active_employees * 100) if active_employees > 0 else 0
        
        # Leave Metrics
        pending_leaves = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.PENDING
        ).count()
        
        # Payroll Metrics
        current_month = date_filter.month
        current_year = date_filter.year
        
        current_payroll = db.query(PayrollRecord).filter(
            PayrollRecord.payroll_month == current_month,
            PayrollRecord.payroll_year == current_year
        ).all()
        
        total_payroll_amount = sum([p.net_salary for p in current_payroll])
        average_salary = total_payroll_amount / len(current_payroll) if current_payroll else 0
        
        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "new_hires_month": new_hires_month,
            "terminations_month": terminations_month,
            "attendance_rate": round(attendance_rate, 2),
            "late_arrivals_today": late_arrivals_today,
            "pending_leave_requests": pending_leaves,
            "total_payroll_amount": total_payroll_amount,
            "average_salary": average_salary,
            "last_updated": datetime.now()
        }
    
    @staticmethod
    def create_employee(db: Session, employee_data: Dict[str, Any], created_by: int) -> Employee:
        """Create a new employee record"""
        
        # Generate employee code if not provided
        if not employee_data.get("employee_code"):
            last_employee = db.query(Employee).order_by(desc(Employee.id)).first()
            next_id = (last_employee.id + 1) if last_employee else 1
            employee_data["employee_code"] = f"EMP{next_id:04d}"
        
        # Create full names
        employee_data["full_name_ar"] = f"{employee_data['first_name_ar']} {employee_data['last_name_ar']}"
        employee_data["full_name_en"] = f"{employee_data['first_name_en']} {employee_data['last_name_en']}"
        
        employee_data["created_by"] = created_by
        
        employee = Employee(**employee_data)
        db.add(employee)
        db.commit()
        db.refresh(employee)
        
        return employee
    
    @staticmethod
    def get_employees(
        db: Session, 
        department_id: Optional[int] = None,
        position_id: Optional[int] = None,
        employment_status: Optional[EmploymentStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """Get employees with filters"""
        
        query = db.query(Employee).filter(Employee.is_active == True)
        
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        if position_id:
            query = query.filter(Employee.position_id == position_id)
        
        if employment_status:
            query = query.filter(Employee.employment_status == employment_status)
        
        if search:
            query = query.filter(
                or_(
                    Employee.full_name_en.contains(search),
                    Employee.full_name_ar.contains(search),
                    Employee.email.contains(search),
                    Employee.employee_code.contains(search)
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def process_attendance(
        db: Session, 
        employee_id: int, 
        action: str,  # "check_in" or "check_out"
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location: Optional[str] = None,
        notes: Optional[str] = None
    ) -> AttendanceRecord:
        """Process employee check-in or check-out"""
        
        today = date.today()
        now = datetime.now()
        
        # Get or create today's attendance record
        attendance = db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.date == today
        ).first()
        
        if not attendance:
            attendance = AttendanceRecord(
                employee_id=employee_id,
                date=today,
                status=AttendanceStatus.PRESENT
            )
            db.add(attendance)
        
        # Get employee working schedule
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        
        if action == "check_in":
            attendance.check_in_time = now
            attendance.check_in_latitude = latitude
            attendance.check_in_longitude = longitude
            attendance.check_in_location = location
            
            # Check if late (assuming 8:00 AM start time)
            expected_start = datetime.combine(today, datetime.min.time().replace(hour=8))
            if now > expected_start:
                attendance.is_late = True
                attendance.late_minutes = int((now - expected_start).total_seconds() / 60)
        
        elif action == "check_out":
            attendance.check_out_time = now
            attendance.check_out_latitude = latitude
            attendance.check_out_longitude = longitude
            attendance.check_out_location = location
            
            # Calculate hours worked
            if attendance.check_in_time:
                total_seconds = (now - attendance.check_in_time).total_seconds()
                attendance.total_hours = round(total_seconds / 3600, 2)
                
                # Calculate regular and overtime hours
                regular_hours = min(attendance.total_hours, employee.working_hours_per_day)
                attendance.regular_hours = regular_hours
                attendance.overtime_hours = max(0, attendance.total_hours - employee.working_hours_per_day)
        
        if notes:
            attendance.notes = notes
        
        db.commit()
        db.refresh(attendance)
        
        return attendance
    
    @staticmethod
    def create_leave_request(
        db: Session,
        employee_id: int,
        leave_data: Dict[str, Any]
    ) -> LeaveRequest:
        """Create a new leave request"""
        
        # Calculate total days
        start_date = leave_data["start_date"]
        end_date = leave_data["end_date"]
        total_days = (end_date - start_date).days + 1
        
        leave_request = LeaveRequest(
            employee_id=employee_id,
            leave_type=LeaveType(leave_data["leave_type"]),
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            reason=leave_data["reason"],
            supporting_documents=json.dumps(leave_data.get("supporting_documents", [])),
            employee_comments=leave_data.get("employee_comments"),
            requested_by=employee_id
        )
        
        db.add(leave_request)
        db.commit()
        db.refresh(leave_request)
        
        return leave_request
    
    @staticmethod
    def approve_leave_request(
        db: Session,
        leave_request_id: int,
        approved_by: int,
        manager_comments: Optional[str] = None
    ) -> LeaveRequest:
        """Approve a leave request"""
        
        leave_request = db.query(LeaveRequest).filter(
            LeaveRequest.id == leave_request_id
        ).first()
        
        if not leave_request:
            raise ValueError("Leave request not found")
        
        leave_request.status = LeaveStatus.APPROVED
        leave_request.approved_by = approved_by
        leave_request.approval_date = datetime.now()
        leave_request.manager_comments = manager_comments
        
        db.commit()
        db.refresh(leave_request)
        
        return leave_request
    
    @staticmethod
    def generate_payroll(
        db: Session,
        employee_id: int,
        payroll_month: int,
        payroll_year: int,
        created_by: int
    ) -> PayrollRecord:
        """Generate payroll for an employee for a specific month"""
        
        # Check if payroll already exists
        existing_payroll = db.query(PayrollRecord).filter(
            PayrollRecord.employee_id == employee_id,
            PayrollRecord.payroll_month == payroll_month,
            PayrollRecord.payroll_year == payroll_year
        ).first()
        
        if existing_payroll:
            raise ValueError("Payroll already exists for this period")
        
        # Get employee details
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise ValueError("Employee not found")
        
        # Calculate pay period
        pay_period_start = date(payroll_year, payroll_month, 1)
        if payroll_month == 12:
            pay_period_end = date(payroll_year + 1, 1, 1) - timedelta(days=1)
        else:
            pay_period_end = date(payroll_year, payroll_month + 1, 1) - timedelta(days=1)
        
        # Get attendance records for the month
        attendance_records = db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.date >= pay_period_start,
            AttendanceRecord.date <= pay_period_end
        ).all()
        
        total_working_days = len([a for a in attendance_records if a.status == AttendanceStatus.PRESENT])
        total_hours_worked = sum([a.total_hours or 0 for a in attendance_records])
        overtime_hours = sum([a.overtime_hours or 0 for a in attendance_records])
        
        # Calculate earnings
        base_salary = employee.base_salary
        overtime_rate = base_salary / (employee.working_hours_per_day * employee.working_days_per_week * 4.33) * 1.5
        overtime_amount = overtime_hours * overtime_rate
        
        # Calculate commission if applicable
        commission_amount = 0.0
        if employee.is_commission_eligible:
            # This would need integration with sales data
            # For now, we'll use a placeholder
            commission_amount = 0.0
        
        gross_salary = base_salary + overtime_amount + commission_amount
        
        # Calculate deductions (simplified)
        tax_deduction = gross_salary * 0.10  # 10% tax
        social_security = gross_salary * 0.05  # 5% social security
        total_deductions = tax_deduction + social_security
        
        net_salary = gross_salary - total_deductions
        
        payroll_record = PayrollRecord(
            employee_id=employee_id,
            payroll_month=payroll_month,
            payroll_year=payroll_year,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            base_salary=base_salary,
            commission_amount=commission_amount,
            overtime_amount=overtime_amount,
            gross_salary=gross_salary,
            tax_deduction=tax_deduction,
            social_security=social_security,
            total_deductions=total_deductions,
            net_salary=net_salary,
            working_days=employee.working_days_per_week * 4,  # Approximate monthly working days
            actual_working_days=total_working_days,
            total_hours_worked=total_hours_worked,
            overtime_hours=overtime_hours,
            created_by=created_by
        )
        
        db.add(payroll_record)
        db.commit()
        db.refresh(payroll_record)
        
        return payroll_record
    
    @staticmethod
    def create_performance_review(
        db: Session,
        employee_id: int,
        review_data: Dict[str, Any],
        reviewed_by: int
    ) -> PerformanceReview:
        """Create a performance review for an employee"""
        
        performance_review = PerformanceReview(
            employee_id=employee_id,
            review_period_start=review_data["review_period_start"],
            review_period_end=review_data["review_period_end"],
            review_type=review_data["review_type"],
            overall_rating=review_data["overall_rating"],
            technical_skills=review_data.get("technical_skills", 0.0),
            communication_skills=review_data.get("communication_skills", 0.0),
            teamwork=review_data.get("teamwork", 0.0),
            leadership=review_data.get("leadership", 0.0),
            punctuality=review_data.get("punctuality", 0.0),
            productivity=review_data.get("productivity", 0.0),
            goals_achieved=review_data.get("goals_achieved"),
            goals_missed=review_data.get("goals_missed"),
            new_goals=review_data.get("new_goals"),
            employee_self_assessment=review_data.get("employee_self_assessment"),
            manager_feedback=review_data.get("manager_feedback"),
            development_plan=review_data.get("development_plan"),
            salary_increase_recommended=review_data.get("salary_increase_recommended", False),
            recommended_increase_amount=review_data.get("recommended_increase_amount", 0.0),
            recommended_increase_percentage=review_data.get("recommended_increase_percentage", 0.0),
            review_date=review_data["review_date"],
            reviewed_by=reviewed_by
        )
        
        db.add(performance_review)
        db.commit()
        db.refresh(performance_review)
        
        return performance_review
    
    @staticmethod
    def get_department_analytics(db: Session, department_id: int) -> Dict[str, Any]:
        """Get analytics for a specific department"""
        
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise ValueError("Department not found")
        
        employees = db.query(Employee).filter(
            Employee.department_id == department_id,
            Employee.is_active == True
        ).all()
        
        total_employees = len(employees)
        
        # Calculate average salary
        total_salary = sum([emp.base_salary for emp in employees])
        average_salary = total_salary / total_employees if total_employees > 0 else 0
        
        # Get recent performance reviews
        recent_reviews = db.query(PerformanceReview).join(Employee).filter(
            Employee.department_id == department_id,
            PerformanceReview.review_date >= date.today() - timedelta(days=365)
        ).all()
        
        average_performance = sum([r.overall_rating for r in recent_reviews]) / len(recent_reviews) if recent_reviews else 0
        
        # Get attendance rate for the department
        today = date.today()
        month_start = today.replace(day=1)
        
        attendance_records = db.query(AttendanceRecord).join(Employee).filter(
            Employee.department_id == department_id,
            AttendanceRecord.date >= month_start,
            AttendanceRecord.date <= today
        ).all()
        
        total_attendance = len(attendance_records)
        expected_attendance = total_employees * (today - month_start).days
        attendance_rate = (total_attendance / expected_attendance * 100) if expected_attendance > 0 else 0
        
        return {
            "department_name": department.name_en,
            "total_employees": total_employees,
            "average_salary": average_salary,
            "total_monthly_cost": total_salary,
            "average_performance_rating": round(average_performance, 2),
            "attendance_rate": round(attendance_rate, 2),
            "budget_utilization": (total_salary / department.monthly_budget * 100) if department.monthly_budget > 0 else 0
        }
    
    @staticmethod
    def get_payroll_summary(db: Session, month: int, year: int) -> Dict[str, Any]:
        """Get payroll summary for a specific month"""
        
        payroll_records = db.query(PayrollRecord).filter(
            PayrollRecord.payroll_month == month,
            PayrollRecord.payroll_year == year
        ).all()
        
        total_employees = len(payroll_records)
        total_gross_salary = sum([p.gross_salary for p in payroll_records])
        total_deductions = sum([p.total_deductions for p in payroll_records])
        total_net_salary = sum([p.net_salary for p in payroll_records])
        total_overtime = sum([p.overtime_amount for p in payroll_records])
        
        processed_count = len([p for p in payroll_records if p.status == PayrollStatus.PROCESSED])
        paid_count = len([p for p in payroll_records if p.status == PayrollStatus.PAID])
        
        return {
            "month": month,
            "year": year,
            "total_employees": total_employees,
            "total_gross_salary": total_gross_salary,
            "total_deductions": total_deductions,
            "total_net_salary": total_net_salary,
            "total_overtime": total_overtime,
            "processed_count": processed_count,
            "paid_count": paid_count,
            "pending_count": total_employees - processed_count,
            "average_salary": total_net_salary / total_employees if total_employees > 0 else 0
        } 