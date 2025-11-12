-- ============================================================================
-- TSH NeuroLink - TDS Notification Rules
-- Version: 1.0.0
-- Date: November 10, 2025
--
-- This migration creates notification rules for TDS (TSH Datasync Core) events
-- Automatically creates notifications when:
-- - Price lists are updated
-- - Sync operations complete/fail
-- - Stock discrepancies detected
-- - Image sync completes
-- ============================================================================

-- ============================================================================
-- 1. PRICE LIST UPDATE NOTIFICATIONS
-- ============================================================================

INSERT INTO neurolink_notification_rules (
    name,
    description,
    is_active,
    priority,
    source_module,
    event_type_pattern,
    notification_template,
    cooldown_minutes,
    max_per_hour
) VALUES (
    'price_list_updated_sales_team',
    'Notify sales team when consumer price list is updated',
    true,
    100,  -- High priority
    'tds',
    'price_list.updated',
    '{
        "title": "💰 Price List Updated: {{price_list_name}}",
        "body": "{{products_updated}} products have been updated in {{price_list_name}}. Please review the new prices before quoting to customers.",
        "severity": "warning",
        "action_url": "/products/prices",
        "action_label": "View Updated Prices",
        "channels": ["in_app", "push", "email"],
        "recipient_roles": ["sales_rep", "sales_manager", "warehouse_manager"]
    }'::jsonb,
    60,  -- 1 hour cooldown (don't spam on multiple syncs)
    3    -- Max 3 per hour
)
ON CONFLICT (name) DO UPDATE SET
    notification_template = EXCLUDED.notification_template,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- 2. SYNC COMPLETION NOTIFICATIONS (Success)
-- ============================================================================

INSERT INTO neurolink_notification_rules (
    name,
    description,
    is_active,
    priority,
    source_module,
    event_type_pattern,
    condition_dsl,
    notification_template,
    cooldown_minutes
) VALUES (
    'sync_completed_success',
    'Notify admins when sync completes successfully with high success rate',
    true,
    50,
    'tds',
    'sync.completed',
    '{
        "conditions": [
            {"field": "success_rate", "operator": ">=", "value": 95}
        ]
    }'::jsonb,
    '{
        "title": "✅ Sync Completed: {{entity_type}}",
        "body": "Successfully synced {{successful}}/{{total_processed}} {{entity_type}} items ({{success_rate}}% success rate) in {{duration_seconds}}s.",
        "severity": "info",
        "action_url": "/tds-admin/sync",
        "action_label": "View Sync Details",
        "channels": ["in_app"],
        "recipient_roles": ["admin", "super_admin"]
    }'::jsonb,
    1440  -- 24 hours cooldown (daily summary)
)
ON CONFLICT (name) DO UPDATE SET
    notification_template = EXCLUDED.notification_template,
    condition_dsl = EXCLUDED.condition_dsl,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- 3. SYNC COMPLETION NOTIFICATIONS (Low Success Rate)
-- ============================================================================

INSERT INTO neurolink_notification_rules (
    name,
    description,
    is_active,
    priority,
    source_module,
    event_type_pattern,
    condition_dsl,
    notification_template,
    max_per_hour
) VALUES (
    'sync_completed_low_success',
    'Alert admins when sync has low success rate',
    true,
    90,  -- Higher priority for problems
    'tds',
    'sync.completed',
    '{
        "conditions": [
            {"field": "success_rate", "operator": "<", "value": 90}
        ]
    }'::jsonb,
    '{
        "title": "⚠️ Sync Issues: {{entity_type}}",
        "body": "Sync completed with only {{success_rate}}% success rate. {{failed}} items failed out of {{total_processed}}. Please investigate.",
        "severity": "warning",
        "action_url": "/tds-admin/alerts",
        "action_label": "View Failures",
        "channels": ["in_app", "email"],
        "recipient_roles": ["admin", "super_admin", "tech_support"]
    }'::jsonb,
    5  -- Max 5 alerts per hour
)
ON CONFLICT (name) DO UPDATE SET
    notification_template = EXCLUDED.notification_template,
    condition_dsl = EXCLUDED.condition_dsl,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- 4. SYNC FAILED NOTIFICATIONS
