# Product Images Solution for TSH ERP Consumer App

**Date:** November 7, 2025
**Issue:** Products in consumer app have no images
**Status:** ✅ Temporary solution implemented, Permanent solution documented

---

## Problem Analysis

### Root Cause
Zoho Books API does **NOT** provide direct public image URLs. Instead, it provides:
- `image_name`: Filename (e.g., "2021-05-03 12:45:39 +0000.jpg")
- `image_type`: File type (e.g., "jpg", "png")
- `documents`: Array with `document_id` for each attached file

**Why this is a problem:**
- Zoho image URLs require OAuth authentication tokens
- Tokens expire every hour
- Consumer app cannot directly display Zoho-hosted images
- 1,621 products out of 2,219 total have images in Zoho

---

## Current Status

### Database State (November 7, 2025)
| Metric | Count |
|--------|-------|
| **Total Products** | 2,219 |
| **Active with Stock** | 472 |
| **Products with Images in Zoho** | 1,621 |
| **Products with Image URLs in DB** | 450 |
| **Products without any images** | 22 |

### Temporary Solution Implemented
✅ Added placeholder images using `via.placeholder.com`:
```sql
UPDATE products
SET image_url = 'https://via.placeholder.com/300x300.png?text=' || SUBSTRING(name, 1, 20)
WHERE image_name IS NOT NULL AND image_url IS NULL;
```

**Result:** 450 active products now display placeholder images in the consumer app.

---

## Permanent Solutions

### Option 1: Download and Self-Host Images (RECOMMENDED)

**Approach:**
1. Download all product images from Zoho Books
2. Store them in `/var/www/tsh_erp/static/product_images/`
3. Serve them through Nginx at `https://erp.tsh.sale/static/product_images/`
4. Update database with local URLs

**Advantages:**
✅ Full control over images
✅ No external dependencies
✅ Fast loading (local server)
✅ Works offline
✅ No authentication required

**Implementation Steps:**
1. Create image download script (see below)
2. Set up Nginx static file serving
3. Run migration to update image URLs
4. Set up cron job for daily image sync

**Script Location:** `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/download_zoho_images.py`

---

### Option 2: Create Image Proxy API

**Approach:**
Create FastAPI endpoint: `/api/product-image/{product_id}`
This endpoint fetches images from Zoho on-demand and caches them.

**Advantages:**
✅ Automatic authentication handling
✅ On-demand loading
✅ Built-in caching

**Disadvantages:**
❌ Slower first load
❌ Depends on Zoho API availability
❌ Additional server load

---

### Option 3: Use CDN (CloudFlare/AWS S3)

**Approach:**
1. Download images from Zoho
2. Upload to CloudFlare R2 or AWS S3
3. Update database with CDN URLs

**Advantages:**
✅ Global CDN performance
✅ Unlimited storage
✅ Professional solution

**Disadvantages:**
❌ Monthly costs ($5-20/month)
❌ External dependency
❌ Requires setup and credentials

---

## Recommended Implementation Plan

### Phase 1: Self-Hosted Images (Immediate - 2 hours)

1. **Create download script:**
```bash
cd /root/
python3 download_zoho_images.py
```

2. **Configure Nginx:**
```nginx
location /static/product_images/ {
    alias /var/www/tsh_erp/static/product_images/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

3. **Update database:**
```sql
UPDATE products
SET image_url = 'https://erp.tsh.sale/static/product_images/' || image_name
WHERE image_name IS NOT NULL;
```

4. **Set up daily sync:**
```bash
# Crontab entry
0 2 * * * cd /root && python3 download_zoho_images.py >> /var/log/zoho_images.log 2>&1
```

### Phase 2: Optimize (Future)
- Implement image compression
- Generate thumbnails for mobile
- Set up WebP conversion for better performance
- Add image upload feature for products

---

## Files Created

1. **fetch_zoho_product_images.py** - Fetches image metadata from Zoho
2. **download_zoho_images.py** - Downloads actual image files (to be created)
3. **PRODUCT_IMAGES_SOLUTION.md** - This documentation

---

## Database Schema Updates

### Columns Added to `products` Table:
```sql
ALTER TABLE products
ADD COLUMN IF NOT EXISTS image_name VARCHAR(500),
ADD COLUMN IF NOT EXISTS image_type VARCHAR(50);
```

### Current Schema:
- `image_url`: Full URL to the image (currently placeholder or empty)
- `image_name`: Original filename from Zoho
- `image_type`: File extension (jpg, png, etc.)

---

## Next Steps

1. ✅ Add placeholder images (DONE)
2. ✅ Document the issue (DONE - this file)
3. ⏳ Create image download script
4. ⏳ Set up Nginx static serving
5. ⏳ Download all 1,621 images
6. ⏳ Update database with local URLs
7. ⏳ Test in consumer app
8. ⏳ Set up automated daily sync

---

## Technical Notes

### Zoho Books Image API Endpoints:
```
# Get item with documents
GET https://www.zohoapis.com/books/v3/items/{item_id}?organization_id={org_id}

# Download document
GET https://www.zohoapis.com/books/v3/items/{item_id}/documents/{document_id}?organization_id={org_id}
```

### Authentication:
- Uses OAuth 2.0 refresh token
- Token expires every 3600 seconds (1 hour)
- Refresh token: `1000.456d43e0209a40ba2d580747be746a54.1aa75b48b965e8a8562dc89d2a15e517`

---

**Status Update:** Consumer app now shows placeholder images for 450/472 products. Real images will be downloaded and hosted in Phase 2.
