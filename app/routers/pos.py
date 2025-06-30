from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.db.database import get_db
from app.services.pos_service import POSService
from app.schemas.pos import (
    POSTerminalCreate, POSTerminalUpdate, POSTerminal,
    POSSessionCreate, POSSessionUpdate, POSSession,
    POSTransactionCreate, POSTransactionUpdate, POSTransaction,
    POSTransactionItemCreate, POSTransactionItem,
    POSPaymentCreate, POSPayment,
    POSDiscountCreate, POSDiscountUpdate, POSDiscount,
    POSPromotionCreate, POSPromotionUpdate, POSPromotion,
    POSSalesReport, POSSessionReport, POSProductSalesReport
)

router = APIRouter()

# POS Terminal Management
@router.get("/terminals", response_model=List[POSTerminal])
def get_terminals(
    branch_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get POS terminals - جلب أجهزة نقاط البيع"""
    service = POSService(db)
    return service.get_terminals(branch_id, active_only)

@router.post("/terminals", response_model=POSTerminal)
def create_terminal(terminal: POSTerminalCreate, db: Session = Depends(get_db)):
    """Create new POS terminal - إنشاء جهاز نقطة بيع جديد"""
    service = POSService(db)
    return service.create_terminal(terminal)

@router.get("/terminals/{terminal_id}", response_model=POSTerminal)
def get_terminal(terminal_id: int, db: Session = Depends(get_db)):
    """Get specific POS terminal - جلب جهاز نقطة بيع محدد"""
    service = POSService(db)
    terminal = service.get_terminal(terminal_id)
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found - الجهاز غير موجود")
    return terminal

@router.put("/terminals/{terminal_id}", response_model=POSTerminal)
def update_terminal(terminal_id: int, terminal: POSTerminalUpdate, db: Session = Depends(get_db)):
    """Update POS terminal - تحديث جهاز نقطة البيع"""
    service = POSService(db)
    updated_terminal = service.update_terminal(terminal_id, terminal)
    if not updated_terminal:
        raise HTTPException(status_code=404, detail="Terminal not found - الجهاز غير موجود")
    return updated_terminal

# POS Session Management
@router.get("/sessions", response_model=List[POSSession])
def get_sessions(
    terminal_id: Optional[int] = Query(None),
    cashier_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get POS sessions with filters - جلب جلسات نقاط البيع مع المرشحات"""
    service = POSService(db)
    return service.get_sessions(terminal_id, cashier_id, date_from, date_to, status)

@router.post("/sessions", response_model=POSSession)
def create_session(session: POSSessionCreate, db: Session = Depends(get_db)):
    """Create new POS session - إنشاء جلسة نقطة بيع جديدة"""
    service = POSService(db)
    return service.create_session(session)

@router.get("/sessions/{session_id}", response_model=POSSession)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get specific POS session - جلب جلسة نقطة بيع محددة"""
    service = POSService(db)
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found - الجلسة غير موجودة")
    return session

@router.post("/sessions/{session_id}/close")
def close_session(session_id: int, db: Session = Depends(get_db)):
    """Close POS session - إغلاق جلسة نقطة البيع"""
    service = POSService(db)
    closed_session = service.close_session(session_id)
    if not closed_session:
        raise HTTPException(status_code=400, detail="Failed to close session - فشل في إغلاق الجلسة")
    return closed_session

@router.get("/sessions/active/{terminal_id}", response_model=POSSession)
def get_active_session(terminal_id: int, db: Session = Depends(get_db)):
    """Get active session for terminal - جلب الجلسة النشطة للجهاز"""
    service = POSService(db)
    session = service.get_active_session(terminal_id)
    if not session:
        raise HTTPException(status_code=404, detail="No active session found - لا توجد جلسة نشطة")
    return session

# POS Transaction Management
@router.get("/transactions", response_model=List[POSTransaction])
def get_transactions(
    session_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get POS transactions with filters - جلب معاملات نقاط البيع مع المرشحات"""
    service = POSService(db)
    return service.get_transactions(session_id, customer_id, date_from, date_to, status)

@router.post("/transactions", response_model=POSTransaction)
def create_transaction(transaction: POSTransactionCreate, db: Session = Depends(get_db)):
    """Create new POS transaction - إنشاء معاملة نقطة بيع جديدة"""
    service = POSService(db)
    try:
        return service.create_transaction(transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions/{transaction_id}", response_model=POSTransaction)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get specific POS transaction - جلب معاملة نقطة بيع محددة"""
    service = POSService(db)
    transaction = service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found - المعاملة غير موجودة")
    return transaction

@router.post("/transactions/{transaction_id}/complete")
def complete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Complete POS transaction - إتمام معاملة نقطة البيع"""
    service = POSService(db)
    completed_transaction = service.complete_transaction(transaction_id)
    if not completed_transaction:
        raise HTTPException(status_code=400, detail="Failed to complete transaction - فشل في إتمام المعاملة")
    return completed_transaction

@router.post("/transactions/{transaction_id}/void")
def void_transaction(transaction_id: int, reason: str, db: Session = Depends(get_db)):
    """Void POS transaction - إلغاء معاملة نقطة البيع"""
    service = POSService(db)
    voided_transaction = service.void_transaction(transaction_id, reason)
    if not voided_transaction:
        raise HTTPException(status_code=400, detail="Failed to void transaction - فشل في إلغاء المعاملة")
    return voided_transaction

@router.post("/transactions/{transaction_id}/refund")
def process_refund(transaction_id: int, items: List[dict], reason: str, db: Session = Depends(get_db)):
    """Process transaction refund - معالجة استرداد المعاملة"""
    service = POSService(db)
    refund_transaction = service.process_refund(transaction_id, items, reason)
    if not refund_transaction:
        raise HTTPException(status_code=400, detail="Failed to process refund - فشل في معالجة الاسترداد")
    return refund_transaction

# POS Payments
@router.get("/payments", response_model=List[POSPayment])
def get_payments(
    transaction_id: Optional[int] = Query(None),
    payment_method: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get POS payments - جلب مدفوعات نقاط البيع"""
    service = POSService(db)
    return service.get_payments(transaction_id, payment_method)

@router.post("/payments", response_model=POSPayment)
def create_payment(payment: POSPaymentCreate, db: Session = Depends(get_db)):
    """Create new POS payment - إنشاء دفعة نقطة بيع جديدة"""
    service = POSService(db)
    return service.create_payment(payment)

# Discount Management
@router.get("/discounts", response_model=List[POSDiscount])
def get_discounts(
    active_only: bool = Query(True),
    discount_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get POS discounts - جلب خصومات نقاط البيع"""
    service = POSService(db)
    return service.get_discounts(active_only, discount_type)

@router.post("/discounts", response_model=POSDiscount)
def create_discount(discount: POSDiscountCreate, db: Session = Depends(get_db)):
    """Create new POS discount - إنشاء خصم نقطة بيع جديد"""
    service = POSService(db)
    return service.create_discount(discount)

@router.get("/discounts/{discount_id}", response_model=POSDiscount)
def get_discount(discount_id: int, db: Session = Depends(get_db)):
    """Get specific POS discount - جلب خصم نقطة بيع محدد"""
    service = POSService(db)
    discount = service.get_discount(discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found - الخصم غير موجود")
    return discount

@router.put("/discounts/{discount_id}", response_model=POSDiscount)
def update_discount(discount_id: int, discount: POSDiscountUpdate, db: Session = Depends(get_db)):
    """Update POS discount - تحديث خصم نقطة البيع"""
    service = POSService(db)
    updated_discount = service.update_discount(discount_id, discount)
    if not updated_discount:
        raise HTTPException(status_code=404, detail="Discount not found - الخصم غير موجود")
    return updated_discount

@router.post("/discounts/{discount_id}/validate")
def validate_discount(
    discount_id: int,
    transaction_total: float,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Validate discount eligibility - التحقق من أهلية الخصم"""
    service = POSService(db)
    is_valid = service.validate_discount(discount_id, transaction_total, customer_id)
    return {"valid": is_valid}

# Promotion Management
@router.get("/promotions", response_model=List[POSPromotion])
def get_promotions(
    active_only: bool = Query(True),
    promotion_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get POS promotions - جلب عروض نقاط البيع"""
    service = POSService(db)
    return service.get_promotions(active_only, promotion_type)

@router.post("/promotions", response_model=POSPromotion)
def create_promotion(promotion: POSPromotionCreate, db: Session = Depends(get_db)):
    """Create new POS promotion - إنشاء عرض نقطة بيع جديد"""
    service = POSService(db)
    return service.create_promotion(promotion)

@router.get("/promotions/{promotion_id}", response_model=POSPromotion)
def get_promotion(promotion_id: int, db: Session = Depends(get_db)):
    """Get specific POS promotion - جلب عرض نقطة بيع محدد"""
    service = POSService(db)
    promotion = service.get_promotion(promotion_id)
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found - العرض غير موجود")
    return promotion

@router.put("/promotions/{promotion_id}", response_model=POSPromotion)
def update_promotion(promotion_id: int, promotion: POSPromotionUpdate, db: Session = Depends(get_db)):
    """Update POS promotion - تحديث عرض نقطة البيع"""
    service = POSService(db)
    updated_promotion = service.update_promotion(promotion_id, promotion)
    if not updated_promotion:
        raise HTTPException(status_code=404, detail="Promotion not found - العرض غير موجود")
    return updated_promotion

# Inventory Checks
@router.get("/inventory/check/{product_id}")
def check_stock_availability(product_id: int, quantity: int, db: Session = Depends(get_db)):
    """Check stock availability - التحقق من توفر المخزون"""
    service = POSService(db)
    available = service.check_stock_availability(product_id, quantity)
    return {"available": available}

@router.get("/inventory/stock/{product_id}")
def get_product_stock(product_id: int, db: Session = Depends(get_db)):
    """Get product stock quantity - جلب كمية المخزون للمنتج"""
    service = POSService(db)
    stock = service.get_product_stock(product_id)
    return {"product_id": product_id, "stock_quantity": stock}

# Reports
@router.get("/reports/sales", response_model=POSSalesReport)
def get_sales_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    terminal_id: Optional[int] = Query(None),
    cashier_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get POS sales report - جلب تقرير مبيعات نقاط البيع"""
    service = POSService(db)
    return service.generate_sales_report(date_from, date_to, terminal_id, cashier_id)

@router.get("/reports/sessions", response_model=List[POSSessionReport])
def get_session_reports(
    date_from: date = Query(...),
    date_to: date = Query(...),
    terminal_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get POS session reports - جلب تقارير جلسات نقاط البيع"""
    service = POSService(db)
    return service.generate_session_reports(date_from, date_to, terminal_id)

@router.get("/reports/product-sales", response_model=List[POSProductSalesReport])
def get_product_sales_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    product_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get product sales report - جلب تقرير مبيعات المنتجات"""
    service = POSService(db)
    return service.generate_product_sales_report(date_from, date_to, product_id, category_id)
