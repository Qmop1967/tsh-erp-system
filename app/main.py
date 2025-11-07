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

# Database tables are managed by migrations (Alembic)

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

# CORS Configuration - Secure settings for production
from app.core.config import settings

# Define allowed origins
allowed_origins = [
    "http://localhost:3000",           # React dev server
    "http://localhost:5173",           # Vite dev server
    "https://erp.tsh.sale",            # Production ERP web
    "https://admin.tsh.sale",          # Admin panel
    "https://shop.tsh.sale",           # Consumer web app
    "https://consumer.tsh.sale",       # Consumer web app (alternative)
    "capacitor://localhost",           # iOS apps (Capacitor)
    "http://localhost",                # Android apps
    "ionic://localhost",               # Ionic apps
]

# Allow all origins in development for easier testing
if settings.environment == "development":
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count", "X-Request-ID"],
)

# استيراد الـ routers
from app.routers import (
    sales_router, inventory_router, accounting_router, pos_router,
    cashflow_router
)
# Phase 5 Refactored Routers
from app.routers.branches_refactored import router as branches_router  # ✅ Phase 5 P0: Refactored
from app.routers.products_refactored import router as products_router  # ✅ Phase 5 P1: Refactored
from app.routers.customers_refactored import router as customers_router  # ✅ Phase 5 P1: Refactored
from app.routers.warehouses_refactored import router as warehouses_router  # ✅ Phase 5 P0: Refactored
from app.routers.items_refactored import router as items_router  # ✅ Phase 5 P2: Refactored
# Legacy migration router removed - TDS Core handles all Zoho integration
# from app.routers.migration import router as migration_router
from app.routers.models import router as models_router
from app.routers.users_refactored import router as users_router  # ✅ Phase 5 P3 Batch 2: Refactored
from app.routers.invoices_refactored import router as invoices_router  # ✅ Phase 5 P3 Batch 2: Refactored
from app.routers.expenses_refactored import router as expenses_router  # ✅ Phase 5 P3 Batch 1: Refactored
from app.routers.money_transfer_refactored import router as money_transfer_router  # ✅ Phase 5 P3 Batch 2: Refactored
from app.routers.settings import router as settings_router  # TODO: Migrate to app.routers.settings module
# New modular settings (Phase 1: System settings completed)
# from app.routers.settings import router as modular_settings_router
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

# ============================================================================
# 🧹 REFACTORING 2025-01-07: Code Duplication Eliminated
# ============================================================================
# Centralized Authentication: app/dependencies/auth.py
# - get_current_user() - Single source of truth (was duplicated in 3 places)
# - get_user_permissions() - Centralized role mapping
#
# Archived Deprecated Routers (see archived/deprecated_routers_2025_01/):
# ❌ auth.py (391 lines) → ✅ app.dependencies.auth
# ❌ auth_simple.py (247 lines) → ✅ app.dependencies.auth
# ❌ partner_salesmen.py (47KB) → ✅ partner_salesmen_simple.py (4KB, -91%)
# ❌ multi_price_system.py (798 lines) → ✅ multi_price_system_simple.py (158 lines, -80%)
#
# Result: -4 files, -2,200+ lines, improved maintainability
# ============================================================================
from app.routers.vendors_refactored import router as vendors_router  # ✅ Phase 5 P2: Refactored
from app.routers.permissions import router as permissions_router  # Enable permissions management
from app.routers.trusted_devices import router as trusted_devices_router  # Trusted devices for automatic login
from app.routers.data_scope import router as data_scope_router  # Row-Level Security (RLS) and data scope management
from app.routers.chatgpt import router as chatgpt_router  # ChatGPT Integration
from app.routers.backup_restore import router as backup_restore_router  # Backup & Restore System
from app.routers.consumer_api import router as consumer_api_router  # Consumer App with Zoho Integration
from app.routers.dashboard_refactored import router as dashboard_router  # ✅ Phase 5 P3 Batch 1: Refactored
from app.routers.notifications import router as notifications_router  # Unified Notification System
# from app.routers.product_images import router as product_images_router  # Temporarily disabled
# ============================================================================
# 🚀 TDS CORE v3.0.0 - TSH DataSync Core (Zoho Integration)
# ============================================================================
# TDS is the SOLE OWNER of ALL Zoho integration logic
#
# 🎯 SINGLE ENTRY POINT: from app.tds.zoho import ZohoService
#
# What TDS Handles:
# ✅ OAuth authentication & auto-token-refresh
# ✅ Unified API client (Books, Inventory, CRM)
# ✅ Sync orchestration (products, customers, inventory)
# ✅ Webhook processing
# ✅ Stock synchronization
# ✅ Rate limiting & retry logic
# ✅ Monitoring & health checks
#
# Consolidated Services (15 → 1):
# ❌ app/services/zoho_*.py (168KB) → archived
# ✅ app/tds/zoho.py (single facade)
# ✅ app/tds/integrations/zoho/* (modular implementation)
#
# Impact: -63KB code, -93% files, 100% duplication eliminated
# ============================================================================
from app.routers.zoho_webhooks import router as zoho_webhooks_router  # TDS webhook receiver
from app.routers.zoho_bulk_sync import router as zoho_bulk_sync_router  # TDS bulk sync

