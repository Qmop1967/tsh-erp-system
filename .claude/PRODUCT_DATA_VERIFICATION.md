# Product Data Verification Guide - CRITICAL INSTRUCTIONS

**Created:** November 13, 2025  
**Authority Level:** CRITICAL - MUST VERIFY AFTER EVERY SYNC  
**Purpose:** Ensure products show correct stock, prices, and images in ALL apps

---

## 🎯 MANDATORY VERIFICATION CHECKLIST

**After EVERY Zoho sync, deployment, or data migration, you MUST verify:**

- [ ] ✅ **Stock quantities** are correct
- [ ] ✅ **Prices** are correct (Consumer, Retailer, Wholesale, etc.)
- [ ] ✅ **Images** are displaying properly
- [ ] ✅ **All apps** show consistent data

---

## 📊 VERIFICATION PROCEDURES

### 1. Stock Verification

#### Check Database Stock

```sql
-- Check products with stock
SELECT 
    sku,
    name,
    actual_available_stock,
    stock_on_hand,
    available_stock,
    reorder_level
FROM products
WHERE is_active = true
ORDER BY actual_available_stock DESC
LIMIT 20;

-- Verify stock matches Zoho
-- Compare with Zoho Books actual_available_stock
```

#### Test Stock in Consumer App

**Steps:**
1. Go to https://consumer.tsh.sale
2. Find a product with known stock (e.g., SKU: `tsh00059y`)
3. Verify stock quantity matches database
4. Check "متوفر" (Available) badge shows correctly
5. Test products with 0 stock show "غير متوفر" (Unavailable)

**Expected:**
- ✅ Stock quantities match database
- ✅ "Available" badge shows for stock > 0
- ✅ Stock updates in real-time via webhooks

#### Test Stock in Admin App

**Steps:**
1. Go to https://erp.tsh.sale/admin/products
2. Check stock column matches database
3. Verify stock updates after Zoho sync

**Expected:**
- ✅ Stock matches `actual_available_stock` from database
- ✅ Stock updates automatically via webhooks

---

### 2. Price Verification

#### Check Database Prices

```sql
-- Check Consumer prices
SELECT 
    p.sku,
    p.name,
    pp.price as consumer_price,
    pl.code as price_list_code,
    pp.currency
FROM products p
JOIN product_prices pp ON pp.product_id = p.id
JOIN pricing_lists pl ON pp.pricing_list_id = pl.id
WHERE p.is_active = true
  AND pl.code = 'consumer_iqd'
ORDER BY p.sku
LIMIT 20;

-- Verify all price lists have prices
SELECT 
    pl.code,
    pl.name,
    COUNT(pp.id) as product_count
FROM pricing_lists pl
LEFT JOIN product_prices pp ON pp.pricing_list_id = pl.id
GROUP BY pl.id, pl.code, pl.name
ORDER BY pl.code;
```

#### Test Prices in Consumer App

**Steps:**
1. Go to https://consumer.tsh.sale
2. Check product prices display in IQD (د.ع)
3. Verify prices match Consumer price list
4. Test multiple products across different categories

**Expected:**
- ✅ Prices show in IQD format (e.g., "1,500 د.ع")
- ✅ Prices match Consumer price list from database
- ✅ No products show "0 د.ع" or missing prices
- ✅ Prices update when changed in Zoho

#### Test Prices in Admin App

**Steps:**
1. Go to https://erp.tsh.sale/admin/products
2. Check price columns for all price lists
3. Verify price history is tracked

**Expected:**
- ✅ All price lists show correct prices
- ✅ Price changes are logged
- ✅ Prices sync from Zoho correctly

#### Price List Verification

```sql
-- CRITICAL: Verify Consumer prices exist
SELECT COUNT(*) as consumer_products_with_prices
FROM product_prices pp
JOIN pricing_lists pl ON pp.pricing_list_id = pl.id
WHERE pl.code = 'consumer_iqd';

-- Should return > 0, ideally matching active products count
```

**If 0:** Run price migration script immediately!
```bash
./scripts/migrate_consumer_prices.sh
```

---

### 3. Image Verification

#### Check Database Images

```sql
-- Check products with local images
SELECT 
    sku,
    name,
    zoho_item_id,
    image_url,
    CASE 
        WHEN image_url LIKE '/uploads/%' THEN 'Local'
        WHEN image_url LIKE '%zohoapis.com%' THEN 'Zoho URL'
        WHEN image_url IS NULL OR image_url = '' THEN 'No Image'
        ELSE 'Other'
    END as image_status
FROM products
WHERE is_active = true
ORDER BY image_status, sku
LIMIT 50;

-- Count products with images
SELECT 
    COUNT(*) FILTER (WHERE image_url LIKE '/uploads/%') as local_images,
    COUNT(*) FILTER (WHERE image_url LIKE '%zohoapis.com%') as zoho_urls,
    COUNT(*) FILTER (WHERE image_url IS NULL OR image_url = '') as no_images,
    COUNT(*) as total_active
FROM products
WHERE is_active = true;
```

