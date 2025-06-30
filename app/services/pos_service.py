from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import datetime, date
from app.models.pos import (
    POSTerminal, POSSession, POSTransaction, POSTransactionItem, POSPayment,
    POSDiscount, POSPromotion, POSSessionStatusEnum, POSTransactionTypeEnum
)
from app.models.product import Product
from app.models.inventory import InventoryItem
from app.schemas.pos import (
    POSTerminalCreate, POSTerminalUpdate,
    POSSessionCreate, POSSessionUpdate,
    POSTransactionCreate, POSTransactionUpdate,
    POSDiscountCreate, POSDiscountUpdate,
    POSPromotionCreate, POSPromotionUpdate,
    POSSalesReport, POSSessionReport
)
from fastapi import HTTPException, status
import json


class POSTerminalService:
    """خدمة إدارة محطات نقاط البيع"""

    @staticmethod
    def create_terminal(db: Session, terminal: POSTerminalCreate) -> POSTerminal:
        """إنشاء محطة نقاط بيع جديدة"""
        # التحقق من عدم تكرار رمز المحطة
        existing_terminal = db.query(POSTerminal).filter(
            POSTerminal.terminal_code == terminal.terminal_code
        ).first()
        if existing_terminal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Terminal code already exists"
            )
        
        db_terminal = POSTerminal(**terminal.dict())
        db.add(db_terminal)
        db.commit()
        db.refresh(db_terminal)
        return db_terminal

    @staticmethod
    def get_terminals(db: Session, branch_id: Optional[int] = None, 
                     active_only: bool = True) -> List[POSTerminal]:
        """الحصول على قائمة محطات نقاط البيع"""
        query = db.query(POSTerminal)
        
        if active_only:
            query = query.filter(POSTerminal.is_active == True)
        
        if branch_id:
            query = query.filter(POSTerminal.branch_id == branch_id)
        
        return query.all()

    @staticmethod
    def get_terminal(db: Session, terminal_id: int) -> POSTerminal:
        """الحصول على محطة نقاط بيع محددة"""
        terminal = db.query(POSTerminal).filter(POSTerminal.id == terminal_id).first()
        if not terminal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Terminal not found"
            )
        return terminal

    @staticmethod
    def update_terminal(db: Session, terminal_id: int, terminal_update: POSTerminalUpdate) -> POSTerminal:
        """تحديث بيانات محطة نقاط البيع"""
        terminal = POSTerminalService.get_terminal(db, terminal_id)
        
        update_data = terminal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(terminal, field, value)
        
        terminal.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(terminal)
        return terminal


class POSSessionService:
    """خدمة إدارة جلسات نقاط البيع"""

    @staticmethod
    def start_session(db: Session, session: POSSessionCreate) -> POSSession:
        """بدء جلسة نقاط بيع جديدة"""
        # التحقق من عدم وجود جلسة مفتوحة للمحطة
        existing_session = db.query(POSSession).filter(
            and_(
                POSSession.terminal_id == session.terminal_id,
                POSSession.status == POSSessionStatusEnum.OPEN
            )
        ).first()
        
        if existing_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Terminal already has an open session"
            )
        
        # إنشاء رقم الجلسة
        session_count = db.query(POSSession).filter(
            POSSession.terminal_id == session.terminal_id
        ).count()
        session_number = f"SES-{session.terminal_id:04d}-{session_count + 1:06d}"
        
        db_session = POSSession(
            **session.dict(),
            session_number=session_number,
            status=POSSessionStatusEnum.OPEN
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def close_session(db: Session, session_id: int, session_update: POSSessionUpdate, 
                     user_id: int) -> POSSession:
        """إغلاق جلسة نقاط البيع"""
        session = db.query(POSSession).filter(POSSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.status != POSSessionStatusEnum.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not open"
            )
        
        # حساب الإجماليات من المعاملات
        session_totals = db.query(
            func.sum(POSTransaction.total_amount).label('total_sales'),
            func.sum(POSTransaction.discount_amount).label('total_discounts'),
            func.sum(POSTransaction.tax_amount).label('total_tax'),
            func.count(POSTransaction.id).label('transaction_count')
        ).filter(
            and_(
                POSTransaction.session_id == session_id,
                POSTransaction.transaction_type == POSTransactionTypeEnum.SALE
            )
        ).first()
        
        # تحديث بيانات الجلسة
        update_data = session_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)
        
        session.status = POSSessionStatusEnum.CLOSED
        session.end_time = datetime.utcnow()
        session.closed_by = user_id
        session.total_sales = session_totals.total_sales or Decimal(0)
        session.total_discounts = session_totals.total_discounts or Decimal(0)
        session.total_tax = session_totals.total_tax or Decimal(0)
        session.transaction_count = session_totals.transaction_count or 0
        
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_current_session(db: Session, terminal_id: int) -> Optional[POSSession]:
        """الحصول على الجلسة الحالية للمحطة"""
        return db.query(POSSession).filter(
            and_(
                POSSession.terminal_id == terminal_id,
                POSSession.status == POSSessionStatusEnum.OPEN
            )
        ).first()


