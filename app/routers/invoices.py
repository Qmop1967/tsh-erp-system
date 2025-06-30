from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.services.invoice_service import InvoiceService
from app.schemas.invoice import (
    SalesInvoice, SalesInvoiceCreate, SalesInvoiceUpdate,
    PurchaseInvoice, PurchaseInvoiceCreate, PurchaseInvoiceUpdate,
    InvoicePayment, InvoicePaymentCreate, InvoicePaymentUpdate,
    InvoiceSummary, InvoiceFilter
)
from app.models.invoice import InvoiceTypeEnum
from app.routers.auth import get_current_user

router = APIRouter(prefix="/invoices", tags=["invoices"])


# Sales Invoice Endpoints
@router.post("/sales", response_model=SalesInvoice, summary="Create Sales Invoice")
async def create_sales_invoice(
    invoice_data: SalesInvoiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """إنشاء فاتورة مبيعات جديدة - Create new sales invoice"""
    try:
        invoice_data.created_by = current_user.id
        invoice = InvoiceService.create_sales_invoice(db, invoice_data)
        return invoice
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sales", response_model=List[SalesInvoice], summary="Get Sales Invoices")
async def get_sales_invoices(
    status: Optional[str] = Query(None, description="Filter by status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    branch_id: Optional[int] = Query(None, description="Filter by branch"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in invoice number, reference, notes"),
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """الحصول على قائمة فواتير المبيعات - Get sales invoices list"""
    
    filters = InvoiceFilter()
    if status:
        filters.status = status
    if customer_id:
        filters.customer_id = customer_id
    if branch_id:
        filters.branch_id = branch_id
    if date_from:
        from datetime import datetime
        filters.date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    if date_to:
        from datetime import datetime
        filters.date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    if search:
        filters.search = search
    
    invoices = InvoiceService.get_sales_invoices(db, filters, skip, limit)
    return invoices


@router.get("/sales/{invoice_id}", response_model=SalesInvoice, summary="Get Sales Invoice")
async def get_sales_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """الحصول على فاتورة مبيعات - Get sales invoice"""
    invoice = InvoiceService.get_sales_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Sales invoice not found")
    return invoice


@router.put("/sales/{invoice_id}", response_model=SalesInvoice, summary="Update Sales Invoice")
async def update_sales_invoice(
    invoice_id: int,
    invoice_data: SalesInvoiceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تحديث فاتورة مبيعات - Update sales invoice"""
    invoice = InvoiceService.update_sales_invoice(db, invoice_id, invoice_data)
    if not invoice:
        raise HTTPException(status_code=404, detail="Sales invoice not found")
    return invoice


@router.delete("/sales/{invoice_id}", summary="Delete Sales Invoice")
async def delete_sales_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """حذف فاتورة مبيعات - Delete sales invoice"""
    success = InvoiceService.delete_sales_invoice(db, invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sales invoice not found")
    return {"message": "Sales invoice deleted successfully"}


# Purchase Invoice Endpoints
@router.post("/purchase", response_model=PurchaseInvoice, summary="Create Purchase Invoice")
async def create_purchase_invoice(
    invoice_data: PurchaseInvoiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """إنشاء فاتورة مشتريات جديدة - Create new purchase invoice"""
    try:
        invoice_data.created_by = current_user.id
        invoice = InvoiceService.create_purchase_invoice(db, invoice_data)
        return invoice
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/purchase", response_model=List[PurchaseInvoice], summary="Get Purchase Invoices")
async def get_purchase_invoices(
    status: Optional[str] = Query(None, description="Filter by status"),
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    branch_id: Optional[int] = Query(None, description="Filter by branch"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in invoice number, reference, notes"),
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """الحصول على قائمة فواتير المشتريات - Get purchase invoices list"""
    
    filters = InvoiceFilter()
    if status:
        filters.status = status
    if supplier_id:
        filters.supplier_id = supplier_id
    if branch_id:
        filters.branch_id = branch_id
    if date_from:
        from datetime import datetime
        filters.date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    if date_to:
        from datetime import datetime
        filters.date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    if search:
        filters.search = search
    
    invoices = InvoiceService.get_purchase_invoices(db, filters, skip, limit)
    return invoices


@router.get("/purchase/{invoice_id}", response_model=PurchaseInvoice, summary="Get Purchase Invoice")
async def get_purchase_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """الحصول على فاتورة مشتريات - Get purchase invoice"""
    invoice = InvoiceService.get_purchase_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Purchase invoice not found")
    return invoice


@router.put("/purchase/{invoice_id}", response_model=PurchaseInvoice, summary="Update Purchase Invoice")
async def update_purchase_invoice(
    invoice_id: int,
    invoice_data: PurchaseInvoiceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تحديث فاتورة مشتريات - Update purchase invoice"""
    invoice = InvoiceService.update_purchase_invoice(db, invoice_id, invoice_data)
    if not invoice:
        raise HTTPException(status_code=404, detail="Purchase invoice not found")
    return invoice


@router.delete("/purchase/{invoice_id}", summary="Delete Purchase Invoice")
async def delete_purchase_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """حذف فاتورة مشتريات - Delete purchase invoice"""
    success = InvoiceService.delete_purchase_invoice(db, invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Purchase invoice not found")
    return {"message": "Purchase invoice deleted successfully"}


# Invoice Payment Endpoints
@router.post("/payments", response_model=InvoicePayment, summary="Create Invoice Payment")
async def create_invoice_payment(
    payment_data: InvoicePaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """إنشاء دفعة فاتورة - Create invoice payment"""
    try:
        payment_data.created_by = current_user.id
        payment = InvoiceService.create_payment(db, payment_data)
        return payment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payments/{invoice_id}", response_model=List[InvoicePayment], summary="Get Invoice Payments")
async def get_invoice_payments(
    invoice_id: int,
    invoice_type: str = Query(..., description="Invoice type: SALES or PURCHASE"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """الحصول على دفعات الفاتورة - Get invoice payments"""
    payments = InvoiceService.get_invoice_payments(db, invoice_id, invoice_type)
    return payments


@router.get("/payments", response_model=List[InvoicePayment], summary="Get All Invoice Payments")
async def get_all_invoice_payments(
    page: int = 1,
    size: int = 10,
    invoice_type: Optional[InvoiceTypeEnum] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """الحصول على جميع دفعات الفواتير - Get all invoice payments"""
    payments = InvoiceService.get_all_payments(db, page, size, invoice_type)
    return payments


# Invoice Status Management
@router.post("/sales/{invoice_id}/send", summary="Mark Sales Invoice as Sent")
async def mark_sales_invoice_as_sent(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تمييز فاتورة المبيعات كمرسلة - Mark sales invoice as sent"""
    success = InvoiceService.mark_invoice_as_sent(db, invoice_id, "SALES")
    if not success:
        raise HTTPException(status_code=404, detail="Sales invoice not found")
    return {"message": "Sales invoice marked as sent"}


@router.post("/purchase/{invoice_id}/send", summary="Mark Purchase Invoice as Sent")
async def mark_purchase_invoice_as_sent(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تمييز فاتورة المشتريات كمرسلة - Mark purchase invoice as sent"""
    success = InvoiceService.mark_invoice_as_sent(db, invoice_id, "PURCHASE")
    if not success:
        raise HTTPException(status_code=404, detail="Purchase invoice not found")
    return {"message": "Purchase invoice marked as sent"}


@router.post("/sales/{invoice_id}/cancel", summary="Cancel Sales Invoice")
async def cancel_sales_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """إلغاء فاتورة المبيعات - Cancel sales invoice"""
    success = InvoiceService.cancel_invoice(db, invoice_id, "SALES")
    if not success:
        raise HTTPException(status_code=404, detail="Sales invoice not found")
    return {"message": "Sales invoice cancelled"}


@router.post("/purchase/{invoice_id}/cancel", summary="Cancel Purchase Invoice")
async def cancel_purchase_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """إلغاء فاتورة المشتريات - Cancel purchase invoice"""
    success = InvoiceService.cancel_invoice(db, invoice_id, "PURCHASE")
    if not success:
        raise HTTPException(status_code=404, detail="Purchase invoice not found")
    return {"message": "Purchase invoice cancelled"}


# Dashboard and Reports
@router.get("/summary", response_model=InvoiceSummary, summary="Get Invoice Summary")
async def get_invoice_summary(
    branch_id: Optional[int] = Query(None, description="Filter by branch"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """الحصول على ملخص الفواتير - Get invoice summary"""
    summary = InvoiceService.get_invoice_summary(db, branch_id)
    return summary


@router.get("/overdue", summary="Get Overdue Invoices")
async def get_overdue_invoices(
    branch_id: Optional[int] = Query(None, description="Filter by branch"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """الحصول على الفواتير المتأخرة - Get overdue invoices"""
    overdue = InvoiceService.get_overdue_invoices(db, branch_id)
    return overdue


# Generate Invoice from Order
@router.post("/generate-from-order", summary="Generate Invoice from Order")
async def generate_invoice_from_order(
    order_id: int = Query(..., description="Order ID"),
    order_type: str = Query(..., description="Order type: SALES or PURCHASE"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """إنشاء فاتورة من أمر - Generate invoice from order"""
    invoice = InvoiceService.create_invoice_from_order(db, order_id, order_type, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Order not found")
    return invoice
