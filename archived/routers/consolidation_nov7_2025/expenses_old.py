from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.expense import Expense, ExpenseItem, ExpenseAttachment
from app.models.expense import ExpenseStatusEnum, ExpenseCategoryEnum, ExpensePaymentMethodEnum
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

router = APIRouter()

# Pydantic schemas for API responses
class ExpenseResponse(BaseModel):
    id: int
    expense_number: str
    title: str
    description: Optional[str]
    category: ExpenseCategoryEnum
    amount: Decimal
    total_amount: Decimal
    expense_date: datetime
    status: ExpenseStatusEnum
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExpenseItemResponse(BaseModel):
    id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    
    class Config:
        from_attributes = True

class ExpenseDetailResponse(ExpenseResponse):
    expense_items: List[ExpenseItemResponse] = []
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ExpenseStatusEnum] = None,
    category: Optional[ExpenseCategoryEnum] = None,
    db: Session = Depends(get_db)
):
    """Get all expenses with optional filtering"""
    query = db.query(Expense)
    
    if status:
        query = query.filter(Expense.status == status)
    if category:
        query = query.filter(Expense.category == category)
    
    expenses = query.offset(skip).limit(limit).all()
    return expenses

@router.get("/{expense_id}", response_model=ExpenseDetailResponse)
async def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Get a specific expense by ID"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense

@router.get("/categories/list")
async def get_expense_categories():
    """Get all available expense categories"""
    return [
        {"value": category.value, "label": category.value.replace("_", " ").title()}
        for category in ExpenseCategoryEnum
    ]

@router.get("/status/list")
async def get_expense_statuses():
    """Get all available expense statuses"""
    return [
        {"value": status.value, "label": status.value.replace("_", " ").title()}
        for status in ExpenseStatusEnum
    ]

@router.get("/payment-methods/list")
async def get_payment_methods():
    """Get all available payment methods"""
    return [
        {"value": method.value, "label": method.value.replace("_", " ").title()}
        for method in ExpensePaymentMethodEnum
    ]
