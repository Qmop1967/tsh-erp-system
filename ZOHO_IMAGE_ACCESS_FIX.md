# Zoho Image Access - OAuth Scope Update Required

**Date:** November 5, 2025
**Status:** OAuth scope missing image access permission

---

## 🚀 Quick Start

**Want to fix this quickly?** Run the automated script:

```bash
/Users/khaleelal-mulla/TSH_ERP_Ecosystem/scripts/update_zoho_oauth_tokens.sh
```

Or see: [**OAUTH_UPDATE_QUICKSTART.md**](./OAUTH_UPDATE_QUICKSTART.md) for step-by-step guide.

---

## 🔍 Problem Discovered

The Zoho OAuth token doesn't have permission to access product images via the API.

**Error from Zoho:**
```json
{
  "code": 57,
  "message": "You are not authorized to perform this operation"
}
```

**Affected Endpoint:**
```
GET https://www.zohoapis.com/inventory/v1/items/{item_id}/image?organization_id=748369814
```

---

## ✅ Solution: Update OAuth Scope

You need to update the Zoho OAuth application to include image access permissions.

### Step 1: Go to Zoho API Console

1. Visit: **https://api-console.zoho.com/**
2. Sign in with your Zoho account
3. Go to **"Self Client"** section

### Step 2: Update OAuth Scopes

Current scopes (what you have now):
```
ZohoInventory.FullAccess.all
ZohoBooks.FullAccess.all
```

**Required scopes** (add these):
```
ZohoInventory.FullAccess.all
ZohoBooks.FullAccess.all
ZohoInventory.items.READ
ZohoInventory.settings.READ
```

Or use the broader scope:
```
ZohoInventory.fullaccess.all
```

### Step 3: Regenerate Tokens

After updating scopes, you need to regenerate the OAuth tokens:

**Option A: Using Zoho API Console**
1. In API Console → Self Client
2. Click **"Generate Code"**
3. Select all required scopes
4. Copy the generated code
5. Use it to get new access & refresh tokens

**Option B: Using OAuth Flow**
1. Visit this URL (replace with your client ID):
```
https://accounts.zoho.com/oauth/v2/auth?scope=ZohoInventory.fullaccess.all&client_id=YOUR_CLIENT_ID&response_type=code&access_type=offline&redirect_uri=YOUR_REDIRECT_URI
```

2. Authorize the application
3. Get the authorization code from redirect
4. Exchange code for tokens:
```bash
curl -X POST "https://accounts.zoho.com/oauth/v2/token" \
  -d "code=YOUR_AUTH_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=YOUR_REDIRECT_URI" \
  -d "grant_type=authorization_code"
```

### Step 4: Update Environment Variables

Update the tokens in your `.env` file on the VPS:

```bash
# SSH to VPS
ssh root@167.71.39.50

# Edit .env file
cd /home/deploy/TSH_ERP_Ecosystem
nano app/.env

# Update these values:
ZOHO_ACCESS_TOKEN=your_new_access_token
ZOHO_REFRESH_TOKEN=your_new_refresh_token

# Save and exit (Ctrl+X, Y, Enter)

# Restart service
systemctl restart tsh-erp
```

### Step 5: Test Image Access

After updating tokens, test if images work:

```bash
# Test image endpoint
curl "https://erp.tsh.sale/api/zoho/image/2646610000000114330"

# Should return JPEG image data, not JSON error
```

---

## 🔧 Alternative Solution (If OAuth Update Fails)

If you can't update the OAuth scope, here's how to upload images manually:

### Option 1: Upload to Server

1. **Download images from Zoho manually**
2. **Upload to VPS:**
```bash
# Create images directory
ssh root@167.71.39.50 "mkdir -p /var/www/product-images"

# Upload images
scp product-images/* root@167.71.39.50:/var/www/product-images/

# Set permissions
ssh root@167.71.39.50 "chmod -R 755 /var/www/product-images"
```

3. **Configure Nginx to serve images:**
```nginx
# Add to nginx config
location /product-images/ {
    alias /var/www/product-images/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

4. **Update database with new URLs:**
```sql
UPDATE products
SET image_url = 'https://erp.tsh.sale/product-images/' || sku || '.jpg'
WHERE zoho_item_id = 'ITEM_ID';
```

### Option 2: Use Cloud Storage (S3/Cloudflare R2)

1. Upload images to cloud storage
2. Get public URLs
3. Update database with cloud URLs
4. Faster global delivery via CDN

---

## 📊 Current Status

**Temporary Fix Applied:**
- Consumer API returns placeholder images
- App still works, just without product photos
- No errors, clean user experience

**Placeholder URL:**
```
https://erp.tsh.sale/static/placeholder-product.png
```

**When OAuth is Fixed:**
- Simply update tokens
- Restart service
- Images will automatically load via proxy
- No code changes needed

---

## 🎯 Recommended Action

**Best Solution:** Update Zoho OAuth scope and regenerate tokens (15 minutes)

This will:
- ✅ Enable automatic image access
- ✅ No manual uploads needed
- ✅ Images stay synced with Zoho
- ✅ Professional solution
- ✅ Scalable for thousands of products

**Alternative:** Manual image upload (if OAuth not possible)

---

## 📞 Need Help?

If you need assistance with:
1. **Zoho OAuth configuration** - I can guide you step-by-step
2. **Token regeneration** - I can provide exact API calls
3. **Manual image upload** - I can create automated scripts

Let me know which approach you prefer!

---

**Summary:**
- Problem: OAuth scope doesn't include image access
- Solution: Add `ZohoInventory.fullaccess.all` scope
- Action: Regenerate tokens with updated scope
- Result: Images will work automatically
