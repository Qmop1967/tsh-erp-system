#!/usr/bin/env python3
"""
Create demo branches for TSH ERP System
إنشاء فروع تجريبية لنظام TSH ERP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.branch import Branch
from datetime import datetime

def create_demo_branches():
    """Create demo branches"""
    db = next(get_db())
    
    try:
        branches_data = [
            {
                "name": "فرع بغداد الرئيسي",
                "name_ar": "فرع بغداد الرئيسي",
                "name_en": "Baghdad Main Branch",
                "branch_code": "BGD-001",
                "location": "Baghdad, Iraq",
                "address_ar": "الكرادة، شارع أبو نواس، بغداد، العراق",
                "address_en": "Karrada, Abu Nawas Street, Baghdad, Iraq",
                "phone": "+964-1-7765432",
                "email": "baghdad@tsh.com",
                "branch_type": "MAIN_BRANCH",
                "is_active": True
            },
            {
                "name": "فرع البصرة",
                "name_ar": "فرع البصرة",
                "name_en": "Basra Branch", 
                "branch_code": "BSR-001",
                "location": "Basra, Iraq",
                "address_ar": "الحارثية، البصرة، العراق",
                "address_en": "Al-Hartha, Basra, Iraq",
                "phone": "+964-40-123456",
                "email": "basra@tsh.com",
                "branch_type": "REGIONAL_BRANCH",
                "is_active": True
            },
            {
                "name": "فرع أربيل",
                "name_ar": "فرع أربيل",
                "name_en": "Erbil Branch",
                "branch_code": "ERB-001", 
                "location": "Erbil, Kurdistan Region",
                "address_ar": "أربيل، إقليم كردستان، العراق",
                "address_en": "Erbil, Kurdistan Region, Iraq",
                "phone": "+964-66-234567",
                "email": "erbil@tsh.com",
                "branch_type": "REGIONAL_BRANCH",
                "is_active": True
            },
            {
                "name": "فرع النجف",
                "name_ar": "فرع النجف",
                "name_en": "Najaf Branch",
                "branch_code": "NJF-001",
                "location": "Najaf, Iraq",
                "address_ar": "النجف الأشرف، العراق",
                "address_en": "Najaf Al-Ashraf, Iraq", 
                "phone": "+964-33-345678",
                "email": "najaf@tsh.com",
                "branch_type": "REGIONAL_BRANCH",
                "is_active": True
            }
        ]
        
        created_count = 0
        
        for branch_data in branches_data:
            # Check if branch already exists
            existing_branch = db.query(Branch).filter(Branch.branch_code == branch_data["branch_code"]).first()
            if existing_branch:
                print(f"⚠️  Branch {branch_data['branch_code']} already exists, skipping...")
                continue
            
            try:
                new_branch = Branch(
                    name=branch_data["name"],
                    name_ar=branch_data["name_ar"],
                    name_en=branch_data["name_en"],
                    branch_code=branch_data["branch_code"],
                    location=branch_data["location"],
                    address_ar=branch_data["address_ar"],
                    address_en=branch_data["address_en"],
                    phone=branch_data["phone"],
                    email=branch_data["email"],
                    branch_type=branch_data["branch_type"],
                    is_active=branch_data["is_active"],
                    created_at=datetime.utcnow()
                )
                
                db.add(new_branch)
                db.commit()
                db.refresh(new_branch)
                
                print(f"✅ Created branch: {branch_data['name']} ({branch_data['branch_code']})")
                created_count += 1
                
            except Exception as e:
                print(f"❌ Error creating branch {branch_data['name']}: {str(e)}")
                db.rollback()
                continue
        
        print(f"\n🎉 Successfully created {created_count} demo branches!")
        print(f"📈 Total branches: {db.query(Branch).count()}")
        
    except Exception as e:
        print(f"❌ Error creating demo branches: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating Demo Branches for TSH ERP System...")
    create_demo_branches()
    print("✨ Demo branch creation completed!") 