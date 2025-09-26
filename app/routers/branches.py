from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.branch import Branch
from app.schemas.branch import BranchCreate, BranchResponse
from app.routers.auth import get_current_user
from app.services.permission_service import simple_require_permission
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[BranchResponse])
@simple_require_permission("branches.view")
def get_branches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """جلب جميع الفروع"""
    branches = db.query(Branch).all()
    return branches

@router.post("/", response_model=BranchResponse)
@simple_require_permission("create_branch")
def create_branch(
    branch: BranchCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """إنشاء فرع جديد"""
    db_branch = Branch(**branch.dict())
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    return db_branch

@router.get("/{branch_id}", response_model=BranchResponse)
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    """جلب فرع محدد"""
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="الفرع غير موجود")
    return branch 