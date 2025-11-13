# Consumer App Troubleshooting Guide - CRITICAL INSTRUCTIONS

**Created:** November 13, 2025  
**Authority Level:** CRITICAL - MUST FOLLOW  
**Last Incident:** November 13, 2025 - Consumer app showed "Failed to load products"

---

## 🚨 CRITICAL ISSUE: Consumer App Shows "Failed to Load Products"

### Symptom
```
Consumer app displays: "فشل في تحميل المنتجات" (Failed to load products)
API returns: {"status":"success","count":0,"items":[]}
```

---

## 🔍 Root Cause

### The Problem
**TWO SEPARATE PRICING SYSTEMS** exist in the database:

**System 1 (Legacy - What Consumer API Uses):**
```
pricing_lists  →  product_prices
    ↓                    ↓
  (empty)            (empty)
```

**System 2 (New - What Zoho Sync Populates):**
```
price_lists  →  price_list_items  →  migration_items
     ↓                 ↓                    ↓
   (7 lists)      (7,825 items)       (2,219 items)
```

### The Disconnect

Consumer API queries:
```sql
FROM products p
JOIN product_prices pp ON pp.product_id = p.id
JOIN pricing_lists pl ON pp.pricing_list_id = pl.id
WHERE pl.code = 'consumer_iqd'
```

But `product_prices` is **EMPTY** because Zoho sync populates `price_list_items` instead!

---

## ✅ MANDATORY CHECKS - Run These ALWAYS

### Check 1: Verify Product Prices Exist

```sql
-- This MUST return > 0 for consumer app to work
SELECT COUNT(*) FROM product_prices;

-- Check consumer prices specifically
SELECT COUNT(*) FROM product_prices pp
JOIN pricing_lists pl ON pp.pricing_list_id = pl.id
WHERE pl.code = 'consumer_iqd';
```

**Expected Result:**
- Total product_prices: **7,825+**
- Consumer prices: **1,304+**

**If 0:** Consumer app will fail! ❌

### Check 2: Verify Pricing Lists Populated

```sql
-- This MUST return > 0
SELECT COUNT(*) FROM pricing_lists;

-- Should show all price lists
SELECT id, name, price_list_type, is_active FROM pricing_lists;
```

**Expected Result:** 7 pricing lists

**If 0:** Product prices foreign key will fail! ❌

### Check 3: Verify Products Have Prices

```sql
-- Test the exact query consumer API uses
SELECT COUNT(*)
FROM products p
LEFT JOIN LATERAL (
    SELECT pp.price
    FROM product_prices pp
    JOIN pricing_lists pl ON pp.pricing_list_id = pl.id
    WHERE pp.product_id = p.id
      AND pl.code = 'consumer_iqd'
      AND pp.price > 0
    LIMIT 1
) consumer_price ON true
WHERE p.is_active = true
  AND p.actual_available_stock > 0
  AND p.zoho_item_id IS NOT NULL
  AND consumer_price.price IS NOT NULL;
```

**Expected Result:** 1,304+ products

**If 0:** Consumer app will show no products! ❌

---

## 🛠️ SOLUTION: Price Data Migration

### When to Run This

**Run immediately if:**
- Consumer app shows "Failed to load products"
- `product_prices` table is empty
- After fresh deployment
- After database restore
- After Zoho sync if prices missing

### Migration Script

**ALWAYS run these in order:**

#### Step 1: Populate `pricing_lists`

```sql
-- Check if empty
SELECT COUNT(*) FROM pricing_lists;

-- If 0, populate from price_lists
INSERT INTO pricing_lists (id, name, price_list_type, description, is_active, valid_from, created_at, updated_at)
SELECT 
    id,
    name_en,
    'standard',
    description_en,
    is_active,
    effective_from::date,
    created_at,
    updated_at
FROM price_lists
ON CONFLICT (id) DO NOTHING;

-- Verify
SELECT COUNT(*) FROM pricing_lists;
-- Should show 7
```

#### Step 2: Migrate Price Data

