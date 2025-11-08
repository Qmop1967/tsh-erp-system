# SSL Certificate Setup for Docker Nginx

This guide covers SSL certificate setup for the TSH ERP Docker deployment with Nginx reverse proxy.

## Overview

The Docker Nginx service expects SSL certificates to be placed in `nginx/ssl/` directory:
- `nginx/ssl/fullchain.pem` - Full certificate chain
- `nginx/ssl/privkey.pem` - Private key

## Prerequisites

- Domain name pointing to your server (e.g., erp.tsh.sale)
- Ports 80 and 443 accessible from the internet
- Docker and Docker Compose installed

---

## Option 1: Let's Encrypt (Recommended for Production)

Let's Encrypt provides free, automated SSL certificates that auto-renew.

### Method 1A: Using Certbot Standalone

```bash
# 1. Stop nginx if running
docker compose --profile proxy stop nginx

# 2. Install certbot
sudo apt-get update
sudo apt-get install -y certbot

# 3. Obtain certificate
sudo certbot certonly --standalone \
  -d erp.tsh.sale \
  -d www.erp.tsh.sale \
  --agree-tos \
  --email admin@tsh.sale \
  --non-interactive

# 4. Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/erp.tsh.sale/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/erp.tsh.sale/privkey.pem nginx/ssl/

# 5. Set proper permissions
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem
sudo chown $(whoami):$(whoami) nginx/ssl/*.pem

# 6. Start nginx
docker compose --profile proxy up -d nginx
```

### Method 1B: Using Certbot with Docker Nginx Running

```bash
# 1. Ensure nginx is running with HTTP (port 80) accessible
docker compose --profile proxy up -d nginx

# 2. Install certbot with nginx plugin
sudo apt-get install -y certbot python3-certbot-nginx

# 3. Obtain certificate (certbot will temporarily modify nginx config)
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d erp.tsh.sale \
  -d www.erp.tsh.sale \
  --agree-tos \
  --email admin@tsh.sale \
  --non-interactive

# 4. Copy certificates
sudo cp /etc/letsencrypt/live/erp.tsh.sale/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/erp.tsh.sale/privkey.pem nginx/ssl/

# 5. Set permissions
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem
sudo chown $(whoami):$(whoami) nginx/ssl/*.pem

# 6. Reload nginx
docker compose --profile proxy restart nginx
```

### Auto-Renewal Setup

Let's Encrypt certificates expire after 90 days. Set up auto-renewal:

```bash
# Create renewal script
cat > /usr/local/bin/renew-tsh-certs.sh << 'EOF'
#!/bin/bash
set -e

# Renew certificates
certbot renew --quiet

# Copy to nginx directory
cp /etc/letsencrypt/live/erp.tsh.sale/fullchain.pem /path/to/TSH_ERP_Ecosystem/nginx/ssl/
cp /etc/letsencrypt/live/erp.tsh.sale/privkey.pem /path/to/TSH_ERP_Ecosystem/nginx/ssl/

# Set permissions
chmod 644 /path/to/TSH_ERP_Ecosystem/nginx/ssl/fullchain.pem
chmod 600 /path/to/TSH_ERP_Ecosystem/nginx/ssl/privkey.pem

# Reload nginx
cd /path/to/TSH_ERP_Ecosystem
docker compose --profile proxy restart nginx

echo "SSL certificates renewed and nginx reloaded"
EOF

# Make executable
chmod +x /usr/local/bin/renew-tsh-certs.sh

# Add to crontab (runs daily, certbot only renews if needed)
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/renew-tsh-certs.sh >> /var/log/certbot-renewal.log 2>&1") | crontab -
```

---

## Option 2: Self-Signed Certificate (Development/Testing Only)

⚠️ **NOT recommended for production** - browsers will show security warnings.

```bash
# 1. Create nginx/ssl directory if it doesn't exist
mkdir -p nginx/ssl

# 2. Generate self-signed certificate (valid for 365 days)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=IQ/ST=Baghdad/L=Baghdad/O=TSH/OU=IT/CN=erp.tsh.sale"

# 3. Set permissions
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem

# 4. Start nginx
docker compose --profile proxy up -d nginx
```

---

## Option 3: Commercial SSL Certificate

If you purchased an SSL certificate from a provider:

