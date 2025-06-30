"""
Cash Flow Management Service
خدمة إدارة التدفق النقدي

Business logic for cash flow operations, transfers, and dashboard data.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, case
from typing import List, Optional, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
from fastapi import HTTPException, status

from app.models.cashflow import (
    CashBox, SalespersonRegion, CashTransaction, CashTransfer, CashFlowSummary,
    CashBoxTypeEnum, TransferStatusEnum, CashPaymentMethodEnum, RegionEnum
)
from app.models.branch import Branch
from app.models.user import User
from app.schemas.cashflow import (
    CashBoxCreate, CashBoxUpdate, SalespersonRegionCreate, SalespersonRegionUpdate,
    CashTransactionCreate, CashTransactionUpdate, CashTransferCreate, CashTransferUpdate,
    CashTransferApproval, BranchCashFlowDashboard, SalespersonCashFlowDashboard,
    CashFlowDashboardData, TransferReceiptData
)


class CashBoxService:
    """خدمة إدارة صناديق النقد"""

    @staticmethod
    def create_cash_box(db: Session, cash_box: CashBoxCreate, created_by: int) -> CashBox:
        """إنشاء صندوق نقد جديد"""
        # التحقق من عدم تكرار الكود
        existing_box = db.query(CashBox).filter(CashBox.code == cash_box.code).first()
        if existing_box:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cash box code already exists - كود صندوق النقد موجود مسبقاً"
            )
        
        # التحقق من صحة البيانات
        if cash_box.box_type == CashBoxTypeEnum.SALESPERSON and not cash_box.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Salesperson cash box must have a user assigned - صندوق مندوب المبيعات يجب أن يكون له مستخدم"
            )
        
        # التحقق من وجود الفرع
        branch = db.query(Branch).filter(Branch.id == cash_box.branch_id).first()
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Branch not found - الفرع غير موجود"
            )
        
        # التحقق من وجود المستخدم إذا كان مطلوباً
        if cash_box.user_id:
            user = db.query(User).filter(User.id == cash_box.user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found - المستخدم غير موجود"
                )
        
        db_cash_box = CashBox(**cash_box.dict(), created_by=created_by)
        db.add(db_cash_box)
        db.commit()
        db.refresh(db_cash_box)
        return db_cash_box

    @staticmethod
    def get_cash_boxes(db: Session, branch_id: Optional[int] = None, 
                      user_id: Optional[int] = None, box_type: Optional[str] = None,
                      active_only: bool = True) -> List[CashBox]:
        """الحصول على قائمة صناديق النقد"""
        query = db.query(CashBox)
        
        if branch_id:
            query = query.filter(CashBox.branch_id == branch_id)
        if user_id:
            query = query.filter(CashBox.user_id == user_id)
        if box_type:
            query = query.filter(CashBox.box_type == box_type)
        if active_only:
            query = query.filter(CashBox.is_active == True)
        
        return query.order_by(CashBox.code).all()

    @staticmethod
    def get_cash_box(db: Session, cash_box_id: int) -> CashBox:
        """الحصول على صندوق نقد محدد"""
        cash_box = db.query(CashBox).filter(CashBox.id == cash_box_id).first()
        if not cash_box:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cash box not found - صندوق النقد غير موجود"
            )
        return cash_box

    @staticmethod
    def update_cash_box(db: Session, cash_box_id: int, cash_box_update: CashBoxUpdate) -> CashBox:
        """تحديث بيانات صندوق النقد"""
        cash_box = CashBoxService.get_cash_box(db, cash_box_id)
        
        update_data = cash_box_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cash_box, field, value)
        
        cash_box.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(cash_box)
        return cash_box

    @staticmethod
    def update_cash_box_balance(db: Session, cash_box_id: int, currency_code: str,
                               amount: Decimal, is_digital: bool, is_debit: bool) -> CashBox:
        """تحديث رصيد صندوق النقد"""
        cash_box = CashBoxService.get_cash_box(db, cash_box_id)
        
        # تحديد الحقل المناسب للرصيد
        balance_field = f"balance_{currency_code.lower()}_{'digital' if is_digital else 'cash'}"
        
        if not hasattr(cash_box, balance_field):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency or payment method - عملة أو طريقة دفع غير صحيحة"
            )
        
        current_balance = getattr(cash_box, balance_field)
        
        if is_debit:
            new_balance = current_balance + amount
        else:
            new_balance = current_balance - amount
            if new_balance < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient balance - رصيد غير كافي"
                )
        
        setattr(cash_box, balance_field, new_balance)
        cash_box.last_transaction_date = datetime.utcnow()
        cash_box.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(cash_box)
        return cash_box


class SalespersonRegionService:
    """خدمة إدارة مناطق مندوبي المبيعات"""

    @staticmethod
    def assign_region(db: Session, region_data: SalespersonRegionCreate, assigned_by: int) -> SalespersonRegion:
        """تعيين منطقة لمندوب مبيعات"""
        # التحقق من وجود المستخدم
        user = db.query(User).filter(User.id == region_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found - المستخدم غير موجود"
            )
        
        # التحقق من عدم تكرار تعيين نفس المنطقة للمستخدم
        existing_assignment = db.query(SalespersonRegion).filter(
            and_(SalespersonRegion.user_id == region_data.user_id,
                 SalespersonRegion.region == region_data.region,
                 SalespersonRegion.is_active == True)
        ).first()
        
        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region already assigned to this user - المنطقة مُعيّنة مسبقاً لهذا المستخدم"
            )
        
        # إذا كانت المنطقة الأساسية، إلغاء تفعيل المناطق الأساسية الأخرى
        if region_data.is_primary:
            db.query(SalespersonRegion).filter(
                and_(SalespersonRegion.user_id == region_data.user_id,
                     SalespersonRegion.is_primary == True)
            ).update({"is_primary": False})
        
        db_region = SalespersonRegion(**region_data.dict(), assigned_by=assigned_by)
        db.add(db_region)
        db.commit()
        db.refresh(db_region)
        return db_region

    @staticmethod
    def get_salesperson_regions(db: Session, user_id: int, active_only: bool = True) -> List[SalespersonRegion]:
        """الحصول على مناطق مندوب مبيعات"""
        query = db.query(SalespersonRegion).filter(SalespersonRegion.user_id == user_id)
        if active_only:
            query = query.filter(SalespersonRegion.is_active == True)
        return query.order_by(desc(SalespersonRegion.is_primary), SalespersonRegion.region).all()

    @staticmethod
    def update_region_assignment(db: Session, assignment_id: int, 
                                update_data: SalespersonRegionUpdate) -> SalespersonRegion:
        """تحديث تعيين منطقة"""
        assignment = db.query(SalespersonRegion).filter(SalespersonRegion.id == assignment_id).first()
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Region assignment not found - تعيين المنطقة غير موجود"
            )
        
        # إذا كانت المنطقة الأساسية، إلغاء تفعيل المناطق الأساسية الأخرى
        if update_data.is_primary and update_data.is_primary != assignment.is_primary:
            db.query(SalespersonRegion).filter(
                and_(SalespersonRegion.user_id == assignment.user_id,
                     SalespersonRegion.is_primary == True,
                     SalespersonRegion.id != assignment_id)
            ).update({"is_primary": False})
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(assignment, field, value)
        
        db.commit()
        db.refresh(assignment)
        return assignment


class CashTransactionService:
    """خدمة إدارة المعاملات النقدية"""

    @staticmethod
    def create_transaction(db: Session, transaction: CashTransactionCreate, created_by: int) -> CashTransaction:
        """إنشاء معاملة نقدية"""
        # التحقق من وجود صندوق النقد
        cash_box = db.query(CashBox).filter(CashBox.id == transaction.cash_box_id).first()
        if not cash_box:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cash box not found - صندوق النقد غير موجود"
            )
        
        # إنشاء رقم المعاملة
        transaction_number = CashTransactionService._generate_transaction_number(db, transaction.transaction_type)
        
        # إنشاء المعاملة
        db_transaction = CashTransaction(
            **transaction.dict(),
            transaction_number=transaction_number,
            created_by=created_by
        )
        db.add(db_transaction)
        db.flush()  # للحصول على ID المعاملة
        
        # تحديث رصيد صندوق النقد
        is_debit = transaction.transaction_type in ['RECEIPT', 'TRANSFER_IN']
        is_digital = transaction.payment_method in [CashPaymentMethodEnum.DIGITAL, CashPaymentMethodEnum.BANK_TRANSFER]
        
        CashBoxService.update_cash_box_balance(
            db, transaction.cash_box_id, transaction.currency_code,
            transaction.amount, is_digital, is_debit
        )
        
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    @staticmethod
    def _generate_transaction_number(db: Session, transaction_type: str) -> str:
        """إنشاء رقم معاملة فريد"""
        today = datetime.now().strftime("%Y%m%d")
        prefix_map = {
            'RECEIPT': 'RCP',
            'PAYMENT': 'PAY',
            'TRANSFER_IN': 'TIN',
            'TRANSFER_OUT': 'TOU'
        }
        prefix = prefix_map.get(transaction_type, 'TXN')
        
        # البحث عن آخر رقم في نفس اليوم
        last_transaction = db.query(CashTransaction).filter(
            CashTransaction.transaction_number.like(f"{prefix}-{today}-%")
        ).order_by(desc(CashTransaction.transaction_number)).first()
        
        if last_transaction:
            last_number = int(last_transaction.transaction_number.split('-')[-1])
            next_number = last_number + 1
        else:
            next_number = 1
        
        return f"{prefix}-{today}-{next_number:04d}"

    @staticmethod
    def get_transactions(db: Session, cash_box_id: Optional[int] = None,
                        user_id: Optional[int] = None, transaction_type: Optional[str] = None,
                        start_date: Optional[date] = None, end_date: Optional[date] = None,
                        skip: int = 0, limit: int = 100) -> List[CashTransaction]:
        """الحصول على قائمة المعاملات النقدية"""
        query = db.query(CashTransaction)
        
        if cash_box_id:
            query = query.filter(CashTransaction.cash_box_id == cash_box_id)
        if user_id:
            # Get transactions for all cash boxes of this user
            user_cash_boxes = db.query(CashBox.id).filter(CashBox.user_id == user_id).subquery()
            query = query.filter(CashTransaction.cash_box_id.in_(user_cash_boxes))
        if transaction_type:
            query = query.filter(CashTransaction.transaction_type == transaction_type)
        if start_date:
            query = query.filter(CashTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(CashTransaction.transaction_date <= end_date)
        
        return query.order_by(desc(CashTransaction.transaction_date)).offset(skip).limit(limit).all()

    @staticmethod
    def get_transaction(db: Session, transaction_id: int) -> CashTransaction:
        """الحصول على معاملة نقدية محددة"""
        transaction = db.query(CashTransaction).filter(CashTransaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found - المعاملة غير موجودة"
            )
        return transaction


class CashTransferService:
    """خدمة إدارة التحويلات النقدية"""

    @staticmethod
    def create_transfer(db: Session, transfer: CashTransferCreate, requested_by: int) -> CashTransfer:
        """إنشاء طلب تحويل نقدي"""
        # التحقق من وجود صناديق النقد
        from_box = db.query(CashBox).filter(CashBox.id == transfer.from_cash_box_id).first()
        to_box = db.query(CashBox).filter(CashBox.id == transfer.to_cash_box_id).first()
        
        if not from_box:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source cash box not found - صندوق النقد المصدر غير موجود"
            )
        if not to_box:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination cash box not found - صندوق النقد المستهدف غير موجود"
            )
        
        # التحقق من الرصيد الكافي
        is_digital = transfer.payment_method in [CashPaymentMethodEnum.DIGITAL, CashPaymentMethodEnum.BANK_TRANSFER]
        balance_field = f"balance_{transfer.currency_code.lower()}_{'digital' if is_digital else 'cash'}"
        
        current_balance = getattr(from_box, balance_field)
        if current_balance < transfer.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance for transfer - رصيد غير كافي للتحويل"
            )
        
        # إنشاء رقم التحويل
        transfer_number = CashTransferService._generate_transfer_number(db)
        
        # إنشاء التحويل
        db_transfer = CashTransfer(
            **transfer.dict(),
            transfer_number=transfer_number,
            requested_by=requested_by
        )
        db.add(db_transfer)
        db.commit()
        db.refresh(db_transfer)
        return db_transfer

    @staticmethod
    def _generate_transfer_number(db: Session) -> str:
        """إنشاء رقم تحويل فريد"""
        today = datetime.now().strftime("%Y%m%d")
        
        # البحث عن آخر رقم في نفس اليوم
        last_transfer = db.query(CashTransfer).filter(
            CashTransfer.transfer_number.like(f"TRF-{today}-%")
        ).order_by(desc(CashTransfer.transfer_number)).first()
        
        if last_transfer:
            last_number = int(last_transfer.transfer_number.split('-')[-1])
            next_number = last_number + 1
        else:
            next_number = 1
        
        return f"TRF-{today}-{next_number:04d}"

    @staticmethod
    def approve_transfer(db: Session, transfer_id: int, approval: CashTransferApproval, 
                        approved_by: int) -> CashTransfer:
        """الموافقة على التحويل أو رفضه"""
        transfer = db.query(CashTransfer).filter(CashTransfer.id == transfer_id).first()
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found - التحويل غير موجود"
            )
        
        if transfer.status != TransferStatusEnum.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfer is not pending approval - التحويل ليس في انتظار الموافقة"
            )
        
        transfer.status = approval.status
        transfer.admin_notes = approval.admin_notes
        transfer.approved_by = approved_by
        transfer.approved_date = datetime.utcnow()
        
        # إذا تمت الموافقة، تنفيذ التحويل
        if approval.status == TransferStatusEnum.APPROVED:
            CashTransferService._execute_transfer(db, transfer)
        
        db.commit()
        db.refresh(transfer)
        return transfer

    @staticmethod
    def _execute_transfer(db: Session, transfer: CashTransfer):
        """تنفيذ التحويل النقدي"""
        is_digital = transfer.payment_method in [CashPaymentMethodEnum.DIGITAL, CashPaymentMethodEnum.BANK_TRANSFER]
        
        # خصم من الصندوق المصدر
        CashBoxService.update_cash_box_balance(
            db, transfer.from_cash_box_id, transfer.currency_code,
            transfer.amount, is_digital, False
        )
        
        # إضافة للصندوق المستهدف
        CashBoxService.update_cash_box_balance(
            db, transfer.to_cash_box_id, transfer.currency_code,
            transfer.amount, is_digital, True
        )
        
        # إنشاء معاملات للتوثيق
        # معاملة الخصم
        CashTransactionService.create_transaction(db, CashTransactionCreate(
            cash_box_id=transfer.from_cash_box_id,
            transaction_type='TRANSFER_OUT',
            payment_method=transfer.payment_method,
            currency_code=transfer.currency_code,
            amount=transfer.amount,
            reference_type='TRANSFER',
            reference_id=transfer.id,
            reference_number=transfer.transfer_number,
            description_ar=f"تحويل إلى {transfer.transfer_number}",
            description_en=f"Transfer to {transfer.transfer_number}",
            transaction_date=datetime.utcnow()
        ), transfer.requested_by)
        
        # معاملة الإضافة
        CashTransactionService.create_transaction(db, CashTransactionCreate(
            cash_box_id=transfer.to_cash_box_id,
            transaction_type='TRANSFER_IN',
            payment_method=transfer.payment_method,
            currency_code=transfer.currency_code,
            amount=transfer.amount,
            reference_type='TRANSFER',
            reference_id=transfer.id,
            reference_number=transfer.transfer_number,
            description_ar=f"تحويل من {transfer.transfer_number}",
            description_en=f"Transfer from {transfer.transfer_number}",
            transaction_date=datetime.utcnow()
        ), transfer.approved_by)

    @staticmethod
    def receive_transfer(db: Session, transfer_id: int, received_by: int) -> CashTransfer:
        """تأكيد استلام التحويل"""
        transfer = db.query(CashTransfer).filter(CashTransfer.id == transfer_id).first()
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found - التحويل غير موجود"
            )
        
        if transfer.status != TransferStatusEnum.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfer is not approved - التحويل غير موافق عليه"
            )
        
        transfer.status = TransferStatusEnum.RECEIVED
        transfer.received_by = received_by
        transfer.received_date = datetime.utcnow()
        
        db.commit()
        db.refresh(transfer)
        return transfer

    @staticmethod
    def get_transfers(db: Session, user_id: Optional[int] = None, 
                     from_cash_box_id: Optional[int] = None, to_cash_box_id: Optional[int] = None,
                     status: Optional[TransferStatusEnum] = None, skip: int = 0, limit: int = 100) -> List[CashTransfer]:
        """الحصول على قائمة التحويلات"""
        query = db.query(CashTransfer)
        
        if user_id:
            # Get transfers for all cash boxes of this user
            user_cash_boxes = db.query(CashBox.id).filter(CashBox.user_id == user_id).subquery()
            query = query.filter(
                or_(CashTransfer.from_cash_box_id.in_(user_cash_boxes),
                    CashTransfer.to_cash_box_id.in_(user_cash_boxes))
            )
        if from_cash_box_id:
            query = query.filter(CashTransfer.from_cash_box_id == from_cash_box_id)
        if to_cash_box_id:
            query = query.filter(CashTransfer.to_cash_box_id == to_cash_box_id)
        if status:
            query = query.filter(CashTransfer.status == status)
        
        return query.order_by(desc(CashTransfer.requested_date)).offset(skip).limit(limit).all()

    @staticmethod
    def get_transfer(db: Session, transfer_id: int) -> CashTransfer:
        """الحصول على تحويل نقدي محدد"""
        transfer = db.query(CashTransfer).filter(CashTransfer.id == transfer_id).first()
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found - التحويل غير موجود"
            )
        return transfer

    @staticmethod
    def update_transfer(db: Session, transfer_id: int, transfer_update: CashTransferUpdate) -> CashTransfer:
        """تحديث تفاصيل التحويل"""
        transfer = CashTransferService.get_transfer(db, transfer_id)
        
        # Only allow updates if transfer is still pending
        if transfer.status != TransferStatusEnum.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only update pending transfers - يمكن تحديث التحويلات المعلقة فقط"
            )
        
        update_data = transfer_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transfer, field, value)
        
        transfer.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(transfer)
        return transfer


class CashFlowDashboardService:
    """خدمة لوحة معلومات التدفق النقدي"""

    @staticmethod
    def get_branch_dashboard(db: Session, branch_id: int) -> BranchCashFlowDashboard:
        """الحصول على بيانات لوحة معلومات الفرع"""
        branch = db.query(Branch).filter(Branch.id == branch_id).first()
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Branch not found - الفرع غير موجود"
            )
        
        # إحصائيات الصناديق والمندوبين
        total_cash_boxes = db.query(CashBox).filter(
            and_(CashBox.branch_id == branch_id, CashBox.is_active == True)
        ).count()
        
        active_salespeople = db.query(User).filter(
            and_(User.branch_id == branch_id, User.is_salesperson == True, User.is_active == True)
        ).count()
        
        # الأرصدة الإجمالية
        balances = db.query(
            func.sum(CashBox.balance_iqd_cash).label('total_iqd_cash'),
            func.sum(CashBox.balance_iqd_digital).label('total_iqd_digital'),
            func.sum(CashBox.balance_usd_cash).label('total_usd_cash'),
            func.sum(CashBox.balance_usd_digital).label('total_usd_digital'),
            func.sum(CashBox.balance_rmb_cash).label('total_rmb_cash'),
            func.sum(CashBox.balance_rmb_digital).label('total_rmb_digital')
        ).filter(
            and_(CashBox.branch_id == branch_id, CashBox.is_active == True)
        ).first()
        
        # نشاط اليوم
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_activity = db.query(
            func.sum(case((CashTransaction.transaction_type.in_(['RECEIPT', 'TRANSFER_IN']), 
                          CashTransaction.amount), else_=0)).label('receipts_iqd'),
            func.sum(case((CashTransaction.transaction_type.in_(['PAYMENT', 'TRANSFER_OUT']), 
                          CashTransaction.amount), else_=0)).label('payments_iqd'),
            func.count(CashTransaction.id).label('transactions_count')
        ).join(CashBox).filter(
            and_(CashBox.branch_id == branch_id,
                 CashTransaction.transaction_date >= today_start,
                 CashTransaction.transaction_date <= today_end,
                 CashTransaction.currency_code == 'IQD')
        ).first()
        
        # التحويلات المعلقة
        pending_transfers_in = db.query(CashTransfer).join(
            CashBox, CashTransfer.to_cash_box_id == CashBox.id
        ).filter(
            and_(CashBox.branch_id == branch_id,
                 CashTransfer.status == TransferStatusEnum.PENDING)
        ).count()
        
        pending_transfers_out = db.query(CashTransfer).join(
            CashBox, CashTransfer.from_cash_box_id == CashBox.id
        ).filter(
            and_(CashBox.branch_id == branch_id,
                 CashTransfer.status == TransferStatusEnum.PENDING)
        ).count()
        
        return BranchCashFlowDashboard(
            branch_id=branch_id,
            branch_name=branch.name,
            branch_type=getattr(branch, 'branch_type', ''),
            total_cash_boxes=total_cash_boxes,
            active_salespeople=active_salespeople,
            total_iqd_cash=balances.total_iqd_cash or 0,
            total_iqd_digital=balances.total_iqd_digital or 0,
            total_usd_cash=balances.total_usd_cash or 0,
            total_usd_digital=balances.total_usd_digital or 0,
            total_rmb_cash=balances.total_rmb_cash or 0,
            total_rmb_digital=balances.total_rmb_digital or 0,
            today_receipts_iqd=today_activity.receipts_iqd or 0,
            today_payments_iqd=today_activity.payments_iqd or 0,
            today_receipts_usd=0,  # TODO: Calculate USD separately
            today_payments_usd=0,  # TODO: Calculate USD separately
            today_transactions_count=today_activity.transactions_count or 0,
            pending_transfers_in=pending_transfers_in,
            pending_transfers_out=pending_transfers_out,
            pending_transfers_amount_iqd=0,  # TODO: Calculate pending amounts
            pending_transfers_amount_usd=0   # TODO: Calculate pending amounts
        )

    @staticmethod
    def get_salesperson_dashboard(db: Session, user_id: int) -> SalespersonCashFlowDashboard:
        """الحصول على بيانات لوحة معلومات مندوب المبيعات"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found - المستخدم غير موجود"
            )
        
        # المناطق المُعيّنة
        regions = db.query(SalespersonRegion.region).filter(
            and_(SalespersonRegion.user_id == user_id, SalespersonRegion.is_active == True)
        ).all()
        
        # صندوق النقد الخاص بالمندوب
        cash_box = db.query(CashBox).filter(
            and_(CashBox.user_id == user_id, CashBox.is_active == True)
        ).first()
        
        # نشاط اليوم
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_activity = {
            'receipts_iqd': 0, 'payments_iqd': 0, 'receipts_usd': 0, 
            'payments_usd': 0, 'transactions_count': 0
        }
        
        if cash_box:
            activity = db.query(
                func.sum(case((CashTransaction.transaction_type.in_(['RECEIPT', 'TRANSFER_IN']), 
                              CashTransaction.amount), else_=0)).label('receipts'),
                func.sum(case((CashTransaction.transaction_type.in_(['PAYMENT', 'TRANSFER_OUT']), 
                              CashTransaction.amount), else_=0)).label('payments'),
                func.count(CashTransaction.id).label('transactions_count')
            ).filter(
                and_(CashTransaction.cash_box_id == cash_box.id,
                     CashTransaction.transaction_date >= today_start,
                     CashTransaction.transaction_date <= today_end)
            ).group_by(CashTransaction.currency_code).all()
            
            for row in activity:
                today_activity['transactions_count'] += row.transactions_count or 0
        
        # التحويلات المعلقة
        pending_sent = pending_received = 0
        last_transfer_date = None
        
        if cash_box:
            pending_sent = db.query(CashTransfer).filter(
                and_(CashTransfer.from_cash_box_id == cash_box.id,
                     CashTransfer.status == TransferStatusEnum.PENDING)
            ).count()
            
            pending_received = db.query(CashTransfer).filter(
                and_(CashTransfer.to_cash_box_id == cash_box.id,
                     CashTransfer.status == TransferStatusEnum.PENDING)
            ).count()
            
            last_transfer = db.query(CashTransfer.requested_date).filter(
                or_(CashTransfer.from_cash_box_id == cash_box.id,
                    CashTransfer.to_cash_box_id == cash_box.id)
            ).order_by(desc(CashTransfer.requested_date)).first()
            
            if last_transfer:
                last_transfer_date = last_transfer.requested_date
        
        return SalespersonCashFlowDashboard(
            user_id=user_id,
            user_name=user.name,
            employee_code=getattr(user, 'employee_code', None),
            assigned_regions=[region.region for region in regions],
            cash_box_id=cash_box.id if cash_box else None,
            cash_box_code=cash_box.code if cash_box else None,
            balance_iqd_cash=cash_box.balance_iqd_cash if cash_box else 0,
            balance_iqd_digital=cash_box.balance_iqd_digital if cash_box else 0,
            balance_usd_cash=cash_box.balance_usd_cash if cash_box else 0,
            balance_usd_digital=cash_box.balance_usd_digital if cash_box else 0,
            today_receipts_iqd=today_activity['receipts_iqd'],
            today_payments_iqd=today_activity['payments_iqd'],
            today_receipts_usd=today_activity['receipts_usd'],
            today_payments_usd=today_activity['payments_usd'],
            today_transactions_count=today_activity['transactions_count'],
            pending_transfers_sent=pending_sent,
            pending_transfers_received=pending_received,
            last_transfer_date=last_transfer_date
        )

    @staticmethod
    def get_system_dashboard(db: Session) -> CashFlowDashboardData:
        """الحصول على بيانات لوحة معلومات النظام الكاملة"""
        # بيانات الفروع
        branches = db.query(Branch).filter(Branch.is_active == True).all()
        branch_dashboards = []
        
        for branch in branches:
            branch_dashboard = CashFlowDashboardService.get_branch_dashboard(db, branch.id)
            branch_dashboards.append(branch_dashboard)
        
        # بيانات مندوبي المبيعات
        salespeople = db.query(User).filter(
            and_(User.is_salesperson == True, User.is_active == True)
        ).all()
        salesperson_dashboards = []
        
        for salesperson in salespeople:
            salesperson_dashboard = CashFlowDashboardService.get_salesperson_dashboard(db, salesperson.id)
            salesperson_dashboards.append(salesperson_dashboard)
        
        # الإجماليات على مستوى النظام
        system_totals = db.query(
            func.sum(CashBox.balance_iqd_cash + CashBox.balance_iqd_digital).label('total_iqd'),
            func.sum(CashBox.balance_usd_cash + CashBox.balance_usd_digital).label('total_usd'),
            func.sum(CashBox.balance_rmb_cash + CashBox.balance_rmb_digital).label('total_rmb')
        ).filter(CashBox.is_active == True).first()
        
        # نشاط اليوم
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_transactions = db.query(CashTransaction).filter(
            and_(CashTransaction.transaction_date >= today_start,
                 CashTransaction.transaction_date <= today_end)
        ).count()
        
        pending_transfers = db.query(CashTransfer).filter(
            CashTransfer.status == TransferStatusEnum.PENDING
        ).count()
        
        return CashFlowDashboardData(
            branches=branch_dashboards,
            salespeople=salesperson_dashboards,
            system_total_iqd=system_totals.total_iqd or 0,
            system_total_usd=system_totals.total_usd or 0,
            system_total_rmb=system_totals.total_rmb or 0,
            total_transactions_today=today_transactions,
            total_pending_transfers=pending_transfers,
            last_updated=datetime.utcnow()
        )
