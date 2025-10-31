# 🔄 TSH Online Store + ERP Unified Database Strategy

## Current Situation

### Existing Supabase Database (29 Tables)
The Supabase database currently contains tables from the **TSH Online Store** project:

#### Core E-commerce Tables ✅
- `users` - User accounts (UUID-based, linked to Supabase Auth)
- `user_profiles` - Extended user information
- `products` - Product catalog (with Zoho sync)
- `product_prices` - Multi-pricelist pricing
- `pricelists` - Different price lists
- `cart_items` - Shopping cart
- `orders` - Customer orders
- `order_items` - Order line items
- `customers` - Customer information

#### Sync & Integration Tables ✅
- `sync_logs`, `sync_metadata`, `sync_cursors`, `sync_jobs` - Zoho synchronization
- `webhook_logs` - Webhook processing logs
- `financial_cache` - Cached financial data

#### Analytics & Telemetry Tables ✅
- `telemetry_events`, `telemetry_errors`, `telemetry_performance`
- `telemetry_api_calls`, `telemetry_sessions`, `telemetry_daily_stats`
- `visitor_profiles`, `visitor_behavior_events`, `visitor_interests`, `visitor_recommendations`

#### AI & Support Tables ✅
- `ai_error_logs`, `ai_fixes`, `ai_insights`
- `auth_sessions` - Authentication sessions

### ERP System Requirements (Missing Tables)

The ERP system needs additional tables that don't exist yet:

#### Organization Structure 🆕
- `branches` - Company branches/locations
- `departments` - Organizational departments
- `warehouses` - Inventory warehouses
- `currencies` - Multi-currency support

#### User Management & Security 🆕
- `roles` - User roles (Admin, Manager, Salesperson, etc.)
- `permissions` - Granular permissions
- `role_permissions` - Role-permission mapping
- `user_roles` - User-role assignments
- `login_attempts` - Security tracking
- `security_events` - Security event logging
- `trusted_devices` - Multi-factor authentication
- `auth_tokens` - Token management

#### HR Management 🆕
- `employees` - Employee records
- `employee_documents` - Employee files
- `attendance` - Time tracking
- `leave_requests` - Leave management
- `payroll` - Salary processing

#### Inventory Management 🆕
- `items` - Inventory items (extends products)
- `stock_movements` - Stock transactions
- `stock_adjustments` - Stock corrections
- `purchase_orders` - Procurement
- `purchase_order_items` - PO line items

#### Sales & CRM 🆕
- `sales_orders` - Sales transactions (extends orders)
- `invoices` - Invoice generation
- `invoice_items` - Invoice line items
- `quotations` - Price quotes
- `salesperson_assignments` - Territory management

#### Accounting & Finance 🆕
- `chart_of_accounts` - Accounting structure
- `accounts` - Account balances
- `journal_entries` - Double-entry transactions
- `journal_entry_lines` - Transaction details
- `payment_terms` - Payment conditions
- `tax_rates` - Tax configuration

#### POS & Cashflow 🆕
- `pos_sessions` - POS shift management
- `pos_transactions` - Point of sale transactions
- `cash_registers` - Register management
- `money_transfers` - Fund transfers between locations

#### Notifications 🆕
- `notifications` - Unified notification system
- `notification_preferences` - User notification settings

---

## 📋 Migration Strategy

### Phase 1: Foundation Tables (Priority: HIGH)
Create core organizational and security tables that everything else depends on.

```sql
-- Create these tables FIRST
1. currencies
2. branches
3. departments
4. warehouses
5. roles
6. permissions
7. role_permissions
```

### Phase 2: Enhanced User Management (Priority: HIGH)
Extend the existing user system with ERP features.

```sql
-- Modify existing users table to add ERP fields:
ALTER TABLE users ADD COLUMN IF NOT EXISTS role_id INTEGER REFERENCES roles(id);
ALTER TABLE users ADD COLUMN IF NOT EXISTS branch_id INTEGER REFERENCES branches(id);
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR(255); -- For non-Supabase auth users

-- Create new security tables:
8. user_roles
9. login_attempts
10. security_events
11. trusted_devices
12. auth_tokens
```

