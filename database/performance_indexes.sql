-- ===============================================
-- TSH ERP - Performance Optimization Indexes
-- ===============================================
-- Date: November 5, 2025
-- Purpose: Improve query performance with strategic indexes
-- Expected Impact: 20-30% query performance improvement
-- ===============================================

-- IMPORTANT: These indexes are created with CONCURRENTLY to avoid table locks
-- This means the database can continue serving queries while indexes are built

-- ===============================================
-- PRODUCTS TABLE INDEXES
-- ===============================================

-- Active products filter (most common query)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_is_active
ON products(is_active)
WHERE is_active = true;

-- Category browsing
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_category_id
ON products(category_id)
WHERE is_active = true;

-- Product search by SKU
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_sku
ON products(sku);

-- Zoho sync tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_zoho_item_id
ON products(zoho_item_id)
WHERE zoho_item_id IS NOT NULL;

-- Stock management queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_stock_quantity
ON products(stock_quantity)
WHERE is_active = true;

-- Low stock alerts
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_low_stock
ON products(stock_quantity, reorder_level)
WHERE is_active = true AND stock_quantity <= reorder_level;

-- Product creation date (for recent products)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_created_at
ON products(created_at DESC);

-- ===============================================
-- ORDERS TABLE INDEXES
-- ===============================================

-- Customer orders lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer_id
ON orders(customer_id);

-- Order date range queries (reports)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_created_at
ON orders(created_at DESC);

-- Order status filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status
ON orders(status);

-- Composite index for customer orders by date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer_date
ON orders(customer_id, created_at DESC);

-- Zoho sync tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_zoho_salesorder_id
ON orders(zoho_salesorder_id)
WHERE zoho_salesorder_id IS NOT NULL;

-- Branch-specific orders
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_branch_id
ON orders(branch_id)
WHERE branch_id IS NOT NULL;

-- ===============================================
-- ORDER_ITEMS TABLE INDEXES
-- ===============================================

-- Order items lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_order_id
ON order_items(order_id);

-- Product sales analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_product_id
ON order_items(product_id);

-- Composite for order-product lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_order_product
ON order_items(order_id, product_id);

-- ===============================================
-- CUSTOMERS TABLE INDEXES
-- ===============================================

-- Email lookup (login, password reset)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_email
ON customers(email);

-- Phone lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_phone
ON customers(phone)
WHERE phone IS NOT NULL;

-- Zoho sync tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_zoho_contact_id
ON customers(zoho_contact_id)
WHERE zoho_contact_id IS NOT NULL;

-- Customer type filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_customer_type
ON customers(customer_type);

-- Active customers
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_is_active
ON customers(is_active)
WHERE is_active = true;

-- ===============================================
-- USERS TABLE INDEXES
-- ===============================================

-- Email lookup (login)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email
ON users(email);

-- Username lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username
ON users(username)
WHERE username IS NOT NULL;

-- Role-based queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role_id
ON users(role_id);

-- Active users
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_is_active
ON users(is_active)
WHERE is_active = true;

-- Branch assignment
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_branch_id
ON users(branch_id)
WHERE branch_id IS NOT NULL;

-- ===============================================
-- INVOICES TABLE INDEXES
-- ===============================================

-- Customer invoices
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoices_customer_id
ON invoices(customer_id);

-- Invoice date queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoices_invoice_date
ON invoices(invoice_date DESC);

-- Payment status filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoices_payment_status
ON invoices(payment_status);

-- Due date for overdue reports
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoices_due_date
ON invoices(due_date)
WHERE payment_status != 'paid';

-- Order-invoice relationship
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoices_order_id
ON invoices(order_id)
WHERE order_id IS NOT NULL;

-- Zoho sync tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoices_zoho_invoice_id
ON invoices(zoho_invoice_id)
WHERE zoho_invoice_id IS NOT NULL;

-- ===============================================
-- PAYMENTS TABLE INDEXES
-- ===============================================

-- Invoice payments
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_invoice_id
ON payments(invoice_id);

-- Payment date queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_payment_date
ON payments(payment_date DESC);

-- Payment method analytics
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_payment_method
ON payments(payment_method);

-- Customer payments
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_customer_id
ON payments(customer_id);

-- ===============================================
-- INVENTORY_TRANSACTIONS TABLE INDEXES
-- ===============================================

-- Product inventory history
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_inventory_transactions_product_id
ON inventory_transactions(product_id);

-- Transaction date queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_inventory_transactions_created_at
ON inventory_transactions(created_at DESC);

-- Transaction type filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_inventory_transactions_transaction_type
ON inventory_transactions(transaction_type);

-- Warehouse tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_inventory_transactions_warehouse_id
ON inventory_transactions(warehouse_id)
WHERE warehouse_id IS NOT NULL;

-- Composite for product history by date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_inventory_trans_product_date
ON inventory_transactions(product_id, created_at DESC);

-- ===============================================
-- CATEGORIES TABLE INDEXES
-- ===============================================

-- Parent-child category relationships
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_parent_id
ON categories(parent_id)
WHERE parent_id IS NOT NULL;