#### Check Image Files on Server

```bash
# Count downloaded images
ssh root@167.71.39.50 "ls -1 /home/deploy/TSH_ERP_Ecosystem/uploads/products/*.jpg | wc -l"

# Count symlinks (for consumer app)
ssh root@167.71.39.50 "ls -1 /home/deploy/TSH_ERP_Ecosystem/uploads/products/264661*.jpg | wc -l"

# Check specific product image
ssh root@167.71.39.50 "ls -la /home/deploy/TSH_ERP_Ecosystem/uploads/products/2646610000086023221.jpg"
```

#### Test Images in Consumer App

**Steps:**
1. Go to https://consumer.tsh.sale
2. Browse products
3. Check if product images display (not placeholder icons)
4. Test products with known images:
   - `AKS-YB-BL-3M` (Arabic Keyboard Sticker)
   - `tsh00059y` (RCA Adapter)
   - Any product with image_url in database

**Expected:**
- ✅ Products with images show actual product photos
- ✅ Images load quickly (< 2 seconds)
- ✅ No broken image icons
- ✅ Placeholder icons only for products without images

**Image URL Pattern:**
```
https://erp.tsh.sale/product-images/{zoho_item_id}.jpg
```

#### Test Image Access Directly

```bash
# Test image URL (replace with actual zoho_item_id)
curl -I "https://erp.tsh.sale/product-images/2646610000086023221.jpg"

# Expected: HTTP/1.1 200 OK, Content-Type: image/jpeg
```

**If 404:**
1. Check if symlink exists: `ls -la /home/deploy/TSH_ERP_Ecosystem/uploads/products/{zoho_item_id}.jpg`
2. Run symlink creation: `python3 scripts/create_product_image_symlinks_from_db.py`
3. Verify nginx config has `/product-images/` location

---

## 🔍 COMPREHENSIVE TESTING PROCEDURE

### After Zoho Sync

**Step 1: Verify Data Sync**
```bash
# Check product count
docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp \
  -c "SELECT COUNT(*) FROM products WHERE is_active = true;"

# Check stock data
docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp \
  -c "SELECT COUNT(*) FROM products WHERE actual_available_stock > 0;"

# Check prices
docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp \
  -c "SELECT COUNT(*) FROM product_prices;"
```

**Step 2: Verify Consumer App**
1. Open https://consumer.tsh.sale
2. Check first 20 products:
   - ✅ Stock shows correctly
   - ✅ Prices show correctly
   - ✅ Images display (if available)
3. Test search functionality
4. Test category filters

**Step 3: Verify Admin App**
1. Open https://erp.tsh.sale/admin/products
2. Check product list:
   - ✅ Stock quantities match
   - ✅ Prices match
   - ✅ Images show
3. Test product edit page

**Step 4: Verify API**
```bash
# Test consumer API
curl -s "https://erp.tsh.sale/api/consumer/products?limit=5" | python3 -m json.tool

# Check response includes:
# - stock_quantity
# - price
# - image_url
# - in_stock
```

---

## 🚨 COMMON ISSUES & FIXES

### Issue: Products Show No Stock

**Symptoms:**
- Consumer app shows "غير متوفر" (Unavailable)
- Stock shows 0 for products that have stock in Zoho

**Fix:**
```sql
-- Check if stock data exists
SELECT COUNT(*) FROM products WHERE actual_available_stock IS NULL;

-- If NULL, re-run product sync
python3 run_tds_zoho_sync.py
```

### Issue: Products Show No Prices

**Symptoms:**
- Consumer app shows "0 د.ع" or no price
- Products don't appear in consumer app

**Fix:**
```bash
# Check if product_prices table is empty
docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp \
  -c "SELECT COUNT(*) FROM product_prices;"

# If 0, run migration
./scripts/migrate_consumer_prices.sh
```

### Issue: Images Not Displaying

**Symptoms:**
- Consumer app shows placeholder icons
- Images return 404

**Fix:**
```bash
# 1. Check if images downloaded
ls -1 /home/deploy/TSH_ERP_Ecosystem/uploads/products/*.jpg | wc -l

# 2. Create symlinks
python3 scripts/create_product_image_symlinks_from_db.py

# 3. Verify nginx config
grep -A 5 "location /product-images/" /etc/nginx/sites-available/tsh-unified

# 4. Test image access
curl -I "https://erp.tsh.sale/product-images/{zoho_item_id}.jpg"
```

### Issue: Prices Wrong in Consumer App

**Symptoms:**
- Consumer app shows wrong prices
- Prices don't match Consumer price list

