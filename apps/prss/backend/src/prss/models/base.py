"""Base enums and types for models"""
import enum


class ReturnStatus(str, enum.Enum):
    """Return request status"""
    SUBMITTED = "submitted"
    RECEIVED = "received"
    INSPECTING = "inspecting"
    AWAITING_DECISION = "awaiting_decision"
    APPROVED_RESTOCK = "approved_restock"
    TO_REPAIR = "to_repair"
    TO_SUPPLIER = "to_supplier"
    REFUNDED = "refunded"
    REJECTED = "rejected"


class LogisticsStatus(str, enum.Enum):
    """Reverse logistics status"""
    REQUESTED = "requested"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"


class FindingType(str, enum.Enum):
    """Inspection finding type"""
    OK = "ok"
    COSMETIC_DEFECT = "cosmetic_defect"
    FUNCTIONAL_DEFECT = "functional_defect"
    WRONG_ITEM = "wrong_item"
    MISSING_PARTS = "missing_parts"
    DAMAGED_PACKAGING = "damaged_packaging"


class RecommendationType(str, enum.Enum):
    """Inspection recommendation"""
    RESTOCK = "restock"
    REPAIR = "repair"
    SCRAP = "scrap"
    SUPPLIER_RETURN = "supplier_return"
    REFUND = "refund"


class MaintenanceOutcome(str, enum.Enum):
    """Maintenance job outcome"""
    FIXED = "fixed"
    NOT_FIXABLE = "not_fixable"
    PARTS_UNAVAILABLE = "parts_unavailable"
    BEYOND_REPAIR = "beyond_repair"


class WarrantyDecision(str, enum.Enum):
    """Warranty decision type"""
    REPLACE = "replace"
    REPAIR = "repair"
    REFUND = "refund"
    DENY = "deny"


class FinalDecision(str, enum.Enum):
    """Final decision for return"""
    RESTOCK = "restock"
    REFURBISHED = "refurbished"
    SCRAP = "scrap"
    RETURN_TO_SUPPLIER = "return_to_supplier"
    REFUND = "refund"


class InventoryZone(str, enum.Enum):
    """Internal return inventory zones"""
    RECEIVED = "received"
    INSPECTION = "inspection"
    WORKSHOP = "workshop"
    AWAITING_DECISION = "awaiting_decision"
    APPROVED_RESTOCK = "approved_restock"
    SCRAP = "scrap"
    SUPPLIER_RETURN = "supplier_return"


class AccountingEffectType(str, enum.Enum):
    """Accounting effect type"""
    CREDIT_NOTE = "credit_note"
    PARTIAL_REFUND = "partial_refund"
    FULL_REFUND = "full_refund"
    LOSS_WRITEOFF = "loss_writeoff"
    SUPPLIER_DEBIT = "supplier_debit"


class OutboxStatus(str, enum.Enum):
    """Outbox event status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class UserRole(str, enum.Enum):
    """User roles for PRSS"""
    ADMIN = "admin"
    INSPECTOR = "inspector"
    TECHNICIAN = "technician"
    WARRANTY_OFFICER = "warranty_officer"
    LOGISTICS = "logistics"
    ACCOUNTING_VIEW = "accounting_view"