# 📦 Archived Legacy Services (2025-01-07):
# See: archived/legacy_zoho_services_2025_01/README.md
# ❌ zoho_service.py (55KB) - Main service
# ❌ zoho_auth_service.py - OAuth
# ❌ zoho_books_client.py - Books API
# ❌ zoho_inventory_client.py - Inventory API
# ❌ zoho_bulk_sync.py - Sync ops
# ❌ zoho_stock_sync.py - Stock sync
# ❌ zoho_token_manager.py - Token mgmt
# ❌ zoho_token_refresh_scheduler.py - Auto-refresh
# ❌ zoho_rate_limiter.py - Rate limiting
# ❌ zoho_processor.py - Processors
# ❌ zoho_queue.py - Queue
# ❌ zoho_monitoring.py - Monitoring
# ❌ zoho_alert.py - Alerts
# ❌ zoho_inbox.py - Inbox
# ❌ zoho_webhook_health.py - Health
#
# All functionality now in TDS:
# ✅ from app.tds.zoho import ZohoService
# ============================================================================
# 🏗️ PHASE 4: Repository Pattern & Service Layer (2025-01-07)
# ============================================================================
# Architectural Improvements: Eliminated 174+ duplicate CRUD operations
#
# 🎯 NEW INFRASTRUCTURE:
# ✅ app/repositories/base.py - Generic Repository Pattern
# ✅ app/exceptions/__init__.py - Standardized Exception Handling (263→1)
# ✅ app/utils/pagination.py - Reusable Pagination (38→1)
# ✅ app/services/branch_service.py - Service Layer (business logic)
# ✅ app/services/warehouse_service.py - Service Layer
#
# What Changed:
# ❌ BEFORE: Routers → Database (174 duplicate operations)
# ✅ AFTER: Routers → Services → Repository → Database (DRY)
#
# Example Transformation:
# ❌ OLD (app/routers/branches.py): 44 lines, 6 DB queries, manual CRUD
# ✅ NEW (app/routers/branches_refactored.py): 40 lines, 0 DB queries, clean
#
# Benefits:
# - Eliminated 174 duplicate CRUD operations
# - Eliminated 38 duplicate pagination parameters
# - Eliminated 32 duplicate search patterns
# - Standardized 263 HTTPException usages (now bilingual!)
# - Separation of concerns (Router → Service → Repository → DB)
# - Easy testing (mock services, not databases)
# - Type-safe operations throughout
#
# Test Coverage:
# ✅ tests/unit/test_base_repository.py (17 tests)
# ✅ tests/unit/test_exceptions.py (27 tests)
# ✅ tests/unit/test_branch_service.py (17 tests)
# Total: +61 tests for Phase 4 infrastructure
#
# Documentation: docs/PHASE_4_REFACTORING.md
# Impact: -174 duplications, +1,733 lines of infrastructure
# Status: ✅ Infrastructure Complete, Ready for Router Migration
# Next: Migrate 22 routers to use new patterns (15-20 days)
# ============================================================================
# 🚀 PHASE 5: Router Migration - P0 Priority Routers (2025-01-07)
# ============================================================================
# First Wave Migration: Applying Phase 4 patterns to production routers
#
# 🎯 P0 ROUTERS MIGRATED:
# ✅ app/routers/branches_refactored.py (was branches.py)
#    - BEFORE: 44 lines, 6 DB queries, manual CRUD
#    - AFTER: 40 lines, 0 DB queries, service-based
#    - NEW: Pagination, search, filter by is_active, soft delete
#
# ✅ app/routers/warehouses_refactored.py (was warehouses.py)
#    - BEFORE: 100 lines, 10 DB queries, 3 duplicate 404s
#    - AFTER: 50 lines, 0 DB queries, service-based
#    - NEW: Pagination, search, filter by branch_id
#
# Benefits Per Router:
# - 100% backward compatible (all existing endpoints work)
# - Pagination: Standard PaginatedResponse with metadata
# - Search: Built-in across multiple fields
# - Filtering: Query parameters for common filters
# - Error Handling: Bilingual custom exceptions
# - Testability: Mock services instead of database
#
# Migration Pattern:
# 1. Service already exists (Phase 4)
# 2. Replace DB operations with service calls
# 3. Add PaginationParams/SearchParams
# 4. Return PaginatedResponse for list endpoints
# 5. Update main.py imports
#
# Progress: 2/24 routers migrated (8%)
# Next: P1 routers (products, customers)
#
# Documentation: docs/PHASE_5_ROUTER_MIGRATION.md
# Status: ✅ P0 Complete, Template Proven
# ============================================================================
# BFF (Backend For Frontend) - Mobile Optimization Layer
from app.bff import bff_router  # Mobile BFF layer for all 11 apps - 100% Complete!
# V2 API - Clean Architecture Implementation
from app.routers.v2.customers import router as customers_v2_router  # Clean architecture customer API
from app.routers.v2.products import router as products_v2_router  # Clean architecture product API
from app.routers.v2.orders import router as orders_v2_router  # Clean architecture order API
from app.routers.v2.inventory import router as inventory_v2_router  # Clean architecture inventory API

