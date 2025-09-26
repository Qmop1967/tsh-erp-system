#!/usr/bin/env python3
"""
Add comprehensive demo employees for TSH ERP System
إضافة موظفين تجريبيين شاملين لنظام TSH ERP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.role import Role
from app.models.branch import Branch
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from datetime import datetime
import random

def generate_employee_code(role_prefix, number):
    """Generate employee code based on role"""
    prefixes = {
        "Travel Salesperson": "TSP",
        "Partner Salesman": "PSM", 
        "Retailerman": "RTM",
        "Admin": "ADM",
        "Manager": "MGR",
        "Employee": "EMP",
        "Accountant": "ACC",
        "HR Specialist": "HRS"
    }
    prefix = prefixes.get(role_prefix, "EMP")
    return f"{prefix}-{number:03d}"

def create_demo_employees():
    """Create comprehensive demo employees"""
    db = next(get_db())
    
    try:
        # Get all roles and branches
        roles = {role.name: role for role in db.query(Role).all()}
        branches = list(db.query(Branch).filter(Branch.is_active == True).all())
        
        if not branches:
            print("❌ No active branches found. Please create branches first.")
            return
        
        # Define employee data for different roles
        employees_data = [
            # Travel Salespersons
            {
                "name": "أحمد السالمي",
                "email": "ahmed.salemi@tsh.com",
                "phone": "+964-770-1234567",
                "role": "Travel Salesperson",
                "is_salesperson": True,
                "employee_code_base": "Travel Salesperson"
            },
            {
                "name": "فاطمة الكاظمي", 
                "email": "fatima.kazemi@tsh.com",
                "phone": "+964-770-2345678",
                "role": "Travel Salesperson",
                "is_salesperson": True,
                "employee_code_base": "Travel Salesperson"
            },
            {
                "name": "محمد الربيعي",
                "email": "mohammed.rabiee@tsh.com", 
                "phone": "+964-770-3456789",
                "role": "Travel Salesperson",
                "is_salesperson": True,
                "employee_code_base": "Travel Salesperson"
            },
            {
                "name": "زينب العلوي",
                "email": "zeinab.alawi@tsh.com",
                "phone": "+964-770-4567890",
                "role": "Travel Salesperson", 
                "is_salesperson": True,
                "employee_code_base": "Travel Salesperson"
            },
            
            # Partner Salesmen
            {
                "name": "عماد الشمري",
                "email": "emad.shamari@tsh.com",
                "phone": "+964-771-1234567",
                "role": "Partner Salesman",
                "is_salesperson": True,
                "employee_code_base": "Partner Salesman"
            },
            {
                "name": "نور الدين محسن",
                "email": "nooraldin.mohsen@tsh.com",
                "phone": "+964-771-2345678", 
                "role": "Partner Salesman",
                "is_salesperson": True,
                "employee_code_base": "Partner Salesman"
            },
            {
                "name": "سعاد الموسوي",
                "email": "suaad.mousawi@tsh.com",
                "phone": "+964-771-3456789",
                "role": "Partner Salesman",
                "is_salesperson": True,
                "employee_code_base": "Partner Salesman"
            },
            
            # Retailermen  
            {
                "name": "خالد البصري",
                "email": "khaled.basri@tsh.com",
                "phone": "+964-772-1234567",
                "role": "Retailerman",
                "is_salesperson": True,
                "employee_code_base": "Retailerman"
            },
            {
                "name": "مريم الأنصاري",
                "email": "mariam.ansari@tsh.com",
                "phone": "+964-772-2345678",
                "role": "Retailerman", 
                "is_salesperson": True,
                "employee_code_base": "Retailerman"
            },
            {
                "name": "يوسف الطائي",
                "email": "yousif.taee@tsh.com",
                "phone": "+964-772-3456789",
                "role": "Retailerman",
                "is_salesperson": True,
                "employee_code_base": "Retailerman"
            },
            
            # Regular Employees
            {
                "name": "عبد الله الحسيني",
                "email": "abdullah.hussaini@tsh.com",
                "phone": "+964-773-1234567",
                "role": "Manager",
                "is_salesperson": False,
                "employee_code_base": "Manager"
            },
            {
                "name": "أسماء الجبوري",
                "email": "asmaa.juboori@tsh.com",
                "phone": "+964-773-2345678",
                "role": "Accountant",
                "is_salesperson": False,
                "employee_code_base": "Accountant"
            },
            {
                "name": "حسام الدليمي",
                "email": "hussam.dalimi@tsh.com",
                "phone": "+964-773-3456789",
                "role": "Employee",
                "is_salesperson": False,
                "employee_code_base": "Employee"
            },
            {
                "name": "رشا النعيمي",
                "email": "rasha.naeemi@tsh.com",
                "phone": "+964-773-4567890",
                "role": "HR Specialist",
                "is_salesperson": False,
                "employee_code_base": "HR Specialist"
            },
            {
                "name": "علي الماجدي",
                "email": "ali.majidi@tsh.com",
                "phone": "+964-774-1234567",
                "role": "Employee",
                "is_salesperson": False,
                "employee_code_base": "Employee"
            },
            {
                "name": "ليلى السلطاني",
                "email": "layla.sultani@tsh.com",
                "phone": "+964-774-2345678",
                "role": "Manager",
                "is_salesperson": False,
                "employee_code_base": "Manager"
            }
        ]
        
        created_count = 0
        role_counters = {}
        
        for emp_data in employees_data:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == emp_data["email"]).first()
            if existing_user:
                print(f"⚠️  User {emp_data['email']} already exists, skipping...")
                continue
            
            # Get role
            role = roles.get(emp_data["role"])
            if not role:
                print(f"❌ Role '{emp_data['role']}' not found, skipping {emp_data['name']}")
                continue
            
            # Generate employee code
            role_key = emp_data["employee_code_base"]
            if role_key not in role_counters:
                role_counters[role_key] = 1
            else:
                role_counters[role_key] += 1
            
            employee_code = generate_employee_code(role_key, role_counters[role_key])
            
            # Random branch assignment
            branch = random.choice(branches)
            
            # Create user
            try:
                # Hash password (default: 123456)
                hashed_password = AuthService.get_password_hash("123456")
                
                new_user = User(
                    name=emp_data["name"],
                    email=emp_data["email"],
                    password=hashed_password,
                    role_id=role.id,
                    branch_id=branch.id,
                    employee_code=employee_code,
                    phone=emp_data["phone"],
                    is_salesperson=emp_data["is_salesperson"],
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                print(f"✅ Created {emp_data['role']}: {emp_data['name']} ({employee_code}) - {branch.name}")
                created_count += 1
                
            except Exception as e:
                print(f"❌ Error creating {emp_data['name']}: {str(e)}")
                db.rollback()
                continue
        
        # Summary
        print(f"\n🎉 Successfully created {created_count} demo employees!")
        
        # Count by role
        print("\n📊 Employee Count by Role:")
        for role_name, role in roles.items():
            count = db.query(User).filter(User.role_id == role.id).count()
            print(f"  • {role_name}: {count}")
        
        print(f"\n📈 Total Employees: {db.query(User).count()}")
        
        # Show login credentials
        print("\n🔑 Login Credentials:")
        print("All employees can login with their email and password: 123456")
        
    except Exception as e:
        print(f"❌ Error creating demo employees: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Adding Demo Employees to TSH ERP System...")
    create_demo_employees()
    print("✨ Demo employee creation completed!") 