# نماذج قاعدة البيانات
from .user import User
from .role import Role
from .branch import Branch
from .warehouse import Warehouse
from .product import Category, Product
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
# Multi-tenancy Models
from .tenant import Tenant, TenantSettings
# Enhanced Security and Permission Models
from .permissions import (
    PermissionType, ResourceType, Permission, RolePermission, 
    UserPermission, AuditLog
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

# Migration models
from .migration import (
    MigrationBatch, MigrationRecord, ItemCategory, MigrationItem, PriceList as MigrationPriceList, PriceListItem,
    MigrationCustomer, MigrationVendor, MigrationStock
)

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
    "Item", "PriceList"
]