class POSTransactionService:
    """خدمة إدارة معاملات نقاط البيع"""

    @staticmethod
    def create_transaction(db: Session, transaction: POSTransactionCreate) -> POSTransaction:
        """إنشاء معاملة نقاط بيع جديدة"""
        # التحقق من وجود جلسة مفتوحة
        session = db.query(POSSession).filter(
            and_(
                POSSession.id == transaction.session_id,
                POSSession.status == POSSessionStatusEnum.OPEN
            )
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No open session found"
            )
        
        # إنشاء رقم المعاملة
        transaction_count = db.query(POSTransaction).filter(
            POSTransaction.session_id == transaction.session_id
        ).count()
        transaction_number = f"TXN-{session.session_number}-{transaction_count + 1:06d}"
        
        # حساب الإجماليات
        subtotal = sum(item.line_total for item in transaction.items)
        total_amount = subtotal - transaction.discount_amount + transaction.tax_amount
        
        # التحقق من المدفوعات
        total_payments = sum(payment.amount for payment in transaction.payments)
        if total_payments < total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient payment amount"
            )
        
        change_amount = total_payments - total_amount
        
        # إنشاء المعاملة
        db_transaction = POSTransaction(
            **transaction.dict(exclude={'items', 'payments'}),
            transaction_number=transaction_number,
            subtotal=subtotal,
            total_amount=total_amount,
            amount_paid=total_payments,
            change_amount=change_amount
        )
        db.add(db_transaction)
        db.flush()  # للحصول على ID المعاملة
        
        # إنشاء عناصر المعاملة
        for item_data in transaction.items:
            # التحقق من توفر المنتج في المخزون
            if not POSTransactionService._check_stock_availability(
                db, item_data.product_id, session.terminal.warehouse_id, item_data.quantity
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {item_data.product_id}"
                )
            
            db_item = POSTransactionItem(
                **item_data.dict(),
                transaction_id=db_transaction.id
            )
            db.add(db_item)
            
            # تحديث المخزون
            POSTransactionService._update_inventory(
                db, item_data.product_id, session.terminal.warehouse_id, 
                -item_data.quantity, transaction_number
            )
        
        # إنشاء المدفوعات
        for payment_data in transaction.payments:
            db_payment = POSPayment(
                **payment_data.dict(),
                transaction_id=db_transaction.id
            )
            db.add(db_payment)
        
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    @staticmethod
    def void_transaction(db: Session, transaction_id: int, void_reason: str, user_id: int) -> POSTransaction:
        """إلغاء معاملة نقاط البيع"""
        transaction = db.query(POSTransaction).filter(POSTransaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        if transaction.transaction_type == POSTransactionTypeEnum.VOID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction is already voided"
            )
        
        # إعادة المخزون
        for item in transaction.pos_transaction_items:
            POSTransactionService._update_inventory(
                db, item.product_id, transaction.terminal.warehouse_id,
                item.quantity, f"VOID-{transaction.transaction_number}"
            )
        
        # تحديث المعاملة
        transaction.transaction_type = POSTransactionTypeEnum.VOID
        transaction.void_reason = void_reason
        transaction.voided_at = datetime.utcnow()
        transaction.voided_by = user_id
        
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def _check_stock_availability(db: Session, product_id: int, warehouse_id: int, 
                                 required_quantity: Decimal) -> bool:
        """التحقق من توفر المخزون"""
        inventory_item = db.query(InventoryItem).filter(
            and_(
                InventoryItem.product_id == product_id,
                InventoryItem.warehouse_id == warehouse_id
            )
        ).first()
        
        if not inventory_item:
            return False
        
        available_quantity = inventory_item.quantity_on_hand - inventory_item.quantity_reserved
        return available_quantity >= required_quantity

    @staticmethod
    def _update_inventory(db: Session, product_id: int, warehouse_id: int, 
                         quantity_change: Decimal, reference: str):
        """تحديث المخزون"""
        from app.services.inventory_service import InventoryService
        from app.schemas.inventory import StockMovementCreate
        
        inventory_item = InventoryService.get_or_create_inventory_item(
            db, product_id, warehouse_id
        )
        
        movement_type = "OUT" if quantity_change < 0 else "IN"
        stock_movement = StockMovementCreate(
            inventory_item_id=inventory_item.id,
            movement_type=movement_type,
            reference_type="POS",
            quantity=abs(quantity_change),
            notes=f"POS Transaction: {reference}"
        )
        
        InventoryService.record_stock_movement(db, stock_movement)


