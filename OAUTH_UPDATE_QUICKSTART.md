# Zoho OAuth Update - Quick Start Guide

**Goal**: Fix product images in consumer app by updating Zoho OAuth scope

**Time Required**: 10-15 minutes

---

## 🚀 Quick Method: Use Automated Script

Run this command in Terminal:

```bash
/Users/khaleelal-mulla/TSH_ERP_Ecosystem/scripts/update_zoho_oauth_tokens.sh
```

The script will:
1. ✅ Read your current OAuth configuration
2. ✅ Generate the authorization URL for you
3. ✅ Exchange authorization code for new tokens
4. ✅ Update the .env file on VPS
5. ✅ Restart the service
6. ✅ Test image access

Just follow the prompts!

---

## 📋 Manual Method: Step-by-Step

### Step 1: Update OAuth Scope in Zoho Console

1. **Visit**: https://api-console.zoho.com/
2. **Sign in** with your Zoho account
3. **Go to**: Self Client section
4. **Click**: "Update" or "Edit Scopes"
5. **Add these scopes**:
   ```
   ZohoInventory.fullaccess.all
   ZohoBooks.fullaccess.all
   ```
6. **Save** the changes

### Step 2: Get New Authorization Code

The script will generate an authorization URL for you, or you can construct it manually:

```
https://accounts.zoho.com/oauth/v2/auth?scope=ZohoInventory.fullaccess.all,ZohoBooks.fullaccess.all&client_id=YOUR_CLIENT_ID&response_type=code&access_type=offline&redirect_uri=YOUR_REDIRECT_URI
```

1. **Open** the URL in your browser
2. **Authorize** the application
3. **Copy** the authorization code from the redirect URL

### Step 3: Exchange Code for Tokens

Use the script, or manually run:

```bash
curl -X POST "https://accounts.zoho.com/oauth/v2/token" \
  -d "code=YOUR_AUTH_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=YOUR_REDIRECT_URI" \
  -d "grant_type=authorization_code"
```

### Step 4: Update .env File

```bash
ssh root@167.71.39.50

cd /home/deploy/TSH_ERP_Ecosystem/app

# Backup current .env
cp .env .env.backup

# Edit .env
nano .env

# Update these lines:
ZOHO_ACCESS_TOKEN=your_new_access_token
ZOHO_REFRESH_TOKEN=your_new_refresh_token

# Save (Ctrl+X, Y, Enter)
```

### Step 5: Restart Service

```bash
systemctl restart tsh-erp
systemctl status tsh-erp
```

### Step 6: Test Image Access

```bash
curl -I "https://erp.tsh.sale/api/zoho/image/2646610000000114330"
```

Should return:
```
HTTP/2 200
content-type: image/jpeg
```

---

## ✅ Verification Steps

### Test 1: Image Proxy Endpoint

Visit: https://erp.tsh.sale/api/zoho/image/2646610000000114330

✅ **Success**: Image displays
❌ **Failure**: JSON error or blank

### Test 2: Consumer API

Visit: https://erp.tsh.sale/api/consumer/products?limit=1

✅ **Success**: `image_url` contains `/api/zoho/image/...`
❌ **Failure**: `image_url` contains `placeholder-product.png`

### Test 3: Consumer App

1. **Clear cache**: https://consumer.tsh.sale/clear-cache.html
2. **Visit app**: https://consumer.tsh.sale
3. **Check**: Product images should load

---

## 🔧 Troubleshooting

### Problem: "Authorization code expired"
**Solution**: Get a new authorization code (they expire in ~60 seconds)

### Problem: "Invalid client credentials"
**Solution**: Verify CLIENT_ID and CLIENT_SECRET in .env file

### Problem: "Redirect URI mismatch"
**Solution**: Ensure REDIRECT_URI in request matches Zoho Console configuration

### Problem: Images still not loading in app
**Solution**:
1. Clear Flutter cache: https://consumer.tsh.sale/clear-cache.html
2. Hard refresh browser (Cmd+Shift+R)
3. Check browser console for errors

### Problem: Service won't restart
**Solution**:
```bash
ssh root@167.71.39.50
journalctl -u tsh-erp -n 50 --no-pager
# Check for errors
```

---

## 📊 Current Status Check

Before starting, verify current status:

```bash
# Check if service is running
ssh root@167.71.39.50 'systemctl status tsh-erp --no-pager | head -10'

# Check current OAuth tokens
ssh root@167.71.39.50 'cd /home/deploy/TSH_ERP_Ecosystem && grep -E "ZOHO_(ACCESS|REFRESH)_TOKEN" app/.env | head -c 100'

# Test current image access
curl -s "https://erp.tsh.sale/api/zoho/image/2646610000000114330" | head -c 100
```

---

## 🎯 Expected Results

**Before OAuth Update**:
- ❌ Image endpoint returns: `{"code":57,"message":"You are not authorized to perform this operation"}`
- ❌ Consumer app shows placeholder icons
- ❌ API returns: `https://erp.tsh.sale/static/placeholder-product.png`

**After OAuth Update**:
- ✅ Image endpoint returns: JPEG image data
- ✅ Consumer app shows actual product photos
- ✅ API returns: `https://erp.tsh.sale/api/zoho/image/{item_id}`

---

## 📞 Need Help?

If you encounter issues:

1. **Check service logs**:
   ```bash
   ssh root@167.71.39.50 'journalctl -u tsh-erp -n 50 --no-pager'
   ```

2. **Test image endpoint manually**:
   ```bash
   curl -v "https://erp.tsh.sale/api/zoho/image/2646610000000114330"
   ```

3. **Verify OAuth scope**:
   - Go to Zoho API Console
   - Check Self Client → Scopes
   - Should include `ZohoInventory.fullaccess.all`

---

## 📁 Related Documentation

- **Detailed fix guide**: `ZOHO_IMAGE_ACCESS_FIX.md`
- **Update script**: `scripts/update_zoho_oauth_tokens.sh`
- **Consumer API code**: `app/routers/consumer_api.py:124-136`
- **Image proxy code**: `app/routers/zoho_proxy.py:20-86`

---

## ⏱️ Estimated Timeline

- **OAuth scope update in Zoho Console**: 2 minutes
- **Get authorization code**: 1 minute
- **Exchange code for tokens**: 30 seconds
- **Update .env and restart service**: 2 minutes
- **Testing and verification**: 5 minutes

**Total**: ~10-15 minutes

---

**Ready to start?**

Run the automated script:
```bash
/Users/khaleelal-mulla/TSH_ERP_Ecosystem/scripts/update_zoho_oauth_tokens.sh
```

Or follow the manual steps above.