```bash
# 1. Create nginx/ssl directory
mkdir -p nginx/ssl

# 2. Copy your certificate files
# - Copy certificate + intermediate certificates to fullchain.pem
# - Copy private key to privkey.pem

# If you have separate files:
cat your_certificate.crt intermediate.crt > nginx/ssl/fullchain.pem
cp your_private.key nginx/ssl/privkey.pem

# 3. Set permissions
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem

# 4. Start nginx
docker compose --profile proxy up -d nginx
```

---

## Verification

After setting up SSL certificates:

```bash
# 1. Check certificate files exist
ls -lh nginx/ssl/

# Should show:
# -rw-r--r-- 1 user user 3.5K fullchain.pem
# -rw------- 1 user user 1.7K privkey.pem

# 2. Test nginx configuration
docker compose --profile proxy config

# 3. Check nginx logs
docker compose --profile proxy logs nginx

# 4. Test HTTPS endpoint
curl -I https://erp.tsh.sale/health

# 5. Check certificate details
openssl s_client -connect erp.tsh.sale:443 -servername erp.tsh.sale < /dev/null 2>/dev/null | openssl x509 -noout -dates

# 6. Test SSL grade (optional)
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=erp.tsh.sale
```

---

## Troubleshooting

### Nginx Won't Start - Certificate Not Found

```bash
# Check if files exist
ls -lh nginx/ssl/

# If missing, certificates weren't copied correctly
# Verify certbot generated certificates:
sudo ls -lh /etc/letsencrypt/live/erp.tsh.sale/

# Copy again:
sudo cp /etc/letsencrypt/live/erp.tsh.sale/*.pem nginx/ssl/
sudo chown $(whoami):$(whoami) nginx/ssl/*.pem
```

### Permission Denied Errors

```bash
# Fix permissions
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem
sudo chown $(whoami):$(whoami) nginx/ssl/*.pem
```

### Certificate Expired

```bash
# Manually renew
sudo certbot renew

# Copy new certificates
sudo cp /etc/letsencrypt/live/erp.tsh.sale/*.pem nginx/ssl/

# Restart nginx
docker compose --profile proxy restart nginx
```

### Browser Shows "Connection Not Secure"

- Verify certificate is valid and not expired
- Check that domain name matches certificate CN
- For self-signed certs, this is expected (use Let's Encrypt for production)

---

## Security Best Practices

1. **Never commit SSL certificates to git**
   - Already excluded in `.gitignore`
   - Keep `nginx/ssl/` directory empty in repository

2. **Restrict private key permissions**
   ```bash
   chmod 600 nginx/ssl/privkey.pem
   ```

3. **Use strong TLS protocols**
   - Already configured in `nginx.conf`: TLSv1.2 and TLSv1.3 only

4. **Enable HSTS**
   - Already configured in `nginx.conf`

5. **Monitor certificate expiration**
   - Set up renewal cron job (see above)
   - Monitor logs: `/var/log/certbot-renewal.log`

---

## Production Checklist

- [ ] Domain DNS points to server IP
- [ ] Ports 80 and 443 are open and accessible
- [ ] Let's Encrypt certificate obtained
- [ ] Certificates copied to `nginx/ssl/`
- [ ] Permissions set correctly (644 for cert, 600 for key)
- [ ] Auto-renewal cron job configured
- [ ] HTTPS test successful (`curl https://erp.tsh.sale/health`)
- [ ] SSL Labs test shows A+ rating
- [ ] Certificate expiration monitoring in place

---

## Quick Reference

```bash
# Generate self-signed cert (dev only)
./scripts/generate_self_signed_cert.sh

# Obtain Let's Encrypt cert
sudo certbot certonly --standalone -d erp.tsh.sale

# Copy certs
sudo cp /etc/letsencrypt/live/erp.tsh.sale/*.pem nginx/ssl/
sudo chown $(whoami):$(whoami) nginx/ssl/*.pem

# Start with SSL
docker compose --profile proxy up -d

# Test HTTPS
curl -I https://erp.tsh.sale/health

# Check cert expiry
openssl s_client -connect erp.tsh.sale:443 < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

---

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/docs/)
- [SSL Labs SSL Test](https://www.ssllabs.com/ssltest/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
