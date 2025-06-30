"""
Cash Flow Management API Router
موجه API إدارة التدفق النقدي

API endpoints for cash flow management, transfers, and dashboard operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.db.database import get_db
from app.services.cashflow_service import (
    CashBoxService, SalespersonRegionService, CashTransactionService,
    CashTransferService, CashFlowDashboardService
)
from app.schemas.cashflow import (
    # Cash Box schemas
    CashBoxCreate, CashBoxUpdate, CashBox,
    # Region schemas  
    SalespersonRegionCreate, SalespersonRegionUpdate, SalespersonRegion,
    # Transaction schemas
    CashTransactionCreate, CashTransactionUpdate, CashTransaction,
    # Transfer schemas
    CashTransferCreate, CashTransferUpdate, CashTransferApproval, CashTransfer,
    # Dashboard schemas
    BranchCashFlowDashboard, SalespersonCashFlowDashboard, CashFlowDashboardData,
    TransferReceiptData,
    # Enums
    RegionEnum, TransferStatusEnum, CashBoxTypeEnum, PaymentMethodEnum
)

router = APIRouter()

# ====== Cash Box Management ======

@router.get("/cash-boxes", response_model=List[CashBox])
def get_cash_boxes(
    branch_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    box_type: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Get cash boxes with filters
    الحصول على صناديق النقد مع المرشحات
    """
    service = CashBoxService()
    return service.get_cash_boxes(db, branch_id, user_id, box_type, active_only)


