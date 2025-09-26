"""Add comprehensive HR management models

Revision ID: 700e3f25897c
Revises: 077db8bc0e4f
Create Date: 2025-07-06 18:52:21.282105

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '700e3f25897c'
down_revision = '077db8bc0e4f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tables in order that avoids circular dependencies
    
    # 1. Create positions table (independent)
    op.create_table('positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('title_ar', sa.String(length=100), nullable=False),
        sa.Column('title_en', sa.String(length=100), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=True),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('min_salary', sa.Float(), nullable=False),
        sa.Column('max_salary', sa.Float(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_positions_code'), 'positions', ['code'], unique=True)
    op.create_index(op.f('ix_positions_id'), 'positions', ['id'], unique=False)
    op.create_index(op.f('ix_positions_title_ar'), 'positions', ['title_ar'], unique=False)
    op.create_index(op.f('ix_positions_title_en'), 'positions', ['title_en'], unique=False)
    
    # 2. Create departments table (without head_employee_id foreign key initially)
    op.create_table('departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name_ar', sa.String(length=100), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('description_ar', sa.Text(), nullable=True),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('head_employee_id', sa.Integer(), nullable=True),
        sa.Column('monthly_budget', sa.Float(), nullable=True),
        sa.Column('annual_budget', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_departments_code'), 'departments', ['code'], unique=True)
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)
    op.create_index(op.f('ix_departments_name_ar'), 'departments', ['name_ar'], unique=False)
    op.create_index(op.f('ix_departments_name_en'), 'departments', ['name_en'], unique=False)
    
    # 3. Create employees table (without direct_manager_id foreign key initially)
    op.create_table('employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_code', sa.String(length=20), nullable=False),
        sa.Column('first_name_ar', sa.String(length=100), nullable=False),
        sa.Column('first_name_en', sa.String(length=100), nullable=False),
        sa.Column('last_name_ar', sa.String(length=100), nullable=False),
        sa.Column('last_name_en', sa.String(length=100), nullable=False),
        sa.Column('full_name_ar', sa.String(length=200), nullable=False),
        sa.Column('full_name_en', sa.String(length=200), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('emergency_contact', sa.String(length=20), nullable=True),
        sa.Column('address_ar', sa.Text(), nullable=True),
        sa.Column('address_en', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('position_id', sa.Integer(), nullable=False),
        sa.Column('direct_manager_id', sa.Integer(), nullable=True),
        sa.Column('employment_status', sa.Enum('ACTIVE', 'INACTIVE', 'TERMINATED', 'ON_LEAVE', name='employmentstatus'), nullable=False),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('base_salary', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('is_commission_eligible', sa.Boolean(), nullable=False),
        sa.Column('commission_rate', sa.Float(), nullable=False),
        sa.Column('working_hours_per_day', sa.Float(), nullable=False),
        sa.Column('working_days_per_week', sa.Integer(), nullable=False),
        sa.Column('profile_photo_url', sa.String(length=500), nullable=True),
        sa.Column('national_id', sa.String(length=50), nullable=True),
        sa.Column('passport_number', sa.String(length=50), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('marital_status', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('national_id'),
        sa.UniqueConstraint('passport_number')
    )
    op.create_index(op.f('ix_employees_email'), 'employees', ['email'], unique=True)
    op.create_index(op.f('ix_employees_employee_code'), 'employees', ['employee_code'], unique=True)
    op.create_index(op.f('ix_employees_full_name_ar'), 'employees', ['full_name_ar'], unique=False)
    op.create_index(op.f('ix_employees_full_name_en'), 'employees', ['full_name_en'], unique=False)
    op.create_index(op.f('ix_employees_id'), 'employees', ['id'], unique=False)
    
    # 4. Add foreign key constraints for circular dependencies
    op.create_foreign_key('fk_employees_direct_manager', 'employees', 'employees', ['direct_manager_id'], ['id'])
    op.create_foreign_key('fk_departments_head_employee', 'departments', 'employees', ['head_employee_id'], ['id'])
    
    # 5. Create remaining HR tables
    op.create_table('hr_dashboard_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('total_employees', sa.Integer(), nullable=True),
        sa.Column('active_employees', sa.Integer(), nullable=True),
        sa.Column('new_hires_month', sa.Integer(), nullable=True),
        sa.Column('terminations_month', sa.Integer(), nullable=True),
        sa.Column('average_attendance_rate', sa.Float(), nullable=True),
        sa.Column('total_late_arrivals', sa.Integer(), nullable=True),
        sa.Column('total_overtime_hours', sa.Float(), nullable=True),
        sa.Column('pending_leave_requests', sa.Integer(), nullable=True),
        sa.Column('approved_leaves_month', sa.Integer(), nullable=True),
        sa.Column('total_payroll_amount', sa.Float(), nullable=True),
        sa.Column('average_salary', sa.Float(), nullable=True),
        sa.Column('total_overtime_cost', sa.Float(), nullable=True),
        sa.Column('pending_reviews', sa.Integer(), nullable=True),
        sa.Column('completed_reviews_month', sa.Integer(), nullable=True),
        sa.Column('average_performance_rating', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hr_dashboard_metrics_id'), 'hr_dashboard_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_hr_dashboard_metrics_metric_date'), 'hr_dashboard_metrics', ['metric_date'], unique=False)
    
    op.create_table('attendance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('check_in_time', sa.DateTime(), nullable=True),
        sa.Column('check_out_time', sa.DateTime(), nullable=True),
        sa.Column('check_in_latitude', sa.Float(), nullable=True),
        sa.Column('check_in_longitude', sa.Float(), nullable=True),
        sa.Column('check_out_latitude', sa.Float(), nullable=True),
        sa.Column('check_out_longitude', sa.Float(), nullable=True),
        sa.Column('check_in_location', sa.String(length=200), nullable=True),
        sa.Column('check_out_location', sa.String(length=200), nullable=True),
        sa.Column('total_hours', sa.Float(), nullable=True),
        sa.Column('regular_hours', sa.Float(), nullable=True),
        sa.Column('overtime_hours', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('PRESENT', 'ABSENT', 'LATE', 'HALF_DAY', 'OVERTIME', name='attendancestatus'), nullable=False),
        sa.Column('is_late', sa.Boolean(), nullable=True),
        sa.Column('late_minutes', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('manager_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attendance_records_date'), 'attendance_records', ['date'], unique=False)
    op.create_index(op.f('ix_attendance_records_id'), 'attendance_records', ['id'], unique=False)
    
    op.create_table('leave_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('leave_type', sa.Enum('ANNUAL', 'SICK', 'MATERNITY', 'PATERNITY', 'EMERGENCY', 'UNPAID', name='leavetype'), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('total_days', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('supporting_documents', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', name='leavestatus'), nullable=False),
        sa.Column('requested_by', sa.Integer(), nullable=False),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('request_date', sa.DateTime(), nullable=False),
        sa.Column('review_date', sa.DateTime(), nullable=True),
        sa.Column('approval_date', sa.DateTime(), nullable=True),
        sa.Column('employee_comments', sa.Text(), nullable=True),
        sa.Column('manager_comments', sa.Text(), nullable=True),
        sa.Column('hr_comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['requested_by'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_requests_id'), 'leave_requests', ['id'], unique=False)
    
    op.create_table('performance_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('review_period_start', sa.Date(), nullable=False),
        sa.Column('review_period_end', sa.Date(), nullable=False),
        sa.Column('review_type', sa.String(length=50), nullable=False),
        sa.Column('overall_rating', sa.Float(), nullable=False),
        sa.Column('technical_skills', sa.Float(), nullable=True),
        sa.Column('communication_skills', sa.Float(), nullable=True),
        sa.Column('teamwork', sa.Float(), nullable=True),
        sa.Column('leadership', sa.Float(), nullable=True),
        sa.Column('punctuality', sa.Float(), nullable=True),
        sa.Column('productivity', sa.Float(), nullable=True),
        sa.Column('goals_achieved', sa.Text(), nullable=True),
        sa.Column('goals_missed', sa.Text(), nullable=True),
        sa.Column('new_goals', sa.Text(), nullable=True),
        sa.Column('employee_self_assessment', sa.Text(), nullable=True),
        sa.Column('manager_feedback', sa.Text(), nullable=True),
        sa.Column('hr_comments', sa.Text(), nullable=True),
        sa.Column('development_plan', sa.Text(), nullable=True),
        sa.Column('salary_increase_recommended', sa.Boolean(), nullable=True),
        sa.Column('recommended_increase_amount', sa.Float(), nullable=True),
        sa.Column('recommended_increase_percentage', sa.Float(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('employee_acknowledged', sa.Boolean(), nullable=True),
        sa.Column('review_date', sa.Date(), nullable=False),
        sa.Column('employee_acknowledgment_date', sa.DateTime(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=False),
        sa.Column('hr_reviewed_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['hr_reviewed_by'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performance_reviews_id'), 'performance_reviews', ['id'], unique=False)
    
    op.create_table('payroll_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('payroll_month', sa.Integer(), nullable=False),
        sa.Column('payroll_year', sa.Integer(), nullable=False),
        sa.Column('pay_period_start', sa.Date(), nullable=False),
        sa.Column('pay_period_end', sa.Date(), nullable=False),
        sa.Column('base_salary', sa.Float(), nullable=False),
        sa.Column('commission_amount', sa.Float(), nullable=False),
        sa.Column('overtime_amount', sa.Float(), nullable=False),
        sa.Column('bonus_amount', sa.Float(), nullable=False),
        sa.Column('allowances', sa.Float(), nullable=False),
        sa.Column('gross_salary', sa.Float(), nullable=False),
        sa.Column('tax_deduction', sa.Float(), nullable=False),
        sa.Column('social_security', sa.Float(), nullable=False),
        sa.Column('insurance_deduction', sa.Float(), nullable=False),
        sa.Column('loan_deduction', sa.Float(), nullable=False),
        sa.Column('other_deductions', sa.Float(), nullable=False),
        sa.Column('total_deductions', sa.Float(), nullable=False),
        sa.Column('net_salary', sa.Float(), nullable=False),
        sa.Column('working_days', sa.Integer(), nullable=False),
        sa.Column('actual_working_days', sa.Integer(), nullable=False),
        sa.Column('total_hours_worked', sa.Float(), nullable=False),
        sa.Column('overtime_hours', sa.Float(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('bank_account', sa.String(length=50), nullable=True),
        sa.Column('payment_date', sa.Date(), nullable=True),
        sa.Column('payment_reference', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSED', 'PAID', 'CANCELLED', name='payrollstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payroll_records_id'), 'payroll_records', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_payroll_records_id'), table_name='payroll_records')
    op.drop_table('payroll_records')
    op.drop_index(op.f('ix_performance_reviews_id'), table_name='performance_reviews')
    op.drop_table('performance_reviews')
    op.drop_index(op.f('ix_leave_requests_id'), table_name='leave_requests')
    op.drop_table('leave_requests')
    op.drop_index(op.f('ix_attendance_records_id'), table_name='attendance_records')
    op.drop_index(op.f('ix_attendance_records_date'), table_name='attendance_records')
    op.drop_table('attendance_records')
    op.drop_index(op.f('ix_hr_dashboard_metrics_metric_date'), table_name='hr_dashboard_metrics')
    op.drop_index(op.f('ix_hr_dashboard_metrics_id'), table_name='hr_dashboard_metrics')
    op.drop_table('hr_dashboard_metrics')
    
    # Drop foreign key constraints for circular dependencies
    op.drop_constraint('fk_departments_head_employee', 'departments', type_='foreignkey')
    op.drop_constraint('fk_employees_direct_manager', 'employees', type_='foreignkey')
    
    op.drop_index(op.f('ix_employees_id'), table_name='employees')
    op.drop_index(op.f('ix_employees_full_name_en'), table_name='employees')
    op.drop_index(op.f('ix_employees_full_name_ar'), table_name='employees')
    op.drop_index(op.f('ix_employees_employee_code'), table_name='employees')
    op.drop_index(op.f('ix_employees_email'), table_name='employees')
    op.drop_table('employees')
    op.drop_index(op.f('ix_departments_name_en'), table_name='departments')
    op.drop_index(op.f('ix_departments_name_ar'), table_name='departments')
    op.drop_index(op.f('ix_departments_id'), table_name='departments')
    op.drop_index(op.f('ix_departments_code'), table_name='departments')
    op.drop_table('departments')
    op.drop_index(op.f('ix_positions_title_en'), table_name='positions')
    op.drop_index(op.f('ix_positions_title_ar'), table_name='positions')
    op.drop_index(op.f('ix_positions_id'), table_name='positions')
    op.drop_index(op.f('ix_positions_code'), table_name='positions')
    op.drop_table('positions') 