**Fix:**
```sql
-- Check Consumer prices
SELECT p.sku, p.name, pp.price, pl.code
FROM products p
JOIN product_prices pp ON pp.product_id = p.id
JOIN pricing_lists pl ON pp.pricing_list_id = pl.id
WHERE pl.code = 'consumer_iqd'
  AND p.sku = '{problematic_sku}';

-- Re-sync price lists
python3 scripts/sync_pricelists_from_zoho.py
```

---

## 📋 TESTING CHECKLIST TEMPLATE

### Product: {SKU} - {Name}

**Stock:**
- [ ] Database: `actual_available_stock = {value}`
- [ ] Consumer App: Shows "{value} متوفر"
- [ ] Admin App: Shows "{value}" in stock column
- [ ] Matches Zoho Books: ✅ / ❌

**Price:**
- [ ] Database Consumer Price: `{price} IQD`
- [ ] Consumer App: Shows "{price} د.ع"
- [ ] Admin App: Shows "{price}" in price column
- [ ] Matches Zoho Price List: ✅ / ❌

**Image:**
- [ ] Database: `image_url = '/uploads/products/{filename}'`
- [ ] File exists: `/home/deploy/TSH_ERP_Ecosystem/uploads/products/{filename}`
- [ ] Symlink exists: `{zoho_item_id}.jpg -> {filename}`
- [ ] Consumer App: Shows image (not placeholder)
- [ ] Image URL accessible: `https://erp.tsh.sale/product-images/{zoho_item_id}.jpg`
- [ ] HTTP Status: 200 OK

**Notes:**
- Any discrepancies: ___________
- Fixed: ✅ / ❌

---

## 🔄 AUTOMATED VERIFICATION SCRIPT

Create: `scripts/verify_product_data.sh`

```bash
#!/bin/bash
# Automated Product Data Verification

echo "=================================="
echo "Product Data Verification"
echo "=================================="
echo ""

# Check stock
echo "📦 Stock Verification:"
STOCK_COUNT=$(docker compose exec -T tsh_postgres psql -U tsh_admin -d tsh_erp -t -c \
  "SELECT COUNT(*) FROM products WHERE is_active = true AND actual_available_stock > 0;")
echo "  Products with stock: $STOCK_COUNT"

# Check prices
echo ""
echo "💰 Price Verification:"
PRICE_COUNT=$(docker compose exec -T tsh_postgres psql -U tsh_admin -d tsh_erp -t -c \
  "SELECT COUNT(*) FROM product_prices pp JOIN pricing_lists pl ON pp.pricing_list_id = pl.id WHERE pl.code = 'consumer_iqd';")
echo "  Consumer prices: $PRICE_COUNT"

# Check images
echo ""
echo "🖼️  Image Verification:"
IMAGE_COUNT=$(docker compose exec -T tsh_postgres psql -U tsh_admin -d tsh_erp -t -c \
  "SELECT COUNT(*) FROM products WHERE image_url LIKE '/uploads/%';")
echo "  Products with local images: $IMAGE_COUNT"

SYMLINK_COUNT=$(ls -1 /home/deploy/TSH_ERP_Ecosystem/uploads/products/264661*.jpg 2>/dev/null | wc -l)
echo "  Image symlinks: $SYMLINK_COUNT"

# Test API
echo ""
echo "🌐 API Verification:"
API_RESPONSE=$(curl -s "https://erp.tsh.sale/api/consumer/products?limit=1")
if echo "$API_RESPONSE" | grep -q '"count"'; then
    echo "  ✅ Consumer API responding"
else
    echo "  ❌ Consumer API error"
fi

echo ""
echo "=================================="
```

---

## 🎯 CRITICAL TEST PRODUCTS

**Always test these specific products after sync:**

1. **SKU: `tsh00059y`** - ( 2 Female To 1 Male ) RCA Adapter
   - Should have stock: 934
   - Should have Consumer price: 1,500 IQD
   - Should have image

2. **SKU: `AKS-YB-BL-3M`** - Arabic Keyboard Sticker YB-BL 3M
   - Should have stock: 345
   - Should have Consumer price: 5,000 IQD
   - Should have image

3. **SKU: `tsh00057`** - 2 Female RCA TO Male 3.5 Adapter
   - Should have stock: 643
   - Should have Consumer price: 3,000 IQD
   - Should have image