# إضافة الـ routers
app.include_router(auth_router, prefix="/api", tags=["Authentication"])  # Enhanced authentication with MFA, rate limiting, session management
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
# Legacy migration router removed - TDS Core handles all Zoho integration
# app.include_router(migration_router, prefix="/api")
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
# ============================================================================
# 🔄 TDS CORE - TSH DataSync Core (Zoho Integration)
# ============================================================================
# TDS Core is the SOLE handler for ALL Zoho Books integration:
# - Real-time webhooks (< 15 seconds sync delay)
# - Bulk sync (manual/scheduled)
# - Queue management with retry logic
# - Monitoring and auto-healing
# - Complete audit trail
# ============================================================================
app.include_router(zoho_webhooks_router, prefix="/api/zoho/webhooks", tags=["TDS Core - Webhooks"])
app.include_router(zoho_bulk_sync_router, prefix="/api/zoho/bulk-sync", tags=["TDS Core - Bulk Sync"])

# Legacy Zoho routers REMOVED:
# ❌ app.include_router(zoho_dashboard_router) - TDS monitoring handles this
# ❌ app.include_router(zoho_admin_router) - TDS admin features handle this
# ❌ app.include_router(zoho_proxy_router) - Direct integration, no proxy needed
# ❌ app.include_router(migration_router) - TDS bulk sync replaced this
# 📱 MOBILE BFF: Optimized API Layer for ALL 11 Flutter Apps (100% Complete)
app.include_router(bff_router, prefix="/api/bff", tags=["Mobile BFF - All 11 Apps | 198 Endpoints | 9,782 Lines"])  # 100% Complete!
# 🏗️ V2 API: Clean Architecture Implementation with Repository Pattern
app.include_router(customers_v2_router, prefix="/api", tags=["Customers V2 - Clean Architecture"])
app.include_router(products_v2_router, prefix="/api", tags=["Products V2 - Clean Architecture"])
app.include_router(orders_v2_router, prefix="/api", tags=["Orders V2 - Clean Architecture"])
app.include_router(inventory_v2_router, prefix="/api", tags=["Inventory V2 - Clean Architecture"])
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