class POSReportService:
    """خدمة تقارير نقاط البيع"""

    @staticmethod
    def get_sales_report(db: Session, from_date: datetime, to_date: datetime,
                        terminal_id: Optional[int] = None) -> POSSalesReport:
        """تقرير مبيعات نقاط البيع"""
        query = db.query(POSTransaction).filter(
            and_(
                POSTransaction.transaction_date >= from_date,
                POSTransaction.transaction_date <= to_date,
                POSTransaction.transaction_type == POSTransactionTypeEnum.SALE
            )
        )
        
        if terminal_id:
            query = query.filter(POSTransaction.terminal_id == terminal_id)
        
        transactions = query.all()
        
        # حساب الإجماليات
        total_transactions = len(transactions)
        total_sales = sum(t.total_amount for t in transactions)
        total_refunds = sum(t.total_amount for t in transactions 
                           if t.transaction_type == POSTransactionTypeEnum.REFUND)
        total_discounts = sum(t.discount_amount for t in transactions)
        total_tax = sum(t.tax_amount for t in transactions)
        net_sales = total_sales - total_refunds
        
        # تجميع المدفوعات حسب الطريقة
        payment_methods = {}
        for transaction in transactions:
            for payment in transaction.pos_payments:
                method = payment.payment_method.value
                if method not in payment_methods:
                    payment_methods[method] = Decimal(0)
                payment_methods[method] += payment.amount
        
        payment_breakdown = [
            {"method": method, "amount": amount}
            for method, amount in payment_methods.items()
        ]
        
        return POSSalesReport(
            from_date=from_date,
            to_date=to_date,
            terminal_id=terminal_id,
            total_transactions=total_transactions,
            total_sales=total_sales,
            total_refunds=total_refunds,
            total_discounts=total_discounts,
            total_tax=total_tax,
            net_sales=net_sales,
            payment_methods=payment_breakdown
        )

    @staticmethod
    def get_session_report(db: Session, session_id: int) -> POSSessionReport:
        """تقرير جلسة نقاط البيع"""
        session = db.query(POSSession).filter(POSSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        cash_difference = session.closing_cash_amount - session.opening_cash_amount - session.total_sales
        
        return POSSessionReport(
            session_id=session.id,
            session_number=session.session_number,
            terminal_code=session.terminal.terminal_code,
            cashier_name=session.user.username if session.user else "Unknown",
            start_time=session.start_time,
            end_time=session.end_time,
            status=session.status,
            opening_cash=session.opening_cash_amount,
            closing_cash=session.closing_cash_amount,
            total_sales=session.total_sales,
            total_transactions=session.transaction_count,
            cash_difference=cash_difference
        )


class POSDiscountService:
    """خدمة إدارة خصومات نقاط البيع"""

    @staticmethod
    def create_discount(db: Session, discount: POSDiscountCreate) -> POSDiscount:
        """إنشاء خصم جديد"""
        # التحقق من عدم تكرار رمز الخصم
        existing_discount = db.query(POSDiscount).filter(
            POSDiscount.code == discount.code
        ).first()
        if existing_discount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code already exists"
            )
        
        db_discount = POSDiscount(**discount.dict())
        db.add(db_discount)
        db.commit()
        db.refresh(db_discount)
        return db_discount

    @staticmethod
    def validate_discount(db: Session, discount_code: str, transaction_amount: Decimal,
                         product_ids: List[int]) -> Optional[POSDiscount]:
        """التحقق من صحة الخصم"""
        discount = db.query(POSDiscount).filter(
            and_(
                POSDiscount.code == discount_code,
                POSDiscount.is_active == True
            )
        ).first()
        
        if not discount:
            return None
        
        # التحقق من صحة التاريخ
        now = datetime.utcnow()
        if discount.valid_from and now < discount.valid_from:
            return None
        if discount.valid_to and now > discount.valid_to:
            return None
        
        # التحقق من حد الاستخدام
        if discount.usage_limit and discount.usage_count >= discount.usage_limit:
            return None
        
        # التحقق من الحد الأدنى للمبلغ
        if discount.min_amount and transaction_amount < discount.min_amount:
            return None
        
        # التحقق من الحد الأقصى للمبلغ
        if discount.max_amount and transaction_amount > discount.max_amount:
            return None
        
        # التحقق من المنتجات المسموحة
        if discount.applicable_products:
            applicable_products = json.loads(discount.applicable_products)
            if not any(pid in applicable_products for pid in product_ids):
                return None
        
        return discount

    @staticmethod
    def apply_discount(db: Session, discount: POSDiscount, amount: Decimal) -> Decimal:
        """تطبيق الخصم"""
        if discount.discount_type == "PERCENTAGE":
            discount_amount = amount * (discount.discount_value / 100)
        else:  # FIXED
            discount_amount = discount.discount_value
        
        # تحديث عداد الاستخدام
        discount.usage_count += 1
        db.commit()
        
        return min(discount_amount, amount)  # لا يتجاوز الخصم المبلغ الأصلي


