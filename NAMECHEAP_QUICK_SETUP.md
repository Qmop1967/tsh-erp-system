# 🚀 Namecheap API - Quick Setup Instructions

**Your API Key**: `062e609309e648e7801d7e3f192e2091`

---

## ⚡ Quick Start (5 minutes)

### Step 1: Enable API Access (2 minutes)

1. **Go to Namecheap API Settings**
   - Click here: https://ap.namecheap.com/settings/tools/apiaccess/
   - Or navigate: Profile → Tools → Namecheap API Access

2. **Enable API**
   - Toggle "API Access" to **ON**
   - Accept Terms of Service

3. **Whitelist Production Server IP**
   - Add IP: **`167.71.39.50`**
   - This is your DigitalOcean production server
   - Click "Add" or "Update"

4. **Note Your Username**
   - You'll need your Namecheap username (usually your email or account name)

---

### Step 2: Test API Connection (1 minute)

Run the test script I created:

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
python3 test_namecheap_connection.py
```

**The script will:**
- Ask for your Namecheap username
- Test the API connection
- List all your domains
- Show DNS records for tsh.sale
- Verify everything is working

**Expected output:**
```
✅ API connection successful!
📋 Found X domain(s):
  • tsh.sale
    Expires: ...
    Status: ✅ Auto-Renew

✅ Found X DNS records
  A Records:
    • erp.tsh.sale -> 167.71.39.50
    • www.tsh.sale -> ...

✅ All tests passed!
```

---

### Step 3: Setup Environment Variables (1 minute)

Once the test passes, create your credentials file:

```bash
# Create credentials file
cat > ~/.namecheap_credentials << 'EOF'
export NAMECHEAP_API_USER="YOUR_USERNAME_HERE"
export NAMECHEAP_API_KEY="062e609309e648e7801d7e3f192e2091"
export NAMECHEAP_USERNAME="YOUR_USERNAME_HERE"
export NAMECHEAP_CLIENT_IP="167.71.39.50"
export NAMECHEAP_SANDBOX="false"
EOF

# Secure it
chmod 600 ~/.namecheap_credentials

# Load credentials
source ~/.namecheap_credentials
```

**Replace `YOUR_USERNAME_HERE` with your actual Namecheap username!**

---

### Step 4: Use DNS Management Tools (Anytime)

Once credentials are set up, you can manage DNS:

```bash
# Load credentials first
source ~/.namecheap_credentials

# List all domains
python3 scripts/manage_namecheap_dns.py list

# Get DNS records for tsh.sale
python3 scripts/manage_namecheap_dns.py get-records tsh.sale

# Add a new A record
python3 scripts/manage_namecheap_dns.py add-record tsh.sale A api 167.71.39.50

# Update an existing record
python3 scripts/manage_namecheap_dns.py update-record tsh.sale A erp 167.71.39.50

# Delete a record
python3 scripts/manage_namecheap_dns.py delete-record tsh.sale A old-subdomain
```

---

## 🔐 SSL Certificate Setup (After API is working)

Once API is confirmed working, we'll set up SSL:

```bash
# On production server
ssh root@167.71.39.50

# Install acme.sh (Let's Encrypt client)
curl https://get.acme.sh | sh -s email=khaleel@tsh.sale

# Get SSL certificate using DNS challenge
# This will automatically create DNS TXT records via Namecheap API
~/.acme.sh/acme.sh --issue --dns dns_namecheap \
  -d tsh.sale \
  -d www.tsh.sale \
  -d erp.tsh.sale \
  -d shop.tsh.sale

# Install certificate to Nginx
~/.acme.sh/acme.sh --install-cert -d tsh.sale \
  --key-file /etc/nginx/ssl/tsh.sale.key \
  --fullchain-file /etc/nginx/ssl/tsh.sale.crt \
  --reloadcmd "systemctl reload nginx"
```

---

## ✅ Verification Checklist

Before running the test script, make sure:

- [ ] You've logged into Namecheap
- [ ] API Access is toggled ON
- [ ] IP `167.71.39.50` is whitelisted
- [ ] You know your Namecheap username
- [ ] You've run `python3 test_namecheap_connection.py`

---

## 🆘 Troubleshooting

### Error: "IP address not whitelisted"
- Go to https://ap.namecheap.com/settings/tools/apiaccess/
- Add `167.71.39.50` to the whitelist
- Wait 2-3 minutes for changes to propagate

### Error: "API Key is invalid"
- Verify the API key hasn't been regenerated
- Check that API Access is enabled (toggle ON)

### Error: "Authentication failed"
- Double-check your username
- Username is usually your account email or account name
- Check in Namecheap account profile

---

## 📞 What I Need From You

**To proceed with SSL setup, please provide:**

1. Your **Namecheap username**
   - Usually your email or account name
   - Found in: Namecheap Account Profile

2. **Confirm** that you've:
   - Enabled API Access (toggle ON)
   - Whitelisted IP: `167.71.39.50`

Then run:
```bash
python3 test_namecheap_connection.py
```

**Once the test passes, we can:**
- ✅ Automate DNS management
- ✅ Setup SSL certificates automatically
- ✅ Enable HTTPS for all domains
- ✅ Configure auto-renewal

---

## 📋 Summary

**Your API Key**: `062e609309e648e7801d7e3f192e2091` ✅
**Required IP**: `167.71.39.50` (production server)
**Test Script**: `./test_namecheap_connection.py`
**DNS Script**: `./scripts/manage_namecheap_dns.py`

**Status**: ⏳ Waiting for:
1. API Access to be enabled in Namecheap
2. IP `167.71.39.50` to be whitelisted
3. Your Namecheap username
4. Test script to pass

Once ready, I'll setup SSL certificates automatically! 🔐
