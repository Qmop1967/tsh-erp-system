"""
Create an admin user for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.branch import Branch
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """Create an admin user for testing"""
    db = SessionLocal()
    
    try:
        # Check if admin role exists
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            print("Creating Admin role...")
            admin_role = Role(
                name="Admin",
                description="System Administrator",
                is_active=True
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"✅ Created Admin role with ID: {admin_role.id}")
        else:
            print(f"✅ Admin role already exists with ID: {admin_role.id}")
        
        # Check if main branch exists
        main_branch = db.query(Branch).filter(Branch.branch_code == "MAIN").first()
        if not main_branch:
            print("Creating Main branch...")
            main_branch = Branch(
                name="Main Branch",
                branch_code="MAIN",
                address="Baghdad, Iraq",
                is_active=True
            )
            db.add(main_branch)
            db.commit()
            db.refresh(main_branch)
            print(f"✅ Created Main branch with ID: {main_branch.id}")
        else:
            print(f"✅ Main branch already exists with ID: {main_branch.id}")
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@tsh.sale").first()
        if not admin_user:
            print("Creating admin user...")
            hashed_password = pwd_context.hash("admin123")
            admin_user = User(
                name="System Administrator",
                email="admin@tsh.sale",
                password=hashed_password,  # Some models expect 'password' field
                password_hash=hashed_password,
                role_id=admin_role.id,
                branch_id=main_branch.id,
                employee_code="ADMIN001",
                phone="+964-770-000-0000",
                is_active=True,
                is_salesperson=False
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Created admin user with ID: {admin_user.id}")
            print(f"   Email: admin@tsh.sale")
            print(f"   Password: admin123")
        else:
            print(f"✅ Admin user already exists with ID: {admin_user.id}")
            print(f"   Email: {admin_user.email}")
        
        print("\n🎉 Admin user setup complete!")
        print("   You can now login with:")
        print("   Email: admin@tsh.sale")
        print("   Password: admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