class POSService:
    """خدمة نقاط البيع الرئيسية - Main POS Service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.terminal_service = POSTerminalService()
        self.session_service = POSSessionService()
        self.transaction_service = POSTransactionService()
        self.discount_service = POSDiscountService()
        self.report_service = POSReportService()
    
    # Terminal methods
    def get_terminals(self, branch_id: int = None, active_only: bool = True):
        query = self.db.query(POSTerminal)
        if branch_id:
            query = query.filter(POSTerminal.branch_id == branch_id)
        if active_only:
            query = query.filter(POSTerminal.is_active == True)
        return query.all()
    
    def create_terminal(self, terminal: POSTerminalCreate):
        return self.terminal_service.create_terminal(self.db, terminal)
    
    def get_terminal(self, terminal_id: int):
        return self.terminal_service.get_terminal(self.db, terminal_id)
    
    def update_terminal(self, terminal_id: int, terminal: POSTerminalUpdate):
        return self.terminal_service.update_terminal(self.db, terminal_id, terminal)
    
    # Session methods
    def get_sessions(self, terminal_id: int = None, cashier_id: int = None, date_from: date = None, date_to: date = None, status: str = None):
        query = self.db.query(POSSession)
        if terminal_id:
            query = query.filter(POSSession.terminal_id == terminal_id)
        if cashier_id:
            query = query.filter(POSSession.cashier_id == cashier_id)
        if date_from:
            query = query.filter(POSSession.start_time >= date_from)
        if date_to:
            query = query.filter(POSSession.end_time <= date_to)
        if status:
            query = query.filter(POSSession.status == status)
        return query.order_by(POSSession.start_time.desc()).all()
    
    def create_session(self, session: POSSessionCreate):
        return self.session_service.create_session(self.db, session)
    
    def get_session(self, session_id: int):
        return self.session_service.get_session(self.db, session_id)
    
    def close_session(self, session_id: int):
        return self.session_service.close_session(self.db, session_id)
    
    def get_active_session(self, terminal_id: int):
        return self.session_service.get_active_session(self.db, terminal_id)
    
    # Transaction methods
    def get_transactions(self, session_id: int = None, customer_id: int = None, date_from: datetime = None, date_to: datetime = None, status: str = None):
        query = self.db.query(POSTransaction)
        if session_id:
            query = query.filter(POSTransaction.session_id == session_id)
        if customer_id:
            query = query.filter(POSTransaction.customer_id == customer_id)
        if date_from:
            query = query.filter(POSTransaction.transaction_time >= date_from)
        if date_to:
            query = query.filter(POSTransaction.transaction_time <= date_to)
        if status:
            query = query.filter(POSTransaction.status == status)
        return query.order_by(POSTransaction.transaction_time.desc()).all()
    
    def create_transaction(self, transaction: POSTransactionCreate):
        return self.transaction_service.create_transaction(self.db, transaction)
    
    def get_transaction(self, transaction_id: int):
        return self.transaction_service.get_transaction(self.db, transaction_id)
    
    def complete_transaction(self, transaction_id: int):
        return self.transaction_service.complete_transaction(self.db, transaction_id)
    
    def void_transaction(self, transaction_id: int, reason: str):
        return self.transaction_service.void_transaction(self.db, transaction_id, reason)
    
    def process_refund(self, transaction_id: int, items: List[dict], reason: str):
        return self.transaction_service.process_refund(self.db, transaction_id, items, reason)
    
    # Payment methods
    def get_payments(self, transaction_id: int = None, payment_method: str = None):
        query = self.db.query(POSPayment)
        if transaction_id:
            query = query.filter(POSPayment.transaction_id == transaction_id)
        if payment_method:
            query = query.filter(POSPayment.payment_method == payment_method)
        return query.all()
    
    def create_payment(self, payment):
        db_payment = POSPayment(**payment.dict())
        self.db.add(db_payment)
        self.db.commit()
        self.db.refresh(db_payment)
        return db_payment
    
    # Discount methods
    def get_discounts(self, active_only: bool = True, discount_type: str = None):
        return self.discount_service.get_discounts(self.db, active_only, discount_type)
    
    def create_discount(self, discount: POSDiscountCreate):
        return self.discount_service.create_discount(self.db, discount)
    
    def get_discount(self, discount_id: int):
        return self.discount_service.get_discount(self.db, discount_id)
    
    def update_discount(self, discount_id: int, discount: POSDiscountUpdate):
        return self.discount_service.update_discount(self.db, discount_id, discount)
    
    def validate_discount(self, discount_id: int, transaction_total: float, customer_id: int = None):
        return self.discount_service.validate_discount(self.db, discount_id, transaction_total, customer_id)
    
    # Promotion methods - simple implementations
    def get_promotions(self, active_only: bool = True, promotion_type: str = None):
        query = self.db.query(POSPromotion)
        if active_only:
            query = query.filter(POSPromotion.is_active == True)
        if promotion_type:
            query = query.filter(POSPromotion.promotion_type == promotion_type)
        return query.all()
    
    def create_promotion(self, promotion: POSPromotionCreate):
        db_promotion = POSPromotion(**promotion.dict())
        self.db.add(db_promotion)
        self.db.commit()
        self.db.refresh(db_promotion)
        return db_promotion
    
    def get_promotion(self, promotion_id: int):
        return self.db.query(POSPromotion).filter(POSPromotion.id == promotion_id).first()
    
    def update_promotion(self, promotion_id: int, promotion: POSPromotionUpdate):
        db_promotion = self.get_promotion(promotion_id)
        if db_promotion:
            for field, value in promotion.dict(exclude_unset=True).items():
                setattr(db_promotion, field, value)
            self.db.commit()
            self.db.refresh(db_promotion)
        return db_promotion
    
    # Inventory checks
    def check_stock_availability(self, product_id: int, quantity: int):
        inventory_item = self.db.query(InventoryItem).filter(InventoryItem.product_id == product_id).first()
        if inventory_item:
            return inventory_item.quantity_on_hand >= quantity
        return False
    
    def get_product_stock(self, product_id: int):
        inventory_item = self.db.query(InventoryItem).filter(InventoryItem.product_id == product_id).first()
        return inventory_item.quantity_on_hand if inventory_item else 0
    
    # Reports
    def generate_sales_report(self, date_from: date, date_to: date, terminal_id: int = None, cashier_id: int = None):
        query = self.db.query(POSTransaction).filter(
            POSTransaction.transaction_time >= date_from,
            POSTransaction.transaction_time <= date_to,
            POSTransaction.status == "COMPLETED"
        )
        
        if terminal_id:
            query = query.join(POSSession).filter(POSSession.terminal_id == terminal_id)
        if cashier_id:
            query = query.join(POSSession).filter(POSSession.cashier_id == cashier_id)
        
        transactions = query.all()
        
        total_sales = sum(t.total_amount for t in transactions)
        total_transactions = len(transactions)
        average_sale = total_sales / total_transactions if total_transactions > 0 else 0
        
        return POSSalesReport(
            period_start=date_from,
            period_end=date_to,
            total_sales=total_sales,
            total_transactions=total_transactions,
            average_sale_amount=average_sale,
            transactions=transactions
        )
    
    def generate_session_reports(self, date_from: date, date_to: date, terminal_id: int = None):
        query = self.db.query(POSSession).filter(
            POSSession.start_time >= date_from,
            POSSession.end_time <= date_to
        )
        
        if terminal_id:
            query = query.filter(POSSession.terminal_id == terminal_id)
        
        sessions = query.all()
        reports = []
        
        for session in sessions:
            transactions = self.db.query(POSTransaction).filter(
                POSTransaction.session_id == session.id
            ).all()
            
            total_sales = sum(t.total_amount for t in transactions if t.status == "COMPLETED")
            
            reports.append(POSSessionReport(
                session_id=session.id,
                terminal_name=session.terminal.name if session.terminal else "",
                cashier_name="",  # Add actual cashier name if available
                start_time=session.start_time,
                end_time=session.end_time,
                total_sales=total_sales,
                transaction_count=len(transactions)
            ))
        
        return reports
    
    def generate_product_sales_report(self, date_from: date, date_to: date, product_id: int = None, category_id: int = None):
        # This would require joining with transaction items and products
        # For now, return a simple structure
        return []