```sql
-- Check if empty
SELECT COUNT(*) FROM product_prices;

-- If 0, migrate from price_list_items
INSERT INTO product_prices (product_id, pricing_list_id, pricelist_id, price, currency, created_at, updated_at)
SELECT DISTINCT ON (p.id, pli.price_list_id)
    p.id as product_id,
    pli.price_list_id as pricing_list_id,
    pli.price_list_id as pricelist_id,
    pli.unit_price as price,
    pl.currency::varchar(3),
    NOW() as created_at,
    NOW() as updated_at
FROM price_list_items pli
JOIN migration_items mi ON pli.item_id = mi.id
JOIN products p ON p.zoho_item_id = mi.zoho_item_id  -- KEY LINK!
JOIN price_lists pl ON pli.price_list_id = pl.id
WHERE pli.is_active = true
  AND p.is_active = true
  AND pli.unit_price > 0
  AND mi.zoho_item_id IS NOT NULL
  AND p.zoho_item_id IS NOT NULL;

-- Verify
SELECT 
    'Total product_prices' as metric, 
    COUNT(*)::text as count 
FROM product_prices
UNION ALL
SELECT 
    'Consumer prices',
    COUNT(*)::text
FROM product_prices pp
JOIN pricing_lists pl ON pp.pricing_list_id = pl.id
WHERE pl.code = 'consumer_iqd';

-- Should show:
-- Total: 7,825
-- Consumer: 1,304
```

#### Step 3: Restart Application

```bash
# On production server
ssh root@167.71.39.50
cd /home/deploy/TSH_ERP_Ecosystem
docker compose restart app

# Wait 30 seconds for startup
sleep 30
```

#### Step 4: Verify Consumer API

```bash
# Test API
curl -s "https://erp.tsh.sale/api/consumer/products?limit=1" | python3 -m json.tool

# Should return products with prices
```

---

## 🔄 AUTOMATIC MIGRATION SCRIPT

Save this as `/home/deploy/TSH_ERP_Ecosystem/scripts/migrate_consumer_prices.sh`:

```bash
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
```

**Usage:**
```bash
chmod +x scripts/migrate_consumer_prices.sh
./scripts/migrate_consumer_prices.sh
```

---

## 🚫 PREVENTION: What NOT to Do

### ❌ NEVER Do These:

1. **Don't assume products sync = prices sync**
   - Products go to `products` table
   - Prices go to `price_list_items` table
   - Consumer API needs `product_prices` table!

2. **Don't skip price migration after deployment**
   - Always check `product_prices` count
   - Run migration if empty

3. **Don't ignore empty consumer API results**
   - If API returns 0 products, investigate immediately
   - Check both product and price tables

4. **Don't modify consumer API query without testing**
   - The query structure is critical
   - Test against actual data before deploying

---

## ✅ PREVENTION: What TO Do

### Always Do These:

1. **After every deployment:**
   ```bash
   # Check product_prices count
   docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp \
     -c "SELECT COUNT(*) FROM product_prices;"
   ```

2. **After Zoho sync:**
   ```bash
   # Verify prices migrated
   docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp \
     -c "SELECT COUNT(*) FROM product_prices pp
         JOIN pricing_lists pl ON pp.pricing_list_id = pl.id
         WHERE pl.code = 'consumer_iqd';"
   ```

3. **After database restore:**
   ```bash
   # Run migration script
   ./scripts/migrate_consumer_prices.sh
   ```

4. **In deployment checklist:**
   ```
   □ Products synced from Zoho
   □ Prices migrated to product_prices
   □ Consumer API tested
   □ Consumer app loads products
   ```

---

## 📊 Monitoring & Alerts

### Set Up These Alerts

**Alert 1: Empty product_prices**
```sql
-- Alert if this returns 0
SELECT COUNT(*) FROM product_prices;
```

**Alert 2: No consumer prices**
```sql
-- Alert if this returns 0
SELECT COUNT(*) FROM product_prices pp
JOIN pricing_lists pl ON pp.pricing_list_id = pl.id
WHERE pl.code = 'consumer_iqd';
```

**Alert 3: Consumer API returns 0**
```bash
# Alert if this returns 0
curl -s "https://erp.tsh.sale/api/consumer/products" | jq '.count'
```

---

## 🔧 Troubleshooting Steps

### Issue: Consumer API returns 0 products