@router.post("/cash-boxes", response_model=CashBox)
def create_cash_box(
    cash_box: CashBoxCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Create new cash box
    إنشاء صندوق نقد جديد
    """
    service = CashBoxService()
    return service.create_cash_box(db, cash_box, current_user_id)


@router.get("/cash-boxes/{cash_box_id}", response_model=CashBox)
def get_cash_box(cash_box_id: int, db: Session = Depends(get_db)):
    """
    Get specific cash box
    الحصول على صندوق نقد محدد
    """
    service = CashBoxService()
    return service.get_cash_box(db, cash_box_id)


@router.put("/cash-boxes/{cash_box_id}", response_model=CashBox)
def update_cash_box(
    cash_box_id: int,
    cash_box_update: CashBoxUpdate,
    db: Session = Depends(get_db)
):
    """
    Update cash box
    تحديث صندوق النقد
    """
    service = CashBoxService()
    return service.update_cash_box(db, cash_box_id, cash_box_update)


# ====== Salesperson Region Management ======

@router.get("/salesperson-regions", response_model=List[SalespersonRegion])
def get_salesperson_regions(
    user_id: int = Query(...),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Get salesperson assigned regions
    الحصول على مناطق مندوب المبيعات
    """
    service = SalespersonRegionService()
    return service.get_salesperson_regions(db, user_id, active_only)


@router.post("/salesperson-regions", response_model=SalespersonRegion)
def assign_region(
    region_data: SalespersonRegionCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Assign region to salesperson
    تعيين منطقة لمندوب مبيعات
    """
    service = SalespersonRegionService()
    return service.assign_region(db, region_data, current_user_id)


@router.put("/salesperson-regions/{assignment_id}", response_model=SalespersonRegion)
def update_region_assignment(
    assignment_id: int,
    update_data: SalespersonRegionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update region assignment
    تحديث تعيين منطقة
    """
    service = SalespersonRegionService()
    return service.update_region_assignment(db, assignment_id, update_data)


# ====== Cash Transaction Management ======

@router.get("/cash-transactions", response_model=List[CashTransaction])
def get_cash_transactions(
    cash_box_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get cash transactions with filters
    الحصول على المعاملات النقدية مع المرشحات
    """
    service = CashTransactionService()
    return service.get_transactions(db, cash_box_id, user_id, transaction_type, 
                                   start_date, end_date, skip, limit)


@router.post("/cash-transactions", response_model=CashTransaction)
def create_cash_transaction(
    transaction: CashTransactionCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Create new cash transaction
    إنشاء معاملة نقدية جديدة
    """
    service = CashTransactionService()
    return service.create_transaction(db, transaction, current_user_id)


@router.get("/cash-transactions/{transaction_id}", response_model=CashTransaction)
def get_cash_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Get specific cash transaction
    الحصول على معاملة نقدية محددة
    """
    service = CashTransactionService()
    transaction = service.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


# ====== Cash Transfer Management ======

@router.get("/cash-transfers", response_model=List[CashTransfer])
def get_cash_transfers(
    user_id: Optional[int] = Query(None),
    from_cash_box_id: Optional[int] = Query(None),
    to_cash_box_id: Optional[int] = Query(None),
    status: Optional[TransferStatusEnum] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get cash transfers with filters
    الحصول على التحويلات النقدية مع المرشحات
    """
    service = CashTransferService()
    return service.get_transfers(db, user_id, from_cash_box_id, to_cash_box_id, 
                                status, skip, limit)


@router.post("/cash-transfers", response_model=CashTransfer)
def create_cash_transfer(
    transfer: CashTransferCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Create new cash transfer request
    إنشاء طلب تحويل نقدي جديد
    """
    service = CashTransferService()
    return service.create_transfer(db, transfer, current_user_id)


@router.get("/cash-transfers/{transfer_id}", response_model=CashTransfer)
def get_cash_transfer(transfer_id: int, db: Session = Depends(get_db)):
    """
    Get specific cash transfer
    الحصول على تحويل نقدي محدد
    """
    service = CashTransferService()
    transfer = service.get_transfer(db, transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@router.put("/cash-transfers/{transfer_id}/approve", response_model=CashTransfer)
def approve_cash_transfer(
    transfer_id: int,
    approval: CashTransferApproval,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Approve or reject cash transfer
    الموافقة على التحويل النقدي أو رفضه
    """
    service = CashTransferService()
    return service.approve_transfer(db, transfer_id, approval, current_user_id)


@router.put("/cash-transfers/{transfer_id}/receive", response_model=CashTransfer)
def receive_cash_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Confirm receipt of cash transfer
    تأكيد استلام التحويل النقدي
    """
    service = CashTransferService()
    return service.receive_transfer(db, transfer_id, current_user_id)


@router.put("/cash-transfers/{transfer_id}/update", response_model=CashTransfer)
def update_cash_transfer(
    transfer_id: int,
    transfer_update: CashTransferUpdate,
    db: Session = Depends(get_db)
):
    """
    Update cash transfer details
    تحديث تفاصيل التحويل النقدي
    """
    service = CashTransferService()
    return service.update_transfer(db, transfer_id, transfer_update)


@router.post("/cash-transfers/{transfer_id}/upload-receipt")
def upload_transfer_receipt(
    transfer_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload transfer receipt attachment
    رفع مرفق إيصال التحويل
    """
    # TODO: Implement file upload logic
    # Save file to storage and update transfer record
    return {"message": "Receipt uploaded successfully", "file_name": file.filename}


@router.post("/cash-transfers/{transfer_id}/upload-paper")
def upload_paper_attachment(
    transfer_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload paper attachment for transfer
    رفع مرفق ورقي للتحويل
    """
    # TODO: Implement file upload logic
    # Save file to storage and update transfer record
    return {"message": "Paper attachment uploaded successfully", "file_name": file.filename}


# ====== Dashboard Endpoints ======

@router.get("/dashboard/branch/{branch_id}", response_model=BranchCashFlowDashboard)
def get_branch_dashboard(branch_id: int, db: Session = Depends(get_db)):
    """
    Get branch cash flow dashboard
    الحصول على لوحة معلومات التدفق النقدي للفرع
    """
    service = CashFlowDashboardService()
    return service.get_branch_dashboard(db, branch_id)


@router.get("/dashboard/salesperson/{user_id}", response_model=SalespersonCashFlowDashboard)
def get_salesperson_dashboard(user_id: int, db: Session = Depends(get_db)):
    """
    Get salesperson cash flow dashboard
    الحصول على لوحة معلومات التدفق النقدي لمندوب المبيعات
    """
    service = CashFlowDashboardService()
    return service.get_salesperson_dashboard(db, user_id)


@router.get("/dashboard/system", response_model=CashFlowDashboardData)
def get_system_dashboard(db: Session = Depends(get_db)):
    """
    Get complete system cash flow dashboard
    الحصول على لوحة معلومات التدفق النقدي للنظام الكامل
    """
    service = CashFlowDashboardService()
    return service.get_system_dashboard(db)


# ====== Utility Endpoints ======

@router.get("/regions", response_model=List[str])
def get_available_regions():
    """
    Get list of available regions
    الحصول على قائمة المناطق المتاحة
    """
    return [region.value for region in RegionEnum]


@router.get("/payment-methods", response_model=List[str])
def get_payment_methods():
    """
    Get list of available payment methods
    الحصول على قائمة طرق الدفع المتاحة
    """
    return [method.value for method in PaymentMethodEnum]


@router.get("/cash-box-types", response_model=List[str])
def get_cash_box_types():
    """
    Get list of available cash box types
    الحصول على قائمة أنواع صناديق النقد المتاحة
    """
    return [box_type.value for box_type in CashBoxTypeEnum]


@router.get("/transfer-statuses", response_model=List[str])
def get_transfer_statuses():
    """
    Get list of transfer statuses
    الحصول على قائمة حالات التحويل
    """
    return [status.value for status in TransferStatusEnum]


# ====== Reports and Analytics ======

@router.get("/reports/daily-cash-flow")
def get_daily_cash_flow_report(
    branch_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    report_date: date = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get daily cash flow report
    الحصول على تقرير التدفق النقدي اليومي
    """
    if not report_date:
        report_date = date.today()
    
    # TODO: Implement daily report generation
    return {
        "report_date": report_date,
        "branch_id": branch_id,
        "user_id": user_id,
        "message": "Daily cash flow report - under development"
    }


@router.get("/reports/transfer-receipt/{transfer_id}", response_model=TransferReceiptData)
def generate_transfer_receipt(transfer_id: int, db: Session = Depends(get_db)):
    """
    Generate transfer receipt data
    إنشاء بيانات إيصال التحويل
    """
    service = CashTransferService()
    transfer = service.get_transfer(db, transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    # TODO: Get related data for receipt
    return TransferReceiptData(
        transfer_id=transfer.id,
        transfer_number=transfer.transfer_number,
        from_salesperson="TBD",  # TODO: Get from relations
        to_branch="TBD",         # TODO: Get from relations
        amount=transfer.amount,
        currency=transfer.currency_code,
        transfer_date=transfer.requested_date,
        notes=transfer.description_en
    )


# ====== Quick Actions for Mobile App ======

@router.post("/quick-actions/receipt")
def quick_cash_receipt(
    cash_box_id: int,
    amount: float,
    currency: str = "IQD",
    payment_method: str = "CASH",
    customer_name: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Quick cash receipt entry for mobile app
    إدخال سريع لاستلام النقد للتطبيق المحمول
    """
    transaction = CashTransactionCreate(
        cash_box_id=cash_box_id,
        transaction_type="RECEIPT",
        payment_method=PaymentMethodEnum(payment_method),
        currency_code=currency,
        amount=amount,
        customer_name=customer_name,
        notes=notes,
        transaction_date=datetime.utcnow()
    )
    
    service = CashTransactionService()
    return service.create_transaction(db, transaction, current_user_id)


@router.post("/quick-actions/payment")
def quick_cash_payment(
    cash_box_id: int,
    amount: float,
    currency: str = "IQD",
    payment_method: str = "CASH",
    description: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Quick cash payment entry for mobile app
    إدخال سريع لدفع النقد للتطبيق المحمول
    """
    transaction = CashTransactionCreate(
        cash_box_id=cash_box_id,
        transaction_type="PAYMENT",
        payment_method=PaymentMethodEnum(payment_method),
        currency_code=currency,
        amount=amount,
        description_en=description,
        notes=notes,
        transaction_date=datetime.utcnow()
    )
    
    service = CashTransactionService()
    return service.create_transaction(db, transaction, current_user_id)
