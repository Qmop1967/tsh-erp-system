# Update Zoho OAuth - Step by Step Guide

**Date:** November 5, 2025
**Status:** Ready to update OAuth scope for image access

---

## 📋 Your OAuth Credentials

- **Client ID:** `1000.SLY5X93N58VN46HXQIIZSOQKG8J3ZJ`
- **Client Secret:** `0581c245cd951e1453042ff2bcf223768e128fed9f`
- **Redirect URI:** `https://www.zoho.com`

---

## 🚀 Step 1: Get Authorization Code

**Click this link to authorize with the correct scope:**

```
https://accounts.zoho.com/oauth/v2/auth?scope=ZohoInventory.fullaccess.all,ZohoBooks.fullaccess.all&client_id=1000.SLY5X93N58VN46HXQIIZSOQKG8J3ZJ&response_type=code&access_type=offline&redirect_uri=https://www.zoho.com&prompt=consent
```

**What will happen:**
1. You'll be redirected to Zoho login (if not already logged in)
2. You'll see a consent screen asking for permissions
3. Click "Accept" to grant permissions
4. You'll be redirected to `https://www.zoho.com/?code=XXXXX`
5. **Copy the code from the URL** (the part after `code=`)

**Important:** The authorization code expires in **60 seconds**, so copy it immediately!

---

## 🔑 Step 2: Exchange Code for Tokens

Once you have the authorization code, run this command in Terminal:

```bash
# Replace YOUR_AUTH_CODE_HERE with the code you copied
AUTH_CODE="YOUR_AUTH_CODE_HERE"

curl -X POST "https://accounts.zoho.com/oauth/v2/token" \
  -d "code=$AUTH_CODE" \
  -d "client_id=1000.SLY5X93N58VN46HXQIIZSOQKG8J3ZJ" \
  -d "client_secret=0581c245cd951e1453042ff2bcf223768e128fed9f" \
  -d "redirect_uri=https://www.zoho.com" \
  -d "grant_type=authorization_code"
```

**Expected Response:**
```json
{
  "access_token": "1000.xxxxx",
  "refresh_token": "1000.yyyyy",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

**Copy both tokens** (access_token and refresh_token) - you'll need them in the next step.

---

## 📝 Step 3: Update .env File on VPS

Run this command to update the tokens on your server:

```bash
# Replace with your actual tokens from Step 2
ACCESS_TOKEN="1000.xxxxx"
REFRESH_TOKEN="1000.yyyyy"

# Update .env file
ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && \
  sed -i 's/^ZOHO_ACCESS_TOKEN=.*/ZOHO_ACCESS_TOKEN=\"$ACCESS_TOKEN\"/' app/.env && \
  sed -i 's/^ZOHO_REFRESH_TOKEN=.*/ZOHO_REFRESH_TOKEN=\"$REFRESH_TOKEN\"/' app/.env && \
  cat app/.env | grep ZOHO_"
```

**Or update manually:**
```bash
ssh root@167.71.39.50
cd /home/deploy/TSH_ERP_Ecosystem
nano app/.env

# Update these lines:
ZOHO_ACCESS_TOKEN="1000.xxxxx"
ZOHO_REFRESH_TOKEN="1000.yyyyy"

# Save: Ctrl+X, Y, Enter
```

---

## 🔄 Step 4: Restart Service

```bash
ssh root@167.71.39.50 "systemctl restart tsh-erp && systemctl status tsh-erp --no-pager"
```

---

## ✅ Step 5: Test Image Access

```bash
# Test if images now work
curl -I "https://erp.tsh.sale/api/zoho/image/2646610000000114330"

# Should return: HTTP/2 200 OK
# Instead of: {"code":57,"message":"You are not authorized..."}
```

---

## 📥 Step 6: Download All Product Images

Once OAuth is working, download all images:

```bash
ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && \
  source venv/bin/activate && \
  python3 scripts/download_zoho_images.py"
```

This will download all 1,309 product images to `/var/www/product-images/`

---

## 🧪 Step 7: Clear Flutter Cache & Test

Visit this URL on your phone/device:
```
https://consumer.tsh.sale/force-reload.html?auto=1
```

Then visit:
```
https://consumer.tsh.sale
```

You should now see product images! ✅

---

## 🆘 Troubleshooting

### Issue: "Invalid authorization code"
**Solution:** The code expired (60 seconds). Go back to Step 1 and get a new code.

### Issue: "Invalid client credentials"
**Solution:** Double-check your Client ID and Client Secret in the curl command.

### Issue: Still getting HTTP 401 on images
**Solution:**
1. Verify the tokens were updated: `ssh root@167.71.39.50 "cat /home/deploy/TSH_ERP_Ecosystem/app/.env | grep ZOHO_REFRESH"`
2. Restart the service: `ssh root@167.71.39.50 "systemctl restart tsh-erp"`
3. Check logs: `ssh root@167.71.39.50 "journalctl -u tsh-erp -n 50"`

### Issue: Images still not showing in app
**Solution:** Clear Flutter cache again:
1. Visit https://consumer.tsh.sale/force-reload.html?auto=1
2. Hard refresh (Cmd+Shift+R)
3. Close and reopen the app

---

## ⏱️ Estimated Time: 10-15 minutes

1. Get authorization code: **1 minute**
2. Exchange for tokens: **30 seconds**
3. Update .env file: **2 minutes**
4. Restart service: **30 seconds**
5. Download images: **5-10 minutes** (depending on network speed)
6. Clear cache & test: **2 minutes**

---

## 📞 Need Help?

If you encounter any issues, share the error message and I'll help you troubleshoot.

**Quick test commands:**
```bash
# Check service status
ssh root@167.71.39.50 "systemctl status tsh-erp --no-pager"

# Check recent logs
ssh root@167.71.39.50 "journalctl -u tsh-erp -n 50 --no-pager"

# Test API
curl -s "https://erp.tsh.sale/api/consumer/products?limit=1" | grep image_url
```

---

**Ready to start? Click the authorization URL in Step 1!**
