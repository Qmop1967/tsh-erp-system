from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.models import (
    Branch, Warehouse, Role, User,
    Category, Product, Customer, Supplier,
    InventoryItem, StockMovement,
    SalesOrder, SalesItem, PurchaseOrder, PurchaseItem,
    # Accounting models
    Currency, ExchangeRate, ChartOfAccounts, Account, 
    Journal, JournalEntry, JournalLine, FiscalYear, AccountingPeriod,
    # Invoice models
    SalesInvoice, PurchaseInvoice, SalesInvoiceItem, PurchaseInvoiceItem, InvoicePayment,
    # POS models
    POSTerminal, POSSession, POSTransaction, POSTransactionItem,
    POSPayment, POSDiscount, POSPromotion,
    # Cash Flow models
    CashBox, SalespersonRegion, CashTransaction, CashTransfer, CashFlowSummary,
    # Expense models
    Expense, ExpenseItem, ExpenseAttachment
)

# إنشاء جميع الجداول
# Branch.__table__.create(bind=engine, checkfirst=True)
# Warehouse.__table__.create(bind=engine, checkfirst=True)
# Role.__table__.create(bind=engine, checkfirst=True)
# User.__table__.create(bind=engine, checkfirst=True)
# Category.__table__.create(bind=engine, checkfirst=True)
# Product.__table__.create(bind=engine, checkfirst=True)
# Customer.__table__.create(bind=engine, checkfirst=True)
# Supplier.__table__.create(bind=engine, checkfirst=True)
# InventoryItem.__table__.create(bind=engine, checkfirst=True)
# StockMovement.__table__.create(bind=engine, checkfirst=True)
# SalesOrder.__table__.create(bind=engine, checkfirst=True)
# SalesItem.__table__.create(bind=engine, checkfirst=True)
# PurchaseOrder.__table__.create(bind=engine, checkfirst=True)
# PurchaseItem.__table__.create(bind=engine, checkfirst=True)

app = FastAPI(
    title="TSH ERP System",
    description="نظام ERP بسيط باستخدام FastAPI و PostgreSQL",
    version="1.0.0",
)

# إعدادات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج، حدد المصادر المسموحة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# استيراد الـ routers
from app.routers import (
    branches_router, products_router, customers_router, 
    sales_router, inventory_router, accounting_router, pos_router,
    cashflow_router
)
from app.routers import auth
from app.routers.migration import router as migration_router
from app.routers.models import router as models_router
from app.routers.users import router as users_router
from app.routers.invoices import router as invoices_router
from app.routers.expenses import router as expenses_router
# from app.routers.warehouses import router as warehouses_router
from app.routers.items import router as items_router
# from app.routers.vendors import router as vendors_router

# إضافة الـ routers
app.include_router(auth.router, prefix="/api", tags=["authentication"])
app.include_router(branches_router, prefix="/api/branches", tags=["branches"])
app.include_router(products_router, prefix="/api/products", tags=["products"])
app.include_router(customers_router, prefix="/api/customers", tags=["customers"])
app.include_router(sales_router, prefix="/api/sales", tags=["sales"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["inventory"])
app.include_router(accounting_router, prefix="/api/accounting", tags=["accounting"])
app.include_router(invoices_router, prefix="/api")
app.include_router(expenses_router, prefix="/api/expenses", tags=["expenses"])
app.include_router(pos_router, prefix="/api/pos", tags=["pos"])
app.include_router(cashflow_router, prefix="/api/cashflow", tags=["cashflow"])
app.include_router(migration_router, prefix="/api")
app.include_router(models_router, prefix="/api", tags=["models"])
app.include_router(users_router, prefix="/api")
# app.include_router(warehouses_router, prefix="/api")
app.include_router(items_router, prefix="/api")
# app.include_router(vendors_router, prefix="/api")

# app.include_router(users.router, prefix="/users", tags=["users"])
# app.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
# app.include_router(roles.router, prefix="/roles", tags=["roles"])

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "مرحباً بك في نظام TSH ERP",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """فحص حالة التطبيق"""
    return {"status": "healthy", "message": "النظام يعمل بشكل طبيعي"}