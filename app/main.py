from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.db.database import engine
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time

# Initialize structured logging
from app.utils.logging_config import get_logger, log_api_request, log_api_response

logger = get_logger(__name__)
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
    Expense, ExpenseItem, ExpenseAttachment,
    # Money Transfer models (CRITICAL - Fraud Prevention)
    MoneyTransfer, TransferPlatform,
    # Enhanced Security models (Tenant disabled for unified database)
    # Tenant, TenantSettings,
    ActionType, ModuleType,
    Permission, RolePermission, UserPermission, AuditLog,
    # Data Scope and RLS models
    UserDataScope, DataScopeTemplate, DataAccessLog
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

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="TSH ERP System",
    description="نظام ERP بسيط باستخدام FastAPI و PostgreSQL",
    version="1.0.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Logging middleware for API requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming API requests and responses"""
    start_time = time.time()

    # Log incoming request
    logger.info(
        "api_request_received",
        method=request.method,
        path=str(request.url.path),
        client_ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown")
    )

    # Process request
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        logger.info(
            "api_response_sent",
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2)
        )

        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "api_request_failed",
            method=request.method,
            path=str(request.url.path),
            error=str(e),
            duration_ms=round(duration_ms, 2),
            exc_info=True
        )
        raise

# Startup event
@app.on_event("startup")
async def startup_event():
    """Log application startup and start background workers"""
    logger.info("application_startup", message="TSH ERP System starting up...")

    # Start Zoho Token Refresh Scheduler
    try:
        from app.services.zoho_token_refresh_scheduler import start_token_refresh_scheduler
        await start_token_refresh_scheduler()
        logger.info("zoho_token_scheduler_started", message="Zoho token refresh scheduler started successfully")
    except Exception as e:
        logger.error("zoho_token_scheduler_failed", error=str(e), message="Failed to start Zoho token refresh scheduler")

    # Start Zoho sync workers
    try:
        from app.background.worker_manager import init_worker_manager, start_workers
        init_worker_manager(num_workers=2)  # Start 2 concurrent workers
        await start_workers()
        logger.info("background_workers_started", message="Zoho sync workers started successfully")
    except Exception as e:
        logger.error("background_workers_failed", error=str(e), message="Failed to start background workers")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown and stop background workers"""
    logger.info("application_shutdown", message="TSH ERP System shutting down...")

    # Stop Zoho Token Refresh Scheduler
    try:
        from app.services.zoho_token_refresh_scheduler import stop_token_refresh_scheduler
        stop_token_refresh_scheduler()
        logger.info("zoho_token_scheduler_stopped", message="Zoho token refresh scheduler stopped successfully")
    except Exception as e:
        logger.error("zoho_token_scheduler_stop_failed", error=str(e), message="Failed to stop Zoho token refresh scheduler")

    # Stop Zoho sync workers
    try:
        from app.background.worker_manager import stop_workers
        await stop_workers()
        logger.info("background_workers_stopped", message="Zoho sync workers stopped successfully")
    except Exception as e:
        logger.error("background_workers_stop_failed", error=str(e), message="Failed to stop background workers")

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
    branches_router, customers_router, 
    sales_router, inventory_router, accounting_router, pos_router,
    cashflow_router
)
from app.routers.products import router as products_router
from app.routers.migration import router as migration_router
from app.routers.models import router as models_router
from app.routers.users import router as users_router
from app.routers.invoices import router as invoices_router
from app.routers.expenses import router as expenses_router
# from app.routers.warehouses import router as warehouses_router
from app.routers.warehouses import router as warehouses_router  # Enable warehouses
from app.routers.items import router as items_router
from app.routers.money_transfer import router as money_transfer_router
from app.routers.settings import router as settings_router
from app.routers.enhanced_settings import router as enhanced_settings_router  # Enhanced security router
from app.routers.admin import router as admin_router
from app.routers.pos_enhanced import router as pos_enhanced_router
from app.routers.returns_exchange import router as returns_exchange_router
from app.routers.gps_money_transfer import router as gps_money_transfer_router
from app.routers.multi_price_system_simple import router as multi_price_system_router
from app.routers.ai_assistant import router as ai_assistant_router
from app.routers.whatsapp_integration import router as whatsapp_router
from app.routers.hr import router as hr_router
from app.routers.gps_tracking import router as gps_router
from app.routers.partner_salesmen_simple import router as partner_salesmen_router
from app.routers.auth_enhanced import router as auth_router  # Enhanced auth router with MFA, rate limiting, sessions
from app.routers.auth_simple import router as auth_simple_router  # Simple auth router for unified database
# from app.routers.partner_salesmen import router as partner_salesmen_router  # Temporarily disabled
from app.routers.vendors import router as vendors_router  # Enable vendors
from app.routers.permissions import router as permissions_router  # Enable permissions management
from app.routers.trusted_devices import router as trusted_devices_router  # Trusted devices for automatic login
from app.routers.data_scope import router as data_scope_router  # Row-Level Security (RLS) and data scope management
from app.routers.chatgpt import router as chatgpt_router  # ChatGPT Integration
from app.routers.backup_restore import router as backup_restore_router  # Backup & Restore System
from app.routers.consumer_api import router as consumer_api_router  # Consumer App with Zoho Integration
from app.routers.dashboard import router as dashboard_router  # Dashboard Statistics
from app.routers.notifications import router as notifications_router  # Unified Notification System
# from app.routers.product_images import router as product_images_router  # Temporarily disabled
# Zoho Integration Routers (unified from TDS Core)
from app.routers.zoho_webhooks import router as zoho_webhooks_router
from app.routers.zoho_dashboard import router as zoho_dashboard_router
from app.routers.zoho_admin import router as zoho_admin_router
from app.routers.zoho_bulk_sync import router as zoho_bulk_sync_router  # Bulk data migration
from app.routers.zoho_proxy import router as zoho_proxy_router  # Zoho image proxy
# BFF (Backend For Frontend) - Mobile Optimization Layer
from app.bff.mobile import router as mobile_bff_router  # Mobile BFF layer enabled!

# إضافة الـ routers
app.include_router(auth_router, prefix="/api", tags=["authentication"])  # Enable authentication
app.include_router(auth_simple_router, tags=["Simple Authentication"])  # Simple auth for unified database
app.include_router(dashboard_router, tags=["dashboard"])  # Dashboard statistics
app.include_router(branches_router, prefix="/api/branches", tags=["branches"])
app.include_router(products_router, prefix="/api/products", tags=["products"])
app.include_router(customers_router, prefix="/api/customers", tags=["customers"])
app.include_router(sales_router, prefix="/api/sales", tags=["sales"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["inventory"])
app.include_router(accounting_router, prefix="/api/accounting", tags=["accounting"])
app.include_router(invoices_router, prefix="/api")
app.include_router(expenses_router, prefix="/api/expenses", tags=["expenses"])
app.include_router(pos_router, prefix="/api/pos", tags=["pos"])
app.include_router(pos_enhanced_router, prefix="/api/pos/enhanced", tags=["POS Enhanced - Google Lens & Advanced Payments"])
app.include_router(returns_exchange_router, prefix="/api/returns", tags=["Returns & Exchange System - Complete Management"])
app.include_router(gps_money_transfer_router, prefix="/api/gps", tags=["GPS Money Transfer Tracking - 12 Travel Salespersons"])
app.include_router(multi_price_system_router, prefix="/api/pricing", tags=["Multi-Price System - 5 Customer Categories"])
app.include_router(cashflow_router, prefix="/api/cashflow", tags=["cashflow"])
# 🚨 CRITICAL: Emergency Money Transfer Tracking System
app.include_router(money_transfer_router, tags=["Money Transfers - FRAUD PREVENTION"])
# 👑 ADMIN CONTROL CENTER: Complete business oversight
app.include_router(admin_router, prefix="/api/admin", tags=["Admin Dashboard - BUSINESS CONTROL"])
# 🤖 AI ASSISTANT: 24/7 Bilingual Customer Support
app.include_router(ai_assistant_router, prefix="/api/ai", tags=["AI Assistant - 24/7 Customer Support"])
# � CHATGPT INTEGRATION: OpenAI-Powered Intelligent Assistant
app.include_router(chatgpt_router, prefix="/api", tags=["ChatGPT - OpenAI Integration"])
# �📱 WHATSAPP INTEGRATION: Communication & Order Processing
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp Integration - Business Communication"])
# 👥 HR MANAGEMENT SYSTEM: Complete HR Control for 19+ Employees
app.include_router(hr_router, prefix="/api/hr", tags=["HR Management System - Phase 3 Implementation"])
# 👥 PARTNER SALESMEN NETWORK: 100+ Salesmen Across Iraq
app.include_router(partner_salesmen_router, prefix="/api/partners", tags=["Partner Salesmen"])
app.include_router(migration_router, prefix="/api")
app.include_router(models_router, prefix="/api", tags=["models"])
app.include_router(users_router, prefix="/api")
app.include_router(permissions_router, prefix="/api")  # Add permissions management
app.include_router(trusted_devices_router, prefix="/api")  # Trusted devices for automatic login
app.include_router(data_scope_router, prefix="/api")  # Row-Level Security (RLS) and data scope management
app.include_router(warehouses_router, prefix="/api")  # Enable warehouses router
app.include_router(items_router, prefix="/api")
app.include_router(vendors_router, prefix="/api")  # Enable vendors router
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
app.include_router(backup_restore_router, prefix="/api/backup", tags=["Backup & Restore - System Protection"])
# 🛒 CONSUMER APP: Modern E-commerce with Zoho Integration
app.include_router(consumer_api_router, prefix="/api/consumer", tags=["Consumer App - E-commerce with Zoho Sync"])
# 🔄 ZOHO INTEGRATION: Unified Zoho Books Integration (from TDS Core)
app.include_router(zoho_webhooks_router, prefix="/api/zoho/webhooks", tags=["Zoho Integration - Webhooks"])
app.include_router(zoho_dashboard_router, prefix="/api/zoho/dashboard", tags=["Zoho Integration - Dashboard"])
app.include_router(zoho_admin_router, prefix="/api/zoho/admin", tags=["Zoho Integration - Admin"])
app.include_router(zoho_bulk_sync_router, prefix="/api/zoho/bulk-sync", tags=["Zoho Integration - Bulk Migration"])
app.include_router(zoho_proxy_router, tags=["Zoho Proxy"])
# 📱 MOBILE BFF: Optimized API Layer for Flutter Apps (Consumer & Salesperson)
app.include_router(mobile_bff_router, prefix="/api/mobile", tags=["Mobile BFF - Optimized for Flutter Apps"])  # Enabled!
# 🔔 UNIFIED NOTIFICATION SYSTEM: Enterprise-grade Notification Center
app.include_router(notifications_router, prefix="/api", tags=["Notifications - Real-time & Push Notifications"])
# 🔒 ENHANCED SECURITY SYSTEM: Advanced RBAC/ABAC, Multi-tenancy, Audit & Monitoring
app.include_router(enhanced_settings_router, prefix="/api/security", tags=["Enhanced Security - RBAC/ABAC & Multi-tenancy"])
# 📷 PRODUCT IMAGES MANAGEMENT: Temporarily disabled due to import issues
# app.include_router(product_images_router, tags=["Product Images - Zoho Integration"])

# Serve static files (e.g., images) from the "app/images" directory
app.mount("/images", StaticFiles(directory=Path("app/images")), name="images")

# Create static directory if it doesn't exist
static_dir = Path("app/static")
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount frontend public directory for product images (mobile app access)
frontend_public_dir = Path("frontend/public")
if frontend_public_dir.exists():
    app.mount("/public", StaticFiles(directory=frontend_public_dir), name="public")
    print(f"✅ Mounted frontend public directory: /public")
else:
    print(f"⚠️ Frontend public directory not found: {frontend_public_dir}")

# Remove duplicate lines and keep clean structure

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