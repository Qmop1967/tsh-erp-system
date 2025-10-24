"""
After-Sales Operations (ASO) Models
===================================
نماذج قاعدة البيانات لنظام عمليات ما بعد البيع (ASO)
يشمل: الإرجاعات، الفحص، الصيانة، الضمان، والقرارات
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# ============================================
# Enums
# ============================================

class ReturnReasonCode(enum.Enum):
    """أسباب الإرجاع"""
    defective = "defective"              # معيب
    wrong_item = "wrong_item"            # منتج خاطئ
    not_as_described = "not_as_described"  # غير مطابق للوصف
    customer_remorse = "customer_remorse"  # تراجع العميل
    damaged_shipping = "damaged_shipping"  # تلف أثناء الشحن
    warranty_claim = "warranty_claim"    # مطالبة ضمان
    other = "other"                      # أخرى


class ReturnStatus(enum.Enum):
    """حالات طلب الإرجاع"""
    pending = "pending"                  # قيد الانتظار
    approved = "approved"                # موافق عليه
    rejected = "rejected"                # مرفوض
    received = "received"                # مستلم
    under_inspection = "under_inspection"  # قيد الفحص
    under_repair = "under_repair"        # قيد الإصلاح
    repaired = "repaired"                # تم إصلاحه
    awaiting_decision = "awaiting_decision"  # بانتظار القرار
    decided = "decided"                  # تم اتخاذ القرار
    closed = "closed"                    # مغلق
    cancelled = "cancelled"              # ملغي


class InspectionStatus(enum.Enum):
    """حالات الفحص"""
    scheduled = "scheduled"              # مجدول
    in_progress = "in_progress"          # جاري
    completed = "completed"              # مكتمل
    cancelled = "cancelled"              # ملغي


class InspectionResult(enum.Enum):
    """نتائج الفحص"""
    pass_result = "pass"                 # ناجح
    fail_defective = "fail_defective"    # فشل - معيب
    fail_damaged = "fail_damaged"        # فشل - تالف
    fail_misuse = "fail_misuse"          # فشل - سوء استخدام
    inconclusive = "inconclusive"        # غير حاسم
    requires_repair = "requires_repair"  # يتطلب إصلاح


class MaintenanceStatus(enum.Enum):
    """حالات الصيانة"""
    pending = "pending"                  # قيد الانتظار
    in_progress = "in_progress"          # جاري
    parts_ordered = "parts_ordered"      # قطع غيار مطلوبة
    parts_arrived = "parts_arrived"      # قطع غيار وصلت
    completed = "completed"              # مكتمل
    failed = "failed"                    # فشل
    cancelled = "cancelled"              # ملغي


class WarrantyStatus(enum.Enum):
    """حالات الضمان"""
    active = "active"                    # فعال
    expired = "expired"                  # منتهي
    void = "void"                        # ملغي
    claimed = "claimed"                  # مطالب به


class Decision(enum.Enum):
    """القرارات النهائية"""
    full_refund = "full_refund"          # استرداد كامل
    partial_refund = "partial_refund"    # استرداد جزئي
    exchange = "exchange"                # استبدال
    store_credit = "store_credit"        # رصيد في المتجر
    repair = "repair"                    # إصلاح
    reject = "reject"                    # رفض
    escalate = "escalate"                # تصعيد


class InventoryZone(enum.Enum):
    """مناطق المخزون الداخلية"""
    received_returns = "received_returns"              # الإرجاعات المستلمة
    under_inspection = "under_inspection"              # قيد الفحص
    repair_workshop = "repair_workshop"                # ورشة الإصلاح
    awaiting_parts = "awaiting_parts"                  # بانتظار القطع
    quality_check = "quality_check"                    # فحص الجودة
    ready_to_restock = "ready_to_restock"              # جاهز لإعادة التخزين
    quarantine = "quarantine"                          # الحجر الصحي


# ============================================
# Models
# ============================================

class ASOProduct(Base):
    """معلومات المنتج للإرجاع"""
    __tablename__ = 'aso_products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100))
    base_price = Column(Numeric(10, 2), nullable=False)
    warranty_months = Column(Integer, default=12)
    is_serialized = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    return_requests = relationship("ASOReturnRequest", back_populates="product")
    warranty_policies = relationship("ASOWarrantyPolicy", back_populates="product")


class ASOReturnRequest(Base):
    """طلب الإرجاع"""
    __tablename__ = 'aso_return_requests'

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, nullable=False, index=True)

    # معلومات العميل والطلب
    customer_id = Column(Integer, nullable=False, index=True)
    sales_order_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('aso_products.id'), nullable=False)
    serial_number = Column(String(100), index=True)

    # تفاصيل الإرجاع
    reason_code = Column(SQLEnum(ReturnReasonCode), nullable=False)
    reason_description = Column(Text)
    status = Column(SQLEnum(ReturnStatus), default=ReturnStatus.pending, nullable=False, index=True)

    # التواريخ
    request_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    approval_date = Column(DateTime)
    received_date = Column(DateTime)
    closed_date = Column(DateTime)

    # التتبع
    current_zone = Column(SQLEnum(InventoryZone), default=InventoryZone.received_returns)
    assigned_to_user_id = Column(Integer, index=True)

    # المعلومات المالية
    original_price = Column(Numeric(10, 2), nullable=False)
    refund_amount = Column(Numeric(10, 2))
    restocking_fee = Column(Numeric(10, 2), default=0)

    # الأولوية والملاحظات
    priority = Column(Integer, default=3)  # 1=عالي, 2=متوسط, 3=عادي
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    product = relationship("ASOProduct", back_populates="return_requests")
    inspections = relationship("ASOInspection", back_populates="return_request")
    maintenance_jobs = relationship("ASOMaintenanceJob", back_populates="return_request")
    decisions = relationship("ASODecisionRecord", back_populates="return_request")


class ASOInspection(Base):
    """سجل الفحص"""
    __tablename__ = 'aso_inspections'

    id = Column(Integer, primary_key=True, index=True)
    return_request_id = Column(Integer, ForeignKey('aso_return_requests.id'), nullable=False, index=True)

    # معلومات الفحص
    inspector_user_id = Column(Integer, nullable=False, index=True)
    inspection_date = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLEnum(InspectionStatus), default=InspectionStatus.scheduled, nullable=False)
    result = Column(SQLEnum(InspectionResult))

    # التفاصيل
    findings = Column(Text)
    photos = Column(JSON)  # قائمة URLs للصور
    diagnostic_codes = Column(JSON)  # أكواد الأعطال

    # التوصيات
    recommended_action = Column(String(50))
    estimated_repair_cost = Column(Numeric(10, 2))
    estimated_repair_time_hours = Column(Integer)

    # ملاحظات
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    return_request = relationship("ASOReturnRequest", back_populates="inspections")


class ASOMaintenanceJob(Base):
    """مهمة الصيانة"""
    __tablename__ = 'aso_maintenance_jobs'

    id = Column(Integer, primary_key=True, index=True)
    job_number = Column(String(50), unique=True, nullable=False, index=True)
    return_request_id = Column(Integer, ForeignKey('aso_return_requests.id'), nullable=False, index=True)

    # تعيين الفني
    technician_user_id = Column(Integer, nullable=False, index=True)
    status = Column(SQLEnum(MaintenanceStatus), default=MaintenanceStatus.pending, nullable=False, index=True)

    # الجدولة
    scheduled_start = Column(DateTime)
    actual_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    actual_end = Column(DateTime)

    # التفاصيل
    work_description = Column(Text)
    parts_used = Column(JSON)  # قائمة القطع المستخدمة
    labor_hours = Column(Numeric(5, 2))
    parts_cost = Column(Numeric(10, 2))
    labor_cost = Column(Numeric(10, 2))
    total_cost = Column(Numeric(10, 2))

    # النتيجة
    completion_notes = Column(Text)
    quality_check_passed = Column(Boolean)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    return_request = relationship("ASOReturnRequest", back_populates="maintenance_jobs")


class ASOWarrantyPolicy(Base):
    """سياسة الضمان"""
    __tablename__ = 'aso_warranty_policies'

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(50), unique=True, nullable=False, index=True)

    # ربط المنتج
    product_id = Column(Integer, ForeignKey('aso_products.id'), nullable=False)
    serial_number = Column(String(100), index=True)

    # معلومات الضمان
    customer_id = Column(Integer, nullable=False, index=True)
    sales_order_id = Column(Integer, nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    warranty_start_date = Column(DateTime, nullable=False)
    warranty_end_date = Column(DateTime, nullable=False)

    # الحالة
    status = Column(SQLEnum(WarrantyStatus), default=WarrantyStatus.active, nullable=False, index=True)

    # التفاصيل
    warranty_type = Column(String(50))  # manufacturer, extended, etc.
    coverage_details = Column(Text)
    exclusions = Column(Text)

    # الاستخدام
    claims_count = Column(Integer, default=0)
    total_claimed_amount = Column(Numeric(10, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    product = relationship("ASOProduct", back_populates="warranty_policies")


class ASODecisionRecord(Base):
    """سجل القرار"""
    __tablename__ = 'aso_decision_records'

    id = Column(Integer, primary_key=True, index=True)
    return_request_id = Column(Integer, ForeignKey('aso_return_requests.id'), nullable=False, index=True)

    # القرار
    decision = Column(SQLEnum(Decision), nullable=False)
    decision_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    decided_by_user_id = Column(Integer, nullable=False, index=True)

    # التفاصيل المالية
    refund_amount = Column(Numeric(10, 2))
    store_credit_amount = Column(Numeric(10, 2))
    exchange_product_id = Column(Integer)

    # التبرير
    rationale = Column(Text)
    supporting_documents = Column(JSON)

    # المتابعة
    requires_approval = Column(Boolean, default=False)
    approved_by_user_id = Column(Integer, index=True)
    approval_date = Column(DateTime)

    # الإكمال
    executed = Column(Boolean, default=False)
    execution_date = Column(DateTime)
    execution_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    return_request = relationship("ASOReturnRequest", back_populates="decisions")


class ASONotification(Base):
    """إشعارات النظام"""
    __tablename__ = 'aso_notifications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    # محتوى الإشعار
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # new_task, status_update, etc.

    # الربط
    related_entity_type = Column(String(50))  # return_request, maintenance_job, etc.
    related_entity_id = Column(Integer)

    # الحالة
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime)

    # الأولوية
    priority = Column(Integer, default=3)  # 1=عالي, 2=متوسط, 3=عادي

    # الإرسال
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivery_method = Column(String(20))  # push, email, sms

    created_at = Column(DateTime, default=datetime.utcnow)

    # الفهارس
    __table_args__ = (
        {'comment': 'جدول إشعارات نظام عمليات ما بعد البيع'}
    )


class ASOOutboxEvent(Base):
    """أحداث Outbox للتكامل مع الأنظمة الأخرى"""
    __tablename__ = 'aso_outbox_events'

    id = Column(Integer, primary_key=True, index=True)

    # تفاصيل الحدث
    event_type = Column(String(100), nullable=False, index=True)
    aggregate_type = Column(String(50), nullable=False)
    aggregate_id = Column(Integer, nullable=False)

    # البيانات
    payload = Column(JSON, nullable=False)

    # المعالجة
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime)
    retry_count = Column(Integer, default=0)
    last_error = Column(Text)

    # التتبع
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # الفهارس
    __table_args__ = (
        {'comment': 'جدول Outbox للأحداث - نمط Transactional Outbox'}
    )