### Phase 3: HR & Employee Management (Priority: MEDIUM)
```sql
13. employees
14. employee_documents
15. attendance
16. leave_requests
17. payroll
```

### Phase 4: Inventory Management (Priority: HIGH)
```sql
-- Extend existing products table:
ALTER TABLE products ADD COLUMN IF NOT EXISTS branch_id INTEGER REFERENCES branches(id);
ALTER TABLE products ADD COLUMN IF NOT EXISTS reorder_level NUMERIC DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS unit_of_measure VARCHAR(20) DEFAULT 'unit';

-- Create new inventory tables:
18. items (simplified view of products for mobile apps)
19. stock_movements
20. stock_adjustments
21. purchase_orders
22. purchase_order_items
```

### Phase 5: Enhanced Sales & CRM (Priority: HIGH)
```sql
-- Extend existing orders table:
ALTER TABLE orders ADD COLUMN IF NOT EXISTS salesperson_id INTEGER;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS branch_id INTEGER REFERENCES branches(id);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS invoice_id INTEGER;

-- Extend existing customers table:
ALTER TABLE customers ADD COLUMN IF NOT EXISTS salesperson_id INTEGER;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS pricelist_id INTEGER REFERENCES pricelists(id);

-- Create new sales tables:
23. sales_orders (enhanced view of orders)
24. invoices
25. invoice_items
26. quotations
27. salesperson_assignments
```

### Phase 6: Accounting & Finance (Priority: MEDIUM)
```sql
28. chart_of_accounts
29. accounts
30. journal_entries
31. journal_entry_lines
32. payment_terms
33. tax_rates
```

### Phase 7: POS & Cashflow (Priority: MEDIUM)
```sql
34. pos_sessions
35. pos_transactions
36. cash_registers
37. money_transfers
```

### Phase 8: Notifications (Priority: LOW)
```sql
38. notifications
39. notification_preferences
```

---

## 🎯 Implementation Approach

### Option 1: Incremental Migration (RECOMMENDED)
Add ERP tables gradually without breaking existing online store functionality.

**Advantages:**
- ✅ Zero downtime
- ✅ Online store continues working
- ✅ Can test each phase independently
- ✅ Rollback is easier

**Process:**
1. Create new tables without foreign keys first
2. Add data to new tables
3. Add foreign keys after data is populated
4. Update application code to use new tables
5. Test thoroughly before next phase

### Option 2: Big Bang Migration
Create all tables at once.

**Advantages:**
- ✅ Faster initial setup
- ✅ All relationships defined upfront

**Disadvantages:**
- ❌ Higher risk
- ❌ Harder to debug issues
- ❌ All-or-nothing approach

---

## 📝 Detailed Migration Plan

### Step 1: Create Unified Migration File

