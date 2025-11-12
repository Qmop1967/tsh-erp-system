from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.database import get_db
from app.schemas.sales import (
    SalesOrderCreate, SalesOrderUpdate, SalesOrder, SalesOrderSummary
)
from app.services.sales_service import SalesService

router = APIRouter(tags=["sales"])


@router.post("/orders", response_model=SalesOrder, status_code=201)
def create_sales_order(
    sales_order: SalesOrderCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # يجب تنفيذ نظام المصادقة
):
    """إنشاء أمر بيع جديد"""
    # مؤقتاً سنستخدم user_id = 1 حتى يتم تنفيذ نظام المصادقة
    return SalesService.create_sales_order(db, sales_order, created_by=1)


@router.get("/orders", response_model=List[SalesOrder])
def get_sales_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="حالة الأمر"),
    customer_id: Optional[int] = Query(None, description="معرف العميل"),
    date_from: Optional[date] = Query(None, description="من تاريخ"),
    date_to: Optional[date] = Query(None, description="إلى تاريخ"),
    db: Session = Depends(get_db)
):
    """الحصول على قائمة أوامر البيع مع التصفية"""
    return SalesService.get_sales_orders(db, skip, limit, status, customer_id, date_from, date_to)


@router.get("/orders/{order_id}", response_model=SalesOrder)
def get_sales_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """الحصول على أمر بيع بالمعرف"""
    return SalesService.get_sales_order_by_id(db, order_id)


@router.put("/orders/{order_id}/confirm", response_model=SalesOrder)
def confirm_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """تأكيد أمر البيع وحجز المخزون"""
    return SalesService.confirm_sales_order(db, order_id, user_id=1)


@router.put("/orders/{order_id}/ship", response_model=SalesOrder)
def ship_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """شحن أمر البيع وخصم المخزون"""
    return SalesService.ship_sales_order(db, order_id, user_id=1)


@router.put("/orders/{order_id}/cancel", response_model=SalesOrder)
def cancel_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """إلغاء أمر البيع"""
    return SalesService.cancel_sales_order(db, order_id, user_id=1)
