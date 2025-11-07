from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal

from app.models.invoice import (
    SalesInvoice, PurchaseInvoice, SalesInvoiceItem, 
    PurchaseInvoiceItem, InvoicePayment, InvoiceStatusEnum, InvoiceTypeEnum
)
from app.models.customer import Customer, Supplier
from app.models.sales import SalesOrder
from app.models.purchase import PurchaseOrder
from app.schemas.invoice import (
    SalesInvoiceCreate, SalesInvoiceUpdate, PurchaseInvoiceCreate, 
    PurchaseInvoiceUpdate, InvoicePaymentCreate, InvoicePaymentUpdate,
    InvoiceSummary, InvoiceFilter
)


class InvoiceService:
    """خدمة إدارة الفواتير - Invoice Management Service"""

    def __init__(self, db: Session):
        """
        Initialize invoice service.

        Args:
            db: Database session
        """
        self.db = db

    """خدمة إدارة الفواتير - Invoice Management Service"""

    # Converted from @staticmethod to instance method
    def generate_invoice_number(self, invoice_type: str = "SALES") -> str:
        """توليد رقم فاتورة جديد - Generate new invoice number"""
        prefix = "INV-S" if invoice_type == "SALES" else "INV-P"
        
        # Get the latest invoice number for this type
        if invoice_type == "SALES":
            latest = self.db.query(SalesInvoice).filter(
                SalesInvoice.invoice_number.startswith(prefix)
            ).order_by(desc(SalesInvoice.id)).first()
        else:
            latest = self.db.query(PurchaseInvoice).filter(
                PurchaseInvoice.invoice_number.startswith(prefix)
            ).order_by(desc(PurchaseInvoice.id)).first()
        
        if latest:
            try:
                last_number = int(latest.invoice_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:06d}"

    # Sales Invoice Operations
    # Converted from @staticmethod to instance method
    def create_sales_invoice(self, invoice_data: SalesInvoiceCreate) -> SalesInvoice:
        """إنشاء فاتورة مبيعات - Create sales invoice"""
        
        # Generate invoice number if not provided
        if not invoice_data.invoice_number:
            invoice_data.invoice_number = self.generate_invoice_number("SALES")
        
        # Create invoice
        db_invoice = SalesInvoice(**invoice_data.dict(exclude={'invoice_items'}))
        self.db.add(db_invoice)
        self.db.flush()  # Get the ID
        
        # Add invoice items
        for item_data in invoice_data.invoice_items:
            db_item = SalesInvoiceItem(invoice_id=db_invoice.id, **item_data.dict())
            self.db.add(db_item)
        
        self.db.commit()
        self.db.refresh(db_invoice)
        return db_invoice

    # Converted from @staticmethod to instance method
    def get_sales_invoice(self, invoice_id: int) -> Optional[SalesInvoice]:
        """الحصول على فاتورة مبيعات - Get sales invoice"""
        return self.db.query(SalesInvoice).filter(SalesInvoice.id == invoice_id).first()

    # Converted from @staticmethod to instance method
    def get_sales_invoices(
        db: Session, 
        filters: Optional[InvoiceFilter] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[SalesInvoice]:
        """الحصول على قائمة فواتير المبيعات - Get sales invoices list"""
        query = self.db.query(SalesInvoice)
        
        if filters:
            if filters.status:
                query = query.filter(SalesInvoice.status == filters.status)
            if filters.customer_id:
                query = query.filter(SalesInvoice.customer_id == filters.customer_id)
            if filters.branch_id:
                query = query.filter(SalesInvoice.branch_id == filters.branch_id)
            if filters.date_from:
                query = query.filter(SalesInvoice.invoice_date >= filters.date_from)
            if filters.date_to:
                query = query.filter(SalesInvoice.invoice_date <= filters.date_to)
            if filters.search:
                search_pattern = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        SalesInvoice.invoice_number.ilike(search_pattern),
                        SalesInvoice.reference_number.ilike(search_pattern),
                        SalesInvoice.notes.ilike(search_pattern)
                    )
                )
        
        return query.order_by(desc(SalesInvoice.created_at)).offset(skip).limit(limit).all()

    # Converted from @staticmethod to instance method
    def update_sales_invoice(
        db: Session, 
        invoice_id: int, 
        invoice_data: SalesInvoiceUpdate
    ) -> Optional[SalesInvoice]:
        """تحديث فاتورة مبيعات - Update sales invoice"""
        db_invoice = self.db.query(SalesInvoice).filter(SalesInvoice.id == invoice_id).first()
        if not db_invoice:
            return None
        
        update_data = invoice_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_invoice, field, value)
        
        self.db.commit()
        self.db.refresh(db_invoice)
        return db_invoice

    # Converted from @staticmethod to instance method
    def delete_sales_invoice(self, invoice_id: int) -> bool:
        """حذف فاتورة مبيعات - Delete sales invoice"""
        db_invoice = self.db.query(SalesInvoice).filter(SalesInvoice.id == invoice_id).first()
        if not db_invoice:
            return False
        
        self.db.delete(db_invoice)
        self.db.commit()
        return True

    # Purchase Invoice Operations
    # Converted from @staticmethod to instance method
    def create_purchase_invoice(self, invoice_data: PurchaseInvoiceCreate) -> PurchaseInvoice:
        """إنشاء فاتورة مشتريات - Create purchase invoice"""
        
        # Generate invoice number if not provided
        if not invoice_data.invoice_number:
            invoice_data.invoice_number = self.generate_invoice_number("PURCHASE")
        
        # Create invoice
        db_invoice = PurchaseInvoice(**invoice_data.dict(exclude={'invoice_items'}))
        self.db.add(db_invoice)
        self.db.flush()  # Get the ID
        
        # Add invoice items
        for item_data in invoice_data.invoice_items:
            db_item = PurchaseInvoiceItem(invoice_id=db_invoice.id, **item_data.dict())
            self.db.add(db_item)
        
        self.db.commit()
        self.db.refresh(db_invoice)
        return db_invoice

    # Converted from @staticmethod to instance method
    def get_purchase_invoice(self, invoice_id: int) -> Optional[PurchaseInvoice]:
        """الحصول على فاتورة مشتريات - Get purchase invoice"""
        return self.db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()

    # Converted from @staticmethod to instance method
    def get_purchase_invoices(
        db: Session, 
        filters: Optional[InvoiceFilter] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[PurchaseInvoice]:
        """الحصول على قائمة فواتير المشتريات - Get purchase invoices list"""
        query = self.db.query(PurchaseInvoice)
        
        if filters:
            if filters.status:
                query = query.filter(PurchaseInvoice.status == filters.status)
            if filters.supplier_id:
                query = query.filter(PurchaseInvoice.supplier_id == filters.supplier_id)
            if filters.branch_id:
                query = query.filter(PurchaseInvoice.branch_id == filters.branch_id)
            if filters.date_from:
                query = query.filter(PurchaseInvoice.invoice_date >= filters.date_from)
            if filters.date_to:
                query = query.filter(PurchaseInvoice.invoice_date <= filters.date_to)
            if filters.search:
                search_pattern = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        PurchaseInvoice.invoice_number.ilike(search_pattern),
                        PurchaseInvoice.supplier_invoice_number.ilike(search_pattern),
                        PurchaseInvoice.reference_number.ilike(search_pattern),
                        PurchaseInvoice.notes.ilike(search_pattern)
                    )
                )
        
        return query.order_by(desc(PurchaseInvoice.created_at)).offset(skip).limit(limit).all()

    # Converted from @staticmethod to instance method
    def update_purchase_invoice(
        db: Session, 
        invoice_id: int, 
        invoice_data: PurchaseInvoiceUpdate
    ) -> Optional[PurchaseInvoice]:
        """تحديث فاتورة مشتريات - Update purchase invoice"""
        db_invoice = self.db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()
        if not db_invoice:
            return None
        
        update_data = invoice_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_invoice, field, value)
        
        self.db.commit()
        self.db.refresh(db_invoice)
        return db_invoice

    # Converted from @staticmethod to instance method
    def delete_purchase_invoice(self, invoice_id: int) -> bool:
        """حذف فاتورة مشتريات - Delete purchase invoice"""
        db_invoice = self.db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()
        if not db_invoice:
            return False
        
        self.db.delete(db_invoice)
        self.db.commit()
        return True

    # Invoice Payment Operations
    # Converted from @staticmethod to instance method
    def create_payment(self, payment_data: InvoicePaymentCreate) -> InvoicePayment:
        """إنشاء دفعة فاتورة - Create invoice payment"""
        
        # Generate payment number if not provided
        if not payment_data.payment_number:
            payment_data.payment_number = self.generate_payment_number()
        
        db_payment = InvoicePayment(**payment_data.dict())
        self.db.add(db_payment)
        
        # Update invoice paid amount
        if payment_data.sales_invoice_id:
            invoice = self.db.query(SalesInvoice).filter(
                SalesInvoice.id == payment_data.sales_invoice_id
            ).first()
            if invoice:
                invoice.paid_amount = (invoice.paid_amount or 0) + payment_data.amount
                # Update status based on payment
                if invoice.paid_amount >= invoice.total_amount:
                    invoice.status = InvoiceStatusEnum.PAID
                elif invoice.paid_amount > 0:
                    invoice.status = InvoiceStatusEnum.PARTIALLY_PAID
        
        elif payment_data.purchase_invoice_id:
            invoice = self.db.query(PurchaseInvoice).filter(
                PurchaseInvoice.id == payment_data.purchase_invoice_id
            ).first()
            if invoice:
                invoice.paid_amount = (invoice.paid_amount or 0) + payment_data.amount
                # Update status based on payment
                if invoice.paid_amount >= invoice.total_amount:
                    invoice.status = InvoiceStatusEnum.PAID
                elif invoice.paid_amount > 0:
                    invoice.status = InvoiceStatusEnum.PARTIALLY_PAID
        
        self.db.commit()
        self.db.refresh(db_payment)
        return db_payment

    # Converted from @staticmethod to instance method
    def generate_payment_number(self) -> str:
        """توليد رقم دفعة جديد - Generate new payment number"""
        prefix = "PAY"
        
        # Get the latest payment number
        latest = self.db.query(InvoicePayment).filter(
            InvoicePayment.payment_number.startswith(prefix)
        ).order_by(desc(InvoicePayment.id)).first()
        
        if latest:
            try:
                last_number = int(latest.payment_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:06d}"

    # Converted from @staticmethod to instance method
    def get_invoice_payments(self, invoice_id: int, invoice_type: str) -> List[InvoicePayment]:
        """الحصول على دفعات الفاتورة - Get invoice payments"""
        if invoice_type.upper() == "SALES":
            return self.db.query(InvoicePayment).filter(
                InvoicePayment.sales_invoice_id == invoice_id
            ).order_by(desc(InvoicePayment.payment_date)).all()
        else:
            return self.db.query(InvoicePayment).filter(
                InvoicePayment.purchase_invoice_id == invoice_id
            ).order_by(desc(InvoicePayment.payment_date)).all()

    # Converted from @staticmethod to instance method
    def get_all_payments(self, page: int = 1, size: int = 10, invoice_type: Optional[InvoiceTypeEnum] = None) -> List[InvoicePayment]:
        """الحصول على جميع دفعات الفواتير - Get all invoice payments"""
        query = self.db.query(InvoicePayment)
        
        if invoice_type:
            if invoice_type == InvoiceTypeEnum.SALES:
                query = query.filter(InvoicePayment.sales_invoice_id.isnot(None))
            elif invoice_type == InvoiceTypeEnum.PURCHASE:
                query = query.filter(InvoicePayment.purchase_invoice_id.isnot(None))
        
        offset = (page - 1) * size
        return query.order_by(desc(InvoicePayment.payment_date)).offset(offset).limit(size).all()

    # Invoice Status Management
    # Converted from @staticmethod to instance method
    def mark_invoice_as_sent(self, invoice_id: int, invoice_type: str) -> bool:
        """تمييز الفاتورة كمرسلة - Mark invoice as sent"""
        if invoice_type.upper() == "SALES":
            invoice = self.db.query(SalesInvoice).filter(SalesInvoice.id == invoice_id).first()
        else:
            invoice = self.db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()
        
        if not invoice:
            return False
        
        invoice.status = InvoiceStatusEnum.PENDING
        invoice.issued_at = datetime.now()
        self.db.commit()
        return True

    # Converted from @staticmethod to instance method
    def cancel_invoice(self, invoice_id: int, invoice_type: str) -> bool:
        """إلغاء الفاتورة - Cancel invoice"""
        if invoice_type.upper() == "SALES":
            invoice = self.db.query(SalesInvoice).filter(SalesInvoice.id == invoice_id).first()
        else:
            invoice = self.db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()
        
        if not invoice:
            return False
        
        invoice.status = InvoiceStatusEnum.CANCELLED
        invoice.cancelled_at = datetime.now()
        self.db.commit()
        return True

    # Dashboard and Reports
    # Converted from @staticmethod to instance method
    def get_invoice_summary(self, branch_id: Optional[int] = None) -> InvoiceSummary:
        """الحصول على ملخص الفواتير - Get invoice summary"""
        
        # Base queries
        sales_query = self.db.query(SalesInvoice)
        purchase_query = self.db.query(PurchaseInvoice)
        
        if branch_id:
            sales_query = sales_query.filter(SalesInvoice.branch_id == branch_id)
            purchase_query = purchase_query.filter(PurchaseInvoice.branch_id == branch_id)
        
        # Sales statistics
        total_sales_invoices = sales_query.count()
        total_sales_amount = sales_query.with_entities(
            func.coalesce(func.sum(SalesInvoice.total_amount), 0)
        ).scalar() or Decimal('0')
        
        pending_sales_amount = sales_query.filter(
            SalesInvoice.status.in_([InvoiceStatusEnum.PENDING, InvoiceStatusEnum.PARTIALLY_PAID])
        ).with_entities(
            func.coalesce(func.sum(SalesInvoice.total_amount - SalesInvoice.paid_amount), 0)
        ).scalar() or Decimal('0')
        
        overdue_sales_count = sales_query.filter(
            and_(
                SalesInvoice.due_date < date.today(),
                SalesInvoice.status != InvoiceStatusEnum.PAID
            )
        ).count()
        
        # Purchase statistics
        total_purchase_invoices = purchase_query.count()
        total_purchase_amount = purchase_query.with_entities(
            func.coalesce(func.sum(PurchaseInvoice.total_amount), 0)
        ).scalar() or Decimal('0')
        
        pending_purchase_amount = purchase_query.filter(
            PurchaseInvoice.status.in_([InvoiceStatusEnum.PENDING, InvoiceStatusEnum.PARTIALLY_PAID])
        ).with_entities(
            func.coalesce(func.sum(PurchaseInvoice.total_amount - PurchaseInvoice.paid_amount), 0)
        ).scalar() or Decimal('0')
        
        overdue_purchase_count = purchase_query.filter(
            and_(
                PurchaseInvoice.due_date < date.today(),
                PurchaseInvoice.status != InvoiceStatusEnum.PAID
            )
        ).count()
        
        return InvoiceSummary(
            total_sales_invoices=total_sales_invoices,
            total_purchase_invoices=total_purchase_invoices,
            total_sales_amount=total_sales_amount,
            total_purchase_amount=total_purchase_amount,
            pending_sales_amount=pending_sales_amount,
            pending_purchase_amount=pending_purchase_amount,
            overdue_sales_count=overdue_sales_count,
            overdue_purchase_count=overdue_purchase_count
        )

    # Converted from @staticmethod to instance method
    def get_overdue_invoices(self, branch_id: Optional[int] = None) -> Dict[str, List]:
        """الحصول على الفواتير المتأخرة - Get overdue invoices"""
        
        # Sales overdue
        sales_query = self.db.query(SalesInvoice).filter(
            and_(
                SalesInvoice.due_date < date.today(),
                SalesInvoice.status != InvoiceStatusEnum.PAID
            )
        )
        
        # Purchase overdue
        purchase_query = self.db.query(PurchaseInvoice).filter(
            and_(
                PurchaseInvoice.due_date < date.today(),
                PurchaseInvoice.status != InvoiceStatusEnum.PAID
            )
        )
        
        if branch_id:
            sales_query = sales_query.filter(SalesInvoice.branch_id == branch_id)
            purchase_query = purchase_query.filter(PurchaseInvoice.branch_id == branch_id)
        
        return {
            "sales": sales_query.order_by(SalesInvoice.due_date).all(),
            "purchase": purchase_query.order_by(PurchaseInvoice.due_date).all()
        }

    # Converted from @staticmethod to instance method
    def create_invoice_from_order(
        db: Session, 
        order_id: int, 
        order_type: str, 
        created_by: int
    ) -> Optional[Dict[str, Any]]:
        """إنشاء فاتورة من أمر - Create invoice from order"""
        
        if order_type.upper() == "SALES":
            order = self.db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
            if not order:
                return None
            
            # Create sales invoice from sales order
            invoice_data = SalesInvoiceCreate(
                invoice_number="",  # Will be generated
                customer_id=order.customer_id,
                sales_order_id=order.id,
                branch_id=order.branch_id,
                warehouse_id=order.warehouse_id,
                invoice_date=date.today(),
                due_date=date.today(),  # Should be calculated based on payment terms
                currency_id=order.currency_id,
                exchange_rate=order.exchange_rate,
                subtotal=order.subtotal,
                discount_percentage=order.discount_percentage,
                discount_amount=order.discount_amount,
                tax_percentage=order.tax_percentage,
                tax_amount=order.tax_amount,
                shipping_amount=order.shipping_amount,
                total_amount=order.total_amount,
                notes=f"Generated from Sales Order: {order.order_number}",
                created_by=created_by,
                invoice_items=[
                    {
                        "product_id": item.product_id,
                        "sales_item_id": item.id,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "discount_percentage": item.discount_percentage,
                        "discount_amount": item.discount_amount,
                        "line_total": item.line_total,
                        "description": item.description,
                        "notes": item.notes
                    }
                    for item in order.order_items
                ]
            )
            
            return self.create_sales_invoice(invoice_data)
        
        else:  # PURCHASE
            order = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
            if not order:
                return None
            
            # Create purchase invoice from purchase order
            invoice_data = PurchaseInvoiceCreate(
                invoice_number="",  # Will be generated
                supplier_id=order.supplier_id,
                purchase_order_id=order.id,
                branch_id=order.branch_id,
                warehouse_id=order.warehouse_id,
                invoice_date=date.today(),
                due_date=date.today(),  # Should be calculated based on payment terms
                currency_id=order.currency_id,
                exchange_rate=order.exchange_rate,
                subtotal=order.subtotal,
                discount_percentage=order.discount_percentage,
                discount_amount=order.discount_amount,
                tax_percentage=order.tax_percentage,
                tax_amount=order.tax_amount,
                shipping_amount=order.shipping_amount,
                total_amount=order.total_amount,
                notes=f"Generated from Purchase Order: {order.order_number}",
                created_by=created_by,
                invoice_items=[
                    {
                        "product_id": item.product_id,
                        "purchase_item_id": item.id,
                        "quantity": item.quantity,
                        "unit_cost": item.unit_cost,
                        "discount_percentage": item.discount_percentage,
                        "discount_amount": item.discount_amount,
                        "line_total": item.line_total,
                        "description": item.description,
                        "notes": item.notes
                    }
                    for item in order.order_items
                ]
            )
            
            return self.create_purchase_invoice(invoice_data)

# ============================================================================
# Dependency for FastAPI
# ============================================================================

from app.db.database import get_db
from fastapi import Depends


def get_invoice_service(db: Session = Depends(get_db)) -> InvoiceService:
    """
    Dependency to get InvoiceService instance.

    Usage in routers:
        @router.get("/invoices")
        def get_invoices(
            service: InvoiceService = Depends(get_invoice_service)
        ):
            invoices, total = service.get_sales_invoices()
            return invoices
    """
    return InvoiceService(db)