-- ============================================================================

INSERT INTO neurolink_notification_rules (
    name,
    description,
    is_active,
    priority,
    source_module,
    event_type_pattern,
    notification_template,
    max_per_hour
) VALUES (
    'sync_failed_critical',
    'Critical alert when sync fails completely',
    true,
    95,  -- Very high priority
    'tds',
    'sync.failed',
    '{
        "title": "🚨 CRITICAL: Sync Failed - {{entity_type}}",
        "body": "Sync operation failed: {{error_message}}. Immediate action required to restore data synchronization.",
        "severity": "critical",
        "action_url": "/tds-admin/alerts",
        "action_label": "View Error Details",
        "channels": ["in_app", "email", "push"],
        "recipient_roles": ["admin", "super_admin", "tech_support"]
    }'::jsonb,
    10  -- Max 10 per hour (prevent spam during outage)
)
ON CONFLICT (name) DO UPDATE SET
    notification_template = EXCLUDED.notification_template,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- 5. STOCK DISCREPANCY NOTIFICATIONS
-- ============================================================================

INSERT INTO neurolink_notification_rules (
    name,
    description,
    is_active,
    priority,
    source_module,
    event_type_pattern,
    condition_dsl,
    notification_template,
    cooldown_minutes
) VALUES (
    'stock_discrepancy_large',
    'Alert when large stock discrepancy is detected between Zoho and local',
    true,
    85,
    'tds',
    'stock.discrepancy',
    '{
        "conditions": [
            {"field": "discrepancy", "operator": "abs_gt", "value": 50}
        ]
    }'::jsonb,
    '{
        "title": "⚠️ Stock Discrepancy: {{product_name}}",
        "body": "Large stock difference detected for {{product_name}} (SKU: {{product_sku}}). Zoho: {{zoho_stock}}, Local: {{local_stock}}, Difference: {{discrepancy}} units.",
        "severity": "warning",
        "action_url": "/inventory/products/{{product_sku}}",
        "action_label": "Review Stock",
        "channels": ["in_app", "email"],
        "recipient_roles": ["inventory_manager", "warehouse_manager", "admin"]
    }'::jsonb,
    120  -- 2 hours cooldown per product
)
ON CONFLICT (name) DO UPDATE SET
    notification_template = EXCLUDED.notification_template,
    condition_dsl = EXCLUDED.condition_dsl,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- 6. IMAGE SYNC NOTIFICATIONS
-- ============================================================================

INSERT INTO neurolink_notification_rules (
    name,
    description,
    is_active,
    priority,
    source_module,
    event_type_pattern,
    condition_dsl,
    notification_template,
    cooldown_minutes
) VALUES (
    'image_sync_completed',
    'Notify when image sync completes',
    true,
    40,
    'tds',
    'image_sync.completed',
    '{
        "conditions": [
            {"field": "images_downloaded", "operator": ">", "value": 0}
        ]
    }'::jsonb,
    '{
        "title": "📸 Product Images Synced",
        "body": "Downloaded {{images_downloaded}} product images ({{images_failed}} failed) for {{products_processed}} products in {{duration_seconds}}s.",
        "severity": "info",
        "action_url": "/tds-admin/sync",
        "action_label": "View Details",
        "channels": ["in_app"],
        "recipient_roles": ["admin", "warehouse_manager"]
    }'::jsonb,
    360  -- 6 hours cooldown
)
ON CONFLICT (name) DO UPDATE SET
    notification_template = EXCLUDED.notification_template,
    condition_dsl = EXCLUDED.condition_dsl,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- 7. COMMENTS
-- ============================================================================

COMMENT ON TABLE neurolink_notification_rules IS 'Notification rules for converting events into user notifications';

-- ============================================================================
-- 8. VERIFICATION
-- ============================================================================

-- Show created rules
SELECT
    name,
    source_module,
    event_type_pattern,
    is_active,
    priority,
    cooldown_minutes,
    max_per_hour
FROM neurolink_notification_rules
WHERE source_module = 'tds'
ORDER BY priority DESC;

SELECT 'TDS notification rules created successfully!' as result;
