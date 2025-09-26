# Module Documentation

This directory contains documentation for individual modules of the TSH ERP System.

## Available Modules

### 📊 Accounting Module
- **[Accounting Module (PostgreSQL)](ACCOUNTING_MODULE_ENABLED_POSTGRESQL.md)** - Complete accounting system with PostgreSQL integration
- **[Accounting Module](ACCOUNTING_MODULE_ENABLED.md)** - Standard accounting system documentation
- **[Accounting System Status](ACCOUNTING_SYSTEM_STATUS.md)** - Current accounting system status and features
- Features: Chart of accounts, journal entries, financial reporting, multi-currency support

### 💰 Sales Module  
- **[Sales Model](SALES_MODEL_ENABLED.md)** - Sales management and tracking system
- **[Sales Inventory](SALES_INVENTORY_README.md)** - Sales and inventory management integration
- Features: Sales orders, quotations, customer management, sales analytics

### 👥 Customer Management Module
- **[Customer Management](CUSTOMER_MANAGEMENT_ENABLED.md)** - Complete customer management system
- **[Customer Management Complete](CUSTOMER_MANAGEMENT_COMPLETE.md)** - Customer management completion status
- **[Customer Enhancement](CUSTOMER_ENHANCEMENT_COMPLETE.md)** - Customer module enhancements
- **[Customer Enhancement Status](CUSTOMER_ENHANCEMENT_STATUS_FINAL.md)** - Final customer enhancement status
- **[Customer Modal Enhancement](CUSTOMER_MODAL_ENHANCEMENT.md)** - Customer modal improvements
- Features: Customer profiles, contact management, relationship tracking, customer analytics

### 👤 Employee Module
- **[Employee Module](EMPLOYEE_MODULE_ENABLED.md)** - Human resources and employee management
- Features: Employee profiles, role management, attendance tracking, performance management

### 📦 Inventory Module
- **[Items Management Enhancement](ITEMS_MANAGEMENT_ENHANCEMENT_COMPLETE.md)** - Complete inventory management system
- Features: Stock management, product catalog, warehouse management, inventory tracking

## Module Features

Each module includes:
- ✅ **Database Models** - SQLAlchemy models with proper relationships
- ✅ **API Routes** - FastAPI routes with full CRUD operations
- ✅ **Frontend Components** - React components with TypeScript
- ✅ **Mobile Support** - Flutter integration for all apps
- ✅ **Multi-language** - Support for dynamic translations
- ✅ **Multi-tenant** - Branch-based data isolation

## Module Architecture

All modules follow the same architectural pattern:
```
Module/
├── models/        # Database models
├── schemas/       # Pydantic schemas  
├── routers/       # API routes
├── services/      # Business logic
└── frontend/      # UI components
```

## Development Guidelines

When adding new modules:
1. Follow the existing module structure
2. Include comprehensive documentation
3. Add proper test coverage
4. Ensure mobile compatibility
5. Support multi-language features
6. Implement proper permissions 