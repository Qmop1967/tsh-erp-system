# Namecheap API Setup Guide

## Overview
This guide will help you set up Namecheap API access to manage DNS records and SSL certificates for your domains.

---

## Step 1: Enable API Access in Namecheap

1. **Login to Namecheap**
   - Go to: https://www.namecheap.com/
   - Login with your account credentials

2. **Enable API Access**
   - Go to your account profile
   - Navigate to: **Profile → Tools → Namecheap API Access**
   - Or directly: https://ap.namecheap.com/settings/tools/apiaccess/

3. **Enable API**
   - Toggle "API Access" to **ON**
   - Read and accept the Terms of Service

4. **Whitelist Your IPs**
   You need to whitelist these IP addresses:
   - **Local Machine**: Your current public IP (for local testing)
   - **Production Server**: `167.71.39.50` (for automated operations)

   To find your current IP:
   ```bash
   curl ifconfig.me
   ```

   Add both IPs to the whitelist in Namecheap API settings.

5. **Get Your API Key**
   - Once API is enabled, you'll see your **API Key**
   - Copy and save it securely (you'll need it in Step 2)

---

## Step 2: Set Up Environment Variables

### On Your Local Machine

Create a file `~/.namecheap_credentials`:

```bash
cat > ~/.namecheap_credentials << 'EOF'
export NAMECHEAP_API_USER="your_username"
export NAMECHEAP_API_KEY="your_api_key_here"
export NAMECHEAP_USERNAME="your_username"
export NAMECHEAP_CLIENT_IP="your_local_ip"
export NAMECHEAP_SANDBOX="false"
EOF

# Secure the file
chmod 600 ~/.namecheap_credentials

# Load credentials
source ~/.namecheap_credentials
```

### On Production Server

```bash
ssh root@167.71.39.50

cat > /opt/tsh_erp/shared/env/namecheap.env << 'EOF'
export NAMECHEAP_API_USER="your_username"
export NAMECHEAP_API_KEY="your_api_key_here"
export NAMECHEAP_USERNAME="your_username"
export NAMECHEAP_CLIENT_IP="167.71.39.50"
export NAMECHEAP_SANDBOX="false"
EOF

# Secure the file
chmod 600 /opt/tsh_erp/shared/env/namecheap.env

# Load credentials
source /opt/tsh_erp/shared/env/namecheap.env
```

---

## Step 3: Verify API Access

### Using Python Script

Create a test script:

```python
#!/usr/bin/env python3
import os
from namecheap import NamecheapClient

# Load credentials from environment
api_user = os.getenv('NAMECHEAP_API_USER')
api_key = os.getenv('NAMECHEAP_API_KEY')
username = os.getenv('NAMECHEAP_USERNAME')
client_ip = os.getenv('NAMECHEAP_CLIENT_IP')
sandbox = os.getenv('NAMECHEAP_SANDBOX', 'false').lower() == 'true'

# Create client
client = NamecheapClient(
    api_user=api_user,
    api_key=api_key,
    username=username,
    client_ip=client_ip,
    sandbox=sandbox
)

# Test API connection
print("Testing Namecheap API connection...")
try:
    # Get list of domains
    result = client.domains_getList()
    print(f"✅ API connection successful!")
    print(f"📋 You have {len(result)} domain(s) in your account")
    for domain in result:
        print(f"   - {domain['Name']}")
except Exception as e:
    print(f"❌ API connection failed: {e}")
```

Save as `test_namecheap_api.py` and run:

```bash
source ~/.namecheap_credentials
python3 test_namecheap_api.py
```

---

## Step 4: DNS Management Examples

### List DNS Records

```python
from namecheap import NamecheapClient
import os

client = NamecheapClient(
    api_user=os.getenv('NAMECHEAP_API_USER'),
    api_key=os.getenv('NAMECHEAP_API_KEY'),
    username=os.getenv('NAMECHEAP_USERNAME'),
    client_ip=os.getenv('NAMECHEAP_CLIENT_IP'),
    sandbox=False
)

# Get DNS records for tsh.sale
records = client.domains_dns_getHosts(sld='tsh', tld='sale')
for record in records:
    print(f"{record['Type']}: {record['Name']}.tsh.sale -> {record['Address']}")
```

### Add/Update DNS Record

```python
# Add an A record for erp.tsh.sale pointing to 167.71.39.50
client.domains_dns_setHosts(
    sld='tsh',
    tld='sale',
    host_records=[
        {
            'HostName': 'erp',
            'RecordType': 'A',
            'Address': '167.71.39.50',
            'TTL': 300
        }
    ]
)
```

---

## Step 5: SSL Certificate Management

### Using Let's Encrypt with DNS Challenge

Once API is configured, you can use DNS challenge for SSL:

```bash
# On production server
ssh root@167.71.39.50

# Source Namecheap credentials
source /opt/tsh_erp/shared/env/namecheap.env

# Install certbot with DNS plugin
pip3 install certbot-dns-namecheap

# Get certificate using DNS challenge
certbot certonly \
  --dns-namecheap \
  --dns-namecheap-credentials /opt/tsh_erp/shared/env/namecheap.env \
  -d erp.tsh.sale \
  -d tsh.sale \
  -d www.tsh.sale
```

---

## Automated DNS Management Script

I've created a DNS management script for you:

```bash
# Location: scripts/manage_namecheap_dns.py
python3 scripts/manage_namecheap_dns.py --help
```

**Available commands**:
- `list` - List all domains
- `get-records <domain>` - Get DNS records for a domain
- `add-record <domain> <type> <host> <value>` - Add DNS record
- `update-record <domain> <type> <host> <value>` - Update DNS record
- `delete-record <domain> <type> <host>` - Delete DNS record

---

## Security Best Practices

1. **Keep API Key Secret**
   - Never commit API key to Git
   - Store in environment variables or secure vaults
   - Rotate API key periodically

2. **Whitelist Only Required IPs**
   - Only whitelist IPs that need API access
   - Update whitelist when IPs change
   - Remove old IPs

3. **Use Sandbox for Testing**
   - Set `NAMECHEAP_SANDBOX=true` for development
   - Test changes before applying to production

4. **Monitor API Usage**
   - Check Namecheap API logs regularly
   - Set up alerts for unusual activity

---

## Troubleshooting

### Error: "API Key is invalid or API access has not been enabled"
- Check that API access is enabled in Namecheap
- Verify API key is correct
- Ensure your IP is whitelisted

### Error: "IP address not whitelisted"
- Add your current IP to the whitelist
- Wait a few minutes after adding IP
- Check that you're using the correct IP

### Error: "Authentication failed"
- Verify username and API user match
- Check that credentials are loaded correctly
- Try regenerating API key

---

## Quick Reference

### Namecheap API Dashboard
https://ap.namecheap.com/settings/tools/apiaccess/

### API Documentation
https://www.namecheap.com/support/api/intro/

### Your Credentials Location
- **Local**: `~/.namecheap_credentials`
- **Production**: `/opt/tsh_erp/shared/env/namecheap.env`

### Load Credentials
```bash
# Local
source ~/.namecheap_credentials

# Production
ssh root@167.71.39.50
source /opt/tsh_erp/shared/env/namecheap.env
```

---

## Next Steps

1. ✅ Enable API access in Namecheap
2. ✅ Whitelist IPs (local + 167.71.39.50)
3. ✅ Get API key
4. ✅ Set up environment variables
5. ✅ Test API connection
6. ✅ Use DNS management scripts
7. ✅ Set up SSL certificates

**Once you provide the API credentials, I can:**
- Verify DNS configuration
- Manage DNS records automatically
- Set up SSL certificates with DNS challenge
- Automate DNS updates in deployment pipeline

---

**Status**: ⏳ Waiting for Namecheap API credentials
**Action Required**: Enable API and provide credentials