I'll create a special migration file that:
1. **Checks** what tables already exist
2. **Skips** creating tables that exist
3. **Only creates** missing ERP tables
4. **Adds new columns** to existing tables (if they don't exist)

### Step 2: Handle Data Compatibility

#### Users Table Compatibility
```sql
-- Online Store uses UUID for users (Supabase Auth)
-- ERP expects INTEGER id

SOLUTION: Keep UUID as primary key, add INTEGER employee_id for ERP references
ALTER TABLE users ADD COLUMN employee_id INTEGER UNIQUE;
```

#### Products Table Compatibility
```sql
-- Online Store has: zoho_item_id, sku, name, price, stock_quantity
-- ERP needs: branch_id, warehouse_id, reorder_level, unit_of_measure

SOLUTION: Add ERP fields with defaults
ALTER TABLE products
  ADD COLUMN IF NOT EXISTS branch_id INTEGER REFERENCES branches(id),
  ADD COLUMN IF NOT EXISTS reorder_level NUMERIC DEFAULT 10,
  ADD COLUMN IF NOT EXISTS unit_of_measure VARCHAR(20) DEFAULT 'unit';
```

#### Orders Table Compatibility
```sql
-- Online Store has: user_id (UUID), items, total
-- ERP needs: salesperson_id, branch_id, invoice_id

SOLUTION: Add ERP tracking fields
ALTER TABLE orders
  ADD COLUMN IF NOT EXISTS salesperson_id INTEGER,
  ADD COLUMN IF NOT EXISTS branch_id INTEGER REFERENCES branches(id),
  ADD COLUMN IF NOT EXISTS invoice_id INTEGER;
```

### Step 3: Create Initial Data

```sql
-- Create default currency
INSERT INTO currencies (code, name, symbol, exchange_rate)
VALUES ('IQD', 'Iraqi Dinar', 'د.ع', 1.00);

-- Create default branch
INSERT INTO branches (name, code, is_active, currency_id)
VALUES ('Main Branch', 'MAIN', true, 1);

-- Create default roles
INSERT INTO roles (name, description) VALUES
  ('Admin', 'Full system access'),
  ('Manager', 'Branch/department management'),
  ('Salesperson', 'Sales and customer management'),
  ('Cashier', 'POS operations'),
  ('Inventory Manager', 'Stock management'),
  ('Accountant', 'Financial operations'),
  ('HR Manager', 'Human resources');

-- Link existing users to default branch
UPDATE users SET branch_id = 1 WHERE branch_id IS NULL;
```

---

## 🔧 Implementation Commands

### Step 1: Create Unified Migration Script

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/database
alembic revision -m "unified_online_store_erp_migration"
```

### Step 2: Run Migration

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/database
PYTHONPATH=/Users/khaleelal-mulla/TSH_ERP_Ecosystem alembic upgrade head
```

### Step 3: Verify Migration

```sql
-- Check all tables exist
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Verify data integrity
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
```

---

## 🎨 Application Integration

### Frontend (Next.js - Online Store)
**NO CHANGES NEEDED** ✅

The online store will continue using:
- `products` table (now with extra ERP fields that don't affect the store)
- `orders` table (with optional ERP fields)
- `users` table (UUID-based as before)

### Backend (FastAPI - ERP System)
**UPDATES NEEDED** 📝

1. **Update User Model** - Support both UUID and employee_id
2. **Update Product Queries** - Include branch filtering
3. **Update Order Processing** - Add salesperson and branch tracking
4. **Add New Endpoints** - For ERP-specific operations

### Mobile Apps (Flutter)
**UPDATES NEEDED** 📝

1. **Salesperson App** - Use employee_id for authentication
2. **Inventory App** - Use branch_id for stock management
3. **POS App** - Use branch_id and pos_session_id

---

## 🚀 Next Steps

1. **Review this strategy** - Confirm approach works for your needs
2. **Create unified migration** - I'll generate the SQL migration file
3. **Test in development** - Run migration on Supabase
4. **Update application code** - Modify ERP backend to use unified schema
5. **Deploy incrementally** - Roll out features one at a time

---

## ✅ Benefits of Unified Database

1. **Single Source of Truth** - All data in one place
2. **Simplified Sync** - No need to sync between databases
3. **Unified Reporting** - Combined analytics across online store + ERP
4. **Cost Savings** - One database subscription instead of two
5. **Better Performance** - No cross-database queries
6. **Easier Maintenance** - One schema to manage

---

## ⚠️ Considerations

1. **RLS (Row Level Security)** - Ensure Supabase policies don't block ERP operations
2. **Backup Strategy** - Take database backup before migration
3. **Testing** - Thoroughly test online store after migration
4. **Rollback Plan** - Keep migration rollback scripts ready

---

**Created**: October 30, 2025
**Status**: Ready for Implementation
**Next Step**: Generate unified migration file