**Step 1:** Check products exist
```sql
SELECT COUNT(*) FROM products WHERE is_active = true;
-- Should be > 0
```

**Step 2:** Check product_prices exist
```sql
SELECT COUNT(*) FROM product_prices;
-- Should be > 0
```

**Step 3:** Check pricing_lists exist
```sql
SELECT COUNT(*) FROM pricing_lists;
-- Should be 7
```

**Step 4:** If any are 0, run migration script
```bash
./scripts/migrate_consumer_prices.sh
```

**Step 5:** Verify API
```bash
curl "https://erp.tsh.sale/api/consumer/products?limit=1"
```

---

## 📝 Database Schema Reference

### The Two Systems

**System 1 (Consumer API):**
```
products (id, zoho_item_id, ...)
    ↓
product_prices (product_id, pricing_list_id, price, ...)
    ↓
pricing_lists (id, name, code, ...)
```

**System 2 (Zoho Sync):**
```
migration_items (id, zoho_item_id, ...)
    ↓
price_list_items (item_id, price_list_id, unit_price, ...)
    ↓
price_lists (id, code, name_en, ...)
```

**The Bridge:** `zoho_item_id` field links both systems

---

## 🎯 Quick Reference

### Is Consumer App Working?

```bash
# Quick check
curl -s "https://erp.tsh.sale/api/consumer/products?limit=1" | jq '.count'

# If returns > 0: ✅ Working
# If returns 0: ❌ Run migration
```

### Run Migration

```bash
ssh root@167.71.39.50
cd /home/deploy/TSH_ERP_Ecosystem
./scripts/migrate_consumer_prices.sh
```

### Verify Success

```bash
# Should return products with prices
curl -s "https://erp.tsh.sale/api/consumer/products?limit=1" | jq '.'
```

---

## 📚 Related Files

- **Consumer API Code:** `app/routers/consumer_api.py` (line 100-200)
- **Migration Script:** `scripts/migrate_consumer_prices.sh`
- **SQL Migration:** `migrate_prices_to_product_prices.sql`
- **Incident Report:** `CONSUMER_APP_FIXED_NOV13_2025.md`

---

## 🎓 Lessons Learned

### Why This Happened

1. **Legacy vs New Architecture:** System has evolved, two pricing tables exist
2. **Incomplete Migration:** Database structure changed but data not migrated
3. **Assumption Error:** Assumed Zoho sync would populate all tables
4. **Missing Check:** No validation after deployment

### How to Prevent

1. **Always check both systems** after Zoho sync
2. **Run migration script** as part of deployment
3. **Add to deployment checklist**
4. **Set up monitoring alerts**
5. **Document the bridge** between systems

---

## ⚡ EMERGENCY FIX

If consumer app is down RIGHT NOW:

```bash
# 1. SSH to server
ssh root@167.71.39.50

# 2. Run this ONE command
docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml exec -T tsh_postgres psql -U tsh_admin -d tsh_erp <<'SQL'
INSERT INTO pricing_lists (id,name,price_list_type,is_active,created_at) SELECT id,name_en,'standard',is_active,created_at FROM price_lists ON CONFLICT DO NOTHING;
INSERT INTO product_prices (product_id,pricing_list_id,pricelist_id,price,currency,created_at) SELECT DISTINCT ON (p.id,pli.price_list_id) p.id,pli.price_list_id,pli.price_list_id,pli.unit_price,pl.currency::varchar(3),NOW() FROM price_list_items pli JOIN migration_items mi ON pli.item_id=mi.id JOIN products p ON p.zoho_item_id=mi.zoho_item_id JOIN price_lists pl ON pli.price_list_id=pl.id WHERE pli.is_active=true AND p.is_active=true AND pli.unit_price>0 AND mi.zoho_item_id IS NOT NULL;
SQL

# 3. Restart app
docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml restart app

# Done! Consumer app should work now.
```

---

**REMEMBER:** This issue has happened once. With these instructions, it should **NEVER** happen again!

**Last Updated:** November 13, 2025  
**Status:** ✅ RESOLVED  
**Prevention:** ✅ IN PLACE

---

**END OF TROUBLESHOOTING GUIDE**

