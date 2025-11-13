#!/bin/bash
# Automatic Consumer App Price Migration
# Run this if consumer app shows no products

set -e

echo "=================================="
echo "Consumer App Price Migration"
echo "=================================="
echo ""

# Check if migration needed
PRICE_COUNT=$(docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml exec -T tsh_postgres psql -U tsh_admin -d tsh_erp -t -c "SELECT COUNT(*) FROM product_prices;")

if [ "$PRICE_COUNT" -gt 0 ]; then
    echo "✅ product_prices table already populated ($PRICE_COUNT records)"
    echo "No migration needed."
    exit 0
fi

echo "⚠️  product_prices table is empty!"
echo "Running migration..."
echo ""

# Step 1: Populate pricing_lists
echo "Step 1: Populating pricing_lists..."
docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml exec -T tsh_postgres psql -U tsh_admin -d tsh_erp <<'SQL'
INSERT INTO pricing_lists (id, name, price_list_type, description, is_active, valid_from, created_at, updated_at)
SELECT 
    id, name_en, 'standard', description_en, is_active, effective_from::date, created_at, updated_at
FROM price_lists
ON CONFLICT (id) DO NOTHING;
SQL

# Step 2: Migrate prices
echo "Step 2: Migrating price data..."
docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml exec -T tsh_postgres psql -U tsh_admin -d tsh_erp <<'SQL'
INSERT INTO product_prices (product_id, pricing_list_id, pricelist_id, price, currency, created_at, updated_at)
SELECT DISTINCT ON (p.id, pli.price_list_id)
    p.id, pli.price_list_id, pli.price_list_id, pli.unit_price, pl.currency::varchar(3), NOW(), NOW()
FROM price_list_items pli
JOIN migration_items mi ON pli.item_id = mi.id
JOIN products p ON p.zoho_item_id = mi.zoho_item_id
JOIN price_lists pl ON pli.price_list_id = pl.id
WHERE pli.is_active = true AND p.is_active = true AND pli.unit_price > 0
  AND mi.zoho_item_id IS NOT NULL AND p.zoho_item_id IS NOT NULL;
SQL

# Step 3: Verify
echo ""
echo "Step 3: Verifying migration..."
docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml exec -T tsh_postgres psql -U tsh_admin -d tsh_erp -c "
SELECT 'Total product_prices' as metric, COUNT(*)::text as count FROM product_prices
UNION ALL
SELECT 'Consumer prices', COUNT(*)::text FROM product_prices pp
JOIN pricing_lists pl ON pp.pricing_list_id = pl.id WHERE pl.code = 'consumer_iqd';
"

# Step 4: Restart app
echo ""
echo "Step 4: Restarting application..."
docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml restart app

echo ""
echo "✅ Migration complete!"
echo "Consumer app should now show products."
echo ""