-- Active categories
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_is_active
ON categories(is_active)
WHERE is_active = true;

-- Category slug for URLs
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_slug
ON categories(slug)
WHERE slug IS NOT NULL;

-- ===============================================
-- PRICES TABLE INDEXES
-- ===============================================

-- Product pricing lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_prices_product_id
ON prices(product_id);

-- Pricelist filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_prices_pricelist_id
ON prices(pricelist_id);

-- Composite for product-pricelist lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_prices_product_pricelist
ON prices(product_id, pricelist_id);

-- ===============================================
-- PRODUCT_IMAGES TABLE INDEXES
-- ===============================================

-- Product images lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_product_images_product_id
ON product_images(product_id);

-- Primary image filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_product_images_is_primary
ON product_images(product_id, is_primary)
WHERE is_primary = true;

-- ===============================================
-- SESSIONS TABLE INDEXES
-- ===============================================

-- User sessions lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_id
ON sessions(user_id);

-- Session token lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_session_token
ON sessions(session_token);

-- Active sessions
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_is_active
ON sessions(is_active)
WHERE is_active = true;

-- Session expiry cleanup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_expires_at
ON sessions(expires_at)
WHERE is_active = true;

-- ===============================================
-- NOTIFICATIONS TABLE INDEXES
-- ===============================================

-- User notifications
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_id
ON notifications(user_id);

-- Unread notifications
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_is_read
ON notifications(user_id, is_read)
WHERE is_read = false;

-- Notification date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_created_at
ON notifications(created_at DESC);

-- ===============================================
-- AUDIT_LOGS TABLE INDEXES
-- ===============================================

-- User activity audit
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_id
ON audit_logs(user_id);

-- Action type filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_action
ON audit_logs(action);

-- Entity tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_entity_type
ON audit_logs(entity_type, entity_id);

-- Timestamp for log queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp
ON audit_logs(timestamp DESC);

-- ===============================================
-- ZOHO SYNC QUEUE TABLE INDEXES
-- ===============================================

-- Pending sync items
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_zoho_sync_queue_status
ON tds_sync_queue(status)
WHERE status = 'pending';

-- Entity sync tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_zoho_sync_queue_entity
ON tds_sync_queue(entity_type, entity_id);

-- Failed sync items for retry
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_zoho_sync_queue_failed
ON tds_sync_queue(status, retry_count)
WHERE status = 'failed';

-- Created date for queue processing
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_zoho_sync_queue_created
ON tds_sync_queue(created_at)
WHERE status = 'pending';

-- ===============================================
-- FULL TEXT SEARCH INDEXES (PostgreSQL)
-- ===============================================

-- Product search (name, description, SKU)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_search
ON products USING gin(to_tsvector('english',
    coalesce(name, '') || ' ' ||
    coalesce(description, '') || ' ' ||
    coalesce(sku, '')
));

-- Customer search (name, email, phone)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_search
ON customers USING gin(to_tsvector('english',
    coalesce(name, '') || ' ' ||
    coalesce(email, '') || ' ' ||
    coalesce(phone, '')
));

-- ===============================================
-- VERIFICATION QUERIES
-- ===============================================

-- Run these queries after index creation to verify:

-- 1. Check all indexes created
-- SELECT
--     schemaname,
--     tablename,
--     indexname,
--     indexdef
-- FROM pg_indexes
-- WHERE schemaname = 'public'
-- ORDER BY tablename, indexname;

-- 2. Check index sizes
-- SELECT
--     schemaname || '.' || tablename AS table,
--     indexname,
--     pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
-- FROM pg_stat_user_indexes
-- ORDER BY pg_relation_size(indexrelid) DESC;

-- 3. Test query performance (example)
-- EXPLAIN ANALYZE
-- SELECT * FROM products
-- WHERE is_active = true
-- AND category_id = 1
-- ORDER BY created_at DESC
-- LIMIT 20;

-- ===============================================
-- MAINTENANCE
-- ===============================================

-- Update table statistics for optimal query planning
ANALYZE products;
ANALYZE orders;
ANALYZE order_items;
ANALYZE customers;
ANALYZE invoices;
ANALYZE payments;
ANALYZE inventory_transactions;
ANALYZE users;
ANALYZE categories;
ANALYZE prices;
ANALYZE product_images;
ANALYZE sessions;
ANALYZE notifications;
ANALYZE audit_logs;
ANALYZE tds_sync_queue;

-- ===============================================
-- NOTES
-- ===============================================

-- 1. CONCURRENTLY means indexes are built without blocking table access
-- 2. Some indexes use WHERE clauses (partial indexes) for efficiency
-- 3. Composite indexes support queries filtering on multiple columns
-- 4. Full-text search indexes enable fast product/customer search
-- 5. Run ANALYZE after creating indexes to update statistics

-- Expected Impact:
-- - 20-30% faster queries on filtered datasets
-- - 40-50% faster JOIN operations
-- - 60-70% faster full-text searches
-- - Improved performance for mobile BFF endpoints
-- - Better response times for admin dashboards

-- ===============================================
-- END OF INDEX DEFINITIONS
-- ===============================================