**Test these in:**
- ✅ Consumer App (https://consumer.tsh.sale)
- ✅ Admin App (https://erp.tsh.sale/admin/products)
- ✅ Consumer API (`/api/consumer/products?sku={sku}`)

---

## 📱 APP-SPECIFIC VERIFICATION

### Consumer App (consumer.tsh.sale)

**What to Check:**
- [ ] Products load without errors
- [ ] Stock badges show correctly ("متوفر" / "غير متوفر")
- [ ] Prices display in IQD format
- [ ] Images load (not placeholders)
- [ ] Search works
- [ ] Categories filter correctly
- [ ] Add to cart works

**Test Products:**
- Products with stock > 0
- Products with stock = 0
- Products with images
- Products without images
- Products in different categories

### Admin App (erp.tsh.sale/admin)

**What to Check:**
- [ ] Product list shows all products
- [ ] Stock column matches database
- [ ] Price columns show all price lists
- [ ] Images display in product cards
- [ ] Product edit page shows correct data
- [ ] Stock updates reflect immediately

### Consumer API (erp.tsh.sale/api/consumer/products)

**What to Check:**
```json
{
  "status": "success",
  "count": 1304,
  "items": [
    {
      "id": "3",
      "sku": "tsh00059y",
      "name": "...",
      "price": 1500.0,
      "currency": "IQD",
      "stock_quantity": 934,
      "image_url": "http://erp.tsh.sale/product-images/2646610000066650802.jpg",
      "in_stock": true,
      "has_image": true
    }
  ]
}
```

**Required Fields:**
- ✅ `price` (must be > 0)
- ✅ `stock_quantity` (must match database)
- ✅ `image_url` (must be accessible)
- ✅ `in_stock` (boolean)
- ✅ `has_image` (boolean)

---

## 🔧 QUICK FIXES

### If Stock Wrong:
```bash
# Re-sync products (includes stock)
python3 run_tds_zoho_sync.py
```

### If Prices Missing:
```bash
# Migrate prices
./scripts/migrate_consumer_prices.sh
```

### If Images Missing:
```bash
# Create symlinks
python3 scripts/create_product_image_symlinks_from_db.py

# Or re-download images
python3 download_all_zoho_images.py
```

---

## 📊 VERIFICATION METRICS

**After every sync, verify these metrics:**

| Metric | Expected | Check |
|--------|----------|-------|
| Active Products | 1,300+ | ✅ |
| Products with Stock | 1,200+ | ✅ |
| Consumer Prices | 1,300+ | ✅ |
| Products with Images | 700+ | ✅ |
| Image Symlinks | 700+ | ✅ |
| Consumer API Products | 1,300+ | ✅ |

**If any metric is 0 or significantly lower, investigate immediately!**

---

## 🚨 RED FLAGS - INVESTIGATE IMMEDIATELY

**Stop and fix if you see:**

1. ❌ **Consumer API returns 0 products**
   - Check `product_prices` table
   - Run `migrate_consumer_prices.sh`

2. ❌ **All products show 0 stock**
   - Check `actual_available_stock` column
   - Re-run product sync

3. ❌ **All products show placeholder images**
   - Check image download status
   - Verify symlinks exist
   - Check nginx `/product-images/` location

4. ❌ **Prices show 0 or missing**
   - Check `product_prices` table
   - Verify `pricing_lists` populated
   - Run price migration

5. ❌ **Consumer app shows "Failed to load products"**
   - Check API endpoint
   - Verify database connection
   - Check app logs

---

## 📝 POST-SYNC VERIFICATION WORKFLOW

**After EVERY sync operation:**

1. **Run Verification Script**
   ```bash
   ./scripts/verify_product_data.sh
   ```

2. **Test Consumer App**
   - Open https://consumer.tsh.sale
   - Check 10 random products
   - Verify stock, prices, images

3. **Test Consumer API**
   ```bash
   curl "https://erp.tsh.sale/api/consumer/products?limit=10" | jq '.items[] | {sku, price, stock_quantity, image_url}'
   ```

4. **Test Critical Products**
   - `tsh00059y`
   - `AKS-YB-BL-3M`
   - `tsh00057`

5. **Document Issues**
   - Note any discrepancies
   - Fix immediately
   - Re-verify after fixes

---

## 🎓 BEST PRACTICES

1. **Always verify after sync** - Never assume data is correct
2. **Test in all apps** - Consumer, Admin, API
3. **Test critical products** - Use known test products
4. **Check metrics** - Compare counts with expected values
5. **Document issues** - Keep track of problems and fixes
6. **Automate checks** - Use verification scripts
7. **Fix immediately** - Don't leave issues unfixed

---

## 📚 Related Documentation

- **CONSUMER_APP_TROUBLESHOOTING.md** - Consumer app fixes
- **ZOHO_SYNC_RULES.md** - Zoho sync procedures
- **DEPLOYMENT_SUCCESS_NOV13_2025.md** - Deployment guide

---

**REMEMBER:** Products must show **correct stock**, **correct prices**, and **correct images** in **ALL apps**!

**Last Updated:** November 13, 2025  
**Status:** ✅ ACTIVE  
**Priority:** 🔴 CRITICAL

---

**END OF VERIFICATION GUIDE**

