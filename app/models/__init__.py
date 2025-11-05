# نماذج قاعدة البيانات
from .user import User
from .role import Role
from .branch import Branch
from .warehouse import Warehouse
from .product import Category, Product
from .item import Item
from .customer import Customer, Supplier
from .inventory import InventoryItem, StockMovement
from .sales import SalesOrder, SalesItem
from .purchase import PurchaseOrder, PurchaseItem
from .accounting import (
    Currency, ExchangeRate, ChartOfAccounts, Account, 
    Journal, JournalEntry, JournalLine, FiscalYear, AccountingPeriod
)
from .invoice import (
    SalesInvoice, PurchaseInvoice, SalesInvoiceItem, PurchaseInvoiceItem, InvoicePayment
)
from .pos import (
    POSTerminal, POSSession, POSTransaction, POSTransactionItem,
    POSPayment, POSDiscount, POSPromotion
)
# Multi-tenancy Models (disabled in unified database)
# from .tenant import Tenant, TenantSettings
# Enhanced Security and Permission Models
from .permissions import (
    ActionType, ModuleType, Permission, RolePermission,
    UserPermission, AuditLog
)
# Data Scope and RLS Models
from .data_scope import (
    UserDataScope, DataScopeTemplate, DataAccessLog, DataScopeType,
    user_customers, user_warehouses, user_branches
)
# Advanced Security Models
from .security import (
    LoginAttempt, AccountLockout, TokenBlacklist,
    MFAMethod, UserMFA, MFAVerification,
    UserSession, PasswordHistory, PasswordResetToken,
    EmailVerificationToken, TrustedDevice, SecurityEvent
)
from .cashflow import (
    CashBox, SalespersonRegion, CashTransaction, CashTransfer, CashFlowSummary
)
from .expense import (
    Expense, ExpenseItem, ExpenseAttachment
)
from .money_transfer import (
    MoneyTransfer, TransferPlatform
)
from .pricing import (
    PricingList, ProductPrice, PriceListCategory, PriceHistory, 
    PriceNegotiationRequest, CustomerPriceCategory
)
from .ai_assistant import (
    AIConversation, AIConversationMessage, AIGeneratedOrder, AISupportTicket
)
from .whatsapp import (
    WhatsAppMessage, WhatsAppBroadcast, WhatsAppAutoResponse
)
from .hr import (
    Employee, Department, Position, PayrollRecord, AttendanceRecord,
    LeaveRequest, PerformanceReview, HRDashboardMetrics,
    EmployeeDocument, EmployeePerformanceRanking, PayslipRecord,
    HRNotification, WhatsAppIntegration,
    EmploymentStatus, PayrollStatus, LeaveType, LeaveStatus, AttendanceStatus,
    PerformanceRank, PaymentMethod, DocumentType
)
# After-Sales Operations (ASO) Models
from .after_sales import (
    ASOProduct, ASOReturnRequest, ASOInspection, ASOMaintenanceJob,
    ASOWarrantyPolicy, ASODecisionRecord, ASONotification, ASOOutboxEvent,
    ReturnReasonCode, ReturnStatus, InspectionStatus, InspectionResult,
    MaintenanceStatus, WarrantyStatus, Decision, InventoryZone
)

# Migration models
from .migration import (
    MigrationBatch, MigrationRecord, ItemCategory, MigrationItem, PriceList as MigrationPriceList, PriceListItem,
    MigrationCustomer, MigrationVendor, MigrationStock
)

# Zoho Sync Models (unified from TDS Core)
from .zoho_sync import (
    TDSInboxEvent, TDSSyncQueue, TDSDeadLetterQueue, TDSSyncLog, TDSAlert,
    EventStatus, SourceType, EntityType, AlertSeverity
)

# Mobile BFF Models
from .promotion import Promotion
from .cart import Cart, CartItem
from .review import Review
from .customer_address import CustomerAddress

# Notification Models
from .notification import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationPriority, NotificationChannel
)

# Backward compatibility alias
AlertLevel = AlertSeverity

# Aliases for backward compatibility
Item = MigrationItem  # Alias for backward compatibility
PriceList = MigrationPriceList  # Alias for backward compatibility

__all__ = [
    "User", "Role", "Branch", "Warehouse",
    "Category", "Product",
    "Customer", "Supplier", 
    "InventoryItem", "StockMovement",
    "SalesOrder", "SalesItem",
    "PurchaseOrder", "PurchaseItem",
    # Accounting models
    "Currency", "ExchangeRate", "ChartOfAccounts", "Account",
    "Journal", "JournalEntry", "JournalLine", "FiscalYear", "AccountingPeriod",
    # Invoice models
    "SalesInvoice", "PurchaseInvoice", "SalesInvoiceItem", "PurchaseInvoiceItem", "InvoicePayment",
    # POS models
    "POSTerminal", "POSSession", "POSTransaction", "POSTransactionItem",
    "POSPayment", "POSDiscount", "POSPromotion",
    # Cash Flow models
    "CashBox", "SalespersonRegion", "CashTransaction", "CashTransfer", "CashFlowSummary",
    # Expense models
    "Expense", "ExpenseItem", "ExpenseAttachment",
    # Money Transfer models (CRITICAL - Fraud Prevention)
    "MoneyTransfer", "TransferPlatform",
    # Pricing models
    "PricingList", "ProductPrice", "PriceListCategory", "PriceHistory", 
    "PriceNegotiationRequest", "CustomerPriceCategory",
    # AI Assistant models
    "AIConversation", "AIConversationMessage", "AIGeneratedOrder", "AISupportTicket",
    # WhatsApp models
    "WhatsAppMessage", "WhatsAppBroadcast", "WhatsAppAutoResponse",
        # HR models
    "Employee", "Department", "Position", "PayrollRecord", "AttendanceRecord",
    "LeaveRequest", "PerformanceReview", "HRDashboardMetrics",
    "EmployeeDocument", "EmployeePerformanceRanking", "PayslipRecord",
    "HRNotification", "WhatsAppIntegration",
    "EmploymentStatus", "PayrollStatus", "LeaveType", "LeaveStatus", "AttendanceStatus",
    "PerformanceRank", "PaymentMethod", "DocumentType",
    # Migration models
    "MigrationBatch", "MigrationRecord", "ItemCategory", "MigrationItem", "MigrationPriceList", "PriceListItem",
    "MigrationCustomer", "MigrationVendor", "MigrationStock",
    # Aliases for backward compatibility
    "Item", "PriceList",
    # Data Scope and RLS Models
    "UserDataScope", "DataScopeTemplate", "DataAccessLog", "DataScopeType",
    "user_customers", "user_warehouses", "user_branches",
    # After-Sales Operations (ASO) Models
    "ASOProduct", "ASOReturnRequest", "ASOInspection", "ASOMaintenanceJob",
    "ASOWarrantyPolicy", "ASODecisionRecord", "ASONotification", "ASOOutboxEvent",
    "ReturnReasonCode", "ReturnStatus", "InspectionStatus", "InspectionResult",
    "MaintenanceStatus", "WarrantyStatus", "Decision", "InventoryZone",
    # Mobile BFF Models
    "Promotion", "Cart", "CartItem", "Review", "CustomerAddress",
    # Notification Models
    "Notification", "NotificationTemplate", "NotificationPreference",
    "NotificationType", "NotificationPriority", "NotificationChannel"
]