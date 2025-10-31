# 🚀 Complete VPS Migration Guide - All-in-One DigitalOcean Deployment

**Migrate TSH Online Store + TSH ERP + PostgreSQL Database to Single DigitalOcean VPS**

This guide will help you:
- ✅ Migrate Supabase PostgreSQL to local VPS database
- ✅ Deploy TSH ERP (FastAPI + React)
- ✅ Deploy TSH Online Store (Next.js)
- ✅ Setup SSL certificates
- ✅ Configure automated backups

**Estimated Time:** 3-4 hours
**Recommended VPS:** $24/month (4GB RAM, 2 vCPUs)

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DigitalOcean VPS                         │
│                   (Single Droplet)                          │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │ Nginx Reverse Proxy (Port 80/443)                 │    │
│  │                                                    │    │
│  │  erp.tsh.sale      → FastAPI Backend (Port 8000)  │    │
│  │  shop.tsh.sale     → Next.js App (Port 3000)      │    │
│  │  www.tsh.sale      → Next.js App (Port 3000)      │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │ Applications                                       │    │
│  │                                                    │    │
│  │  • FastAPI (TSH ERP) - Port 8000                  │    │
│  │  • Next.js (Online Store) - Port 3000             │    │
│  │  • React (ERP Frontend) - Served by Nginx         │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │ PostgreSQL Database - Port 5432                   │    │
│  │                                                    │    │
│  │  • tsh_erp database                               │    │
│  │  • All tables and data from Supabase              │    │
│  │  • Automatic daily backups                        │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Phase 1: Create Larger DigitalOcean Droplet

### Step 1: Create Droplet

1. **Login to DigitalOcean**
   - Go to https://cloud.digitalocean.com
   - Click "Create" → "Droplets"

2. **Choose Configuration**
   ```
   Region: Frankfurt (closest to Iraq) or Amsterdam

   Image: Ubuntu 22.04 LTS x64

   Droplet Size:
   ⭐ RECOMMENDED: Basic Plan - Regular CPU
   - $24/month: 4 GB RAM / 2 vCPUs / 80 GB SSD / 4 TB Transfer

   OR if budget tight:
   - $18/month: 2 GB RAM / 2 vCPUs / 60 GB SSD / 3 TB Transfer
   ```

3. **Additional Options**
   - ✅ Enable: IPv6
   - ✅ Enable: Monitoring (free)
   - ✅ Add: Backups ($4.80/month - recommended!)

4. **Authentication**
   ```bash
   # On your Mac, generate SSH key if not exists
   ssh-keygen -t rsa -b 4096 -C "khaleel@tsh.sale"

   # Copy public key
   cat ~/.ssh/id_rsa.pub
   ```
   - Paste into DigitalOcean "New SSH Key"

5. **Hostname**
   ```
   tsh-production-all-in-one
   ```

6. **Click "Create Droplet"**
   - Note IP address: `________________`

---

## 🎯 Phase 2: Initial Server Setup

### Step 2: Connect and Update

```bash
# SSH into server
ssh root@YOUR_DROPLET_IP

# Update system
apt update && apt upgrade -y

# Set timezone
timedatectl set-timezone Asia/Baghdad

# Install essential tools
apt install -y curl wget git vim ufw htop ncdu
```

### Step 3: Create Users

```bash
# Create deploy user
adduser deploy
usermod -aG sudo deploy

# Setup SSH for deploy user
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

### Step 4: Configure Firewall

```bash
# Allow SSH
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow PostgreSQL (only from localhost for security)
# We'll access it through SSH tunnel from outside

# Enable firewall
ufw --force enable
ufw status
```

---

## 🎯 Phase 3: Install PostgreSQL

### Step 5: Install PostgreSQL 14

```bash
# Switch to deploy user
su - deploy

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib postgresql-client

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

### Step 6: Configure PostgreSQL

```bash
# Switch to postgres user
sudo -i -u postgres

# Access PostgreSQL
psql

# Create database and user
CREATE DATABASE tsh_erp;
CREATE USER tsh_admin WITH ENCRYPTED PASSWORD 'CHANGE_THIS_STRONG_PASSWORD_123!@#';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tsh_erp TO tsh_admin;
ALTER DATABASE tsh_erp OWNER TO tsh_admin;

# Connect to database and grant schema privileges
\c tsh_erp
GRANT ALL ON SCHEMA public TO tsh_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO tsh_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO tsh_admin;

# Exit psql
\q
exit
```

### Step 7: Configure PostgreSQL for Network Access

```bash
# Edit PostgreSQL config to allow local network connections
sudo nano /etc/postgresql/14/main/postgresql.conf
```

**Find and modify:**
```conf
# Change listen_addresses
listen_addresses = 'localhost'  # Keep as localhost for security

# Increase max connections if needed
max_connections = 200
```

**Save and exit**

```bash
# Edit authentication config
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

**Add at the end:**
```conf
# Local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

**Save and exit**

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Test connection
psql -h localhost -U tsh_admin -d tsh_erp
# Enter password when prompted
# If successful, you'll see: tsh_erp=>
\q
```

---

## 🎯 Phase 4: Export Data from Supabase

### Step 8: Export Supabase Database

**Option A: Using Supabase Dashboard (Recommended)**

1. Login to Supabase Dashboard: https://supabase.com/dashboard
2. Go to your project
3. Click "Database" → "Backups" → "Download Backup"
4. Save file as `supabase_backup.sql`

**Option B: Using pg_dump (Direct)**

```bash
# On your local Mac, export database
export PGPASSWORD='Zcbbm.97531tsh'

pg_dump \
  -h aws-1-eu-north-1.pooler.supabase.com \
  -p 5432 \
  -U postgres.trjjglxhteqnzmyakxhe \
  -d postgres \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  -f supabase_backup.sql

# You should now have supabase_backup.sql file
```

### Step 9: Upload Backup to VPS

```bash
# On your local Mac, upload to VPS
scp supabase_backup.sql deploy@YOUR_DROPLET_IP:/home/deploy/

# SSH into VPS
ssh deploy@YOUR_DROPLET_IP

# Verify file is there
ls -lh ~/supabase_backup.sql
```

### Step 10: Import Data to VPS PostgreSQL

```bash
# On VPS, import the database
export PGPASSWORD='YOUR_POSTGRES_PASSWORD'

psql -h localhost -U tsh_admin -d tsh_erp -f ~/supabase_backup.sql

# This will take a few minutes depending on data size
# You'll see CREATE TABLE, INSERT statements
```

### Step 11: Verify Data Import

```bash
# Connect to database
psql -h localhost -U tsh_admin -d tsh_erp

# Check tables
\dt

# Check row counts
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM users;

# Exit
\q
```

---

## 🎯 Phase 5: Install Required Software

### Step 12: Install Python 3.11

```bash
# Install Python
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Verify
python3.11 --version
```

### Step 13: Install Node.js 18

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version
npm --version
```

### Step 14: Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start and enable
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 15: Install PM2 (for Next.js)

```bash
# Install PM2 globally
sudo npm install -g pm2

# Setup PM2 to start on boot
pm2 startup
# Run the command it outputs
```

---

## 🎯 Phase 6: Deploy TSH ERP (FastAPI + React)

### Step 16: Clone TSH ERP

```bash
# Navigate to home
cd /home/deploy

# Clone repository
git clone https://github.com/YOUR_USERNAME/TSH_ERP_Ecosystem.git
cd TSH_ERP_Ecosystem
```

### Step 17: Setup Backend

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn uvicorn[standard]
```

### Step 18: Create Environment File

```bash
nano .env
```

**Paste (update password):**
```env
# Database - Local PostgreSQL
DATABASE_URL=postgresql://tsh_admin:YOUR_POSTGRES_PASSWORD@localhost:5432/tsh_erp

# Application
PYTHONPATH=/home/deploy/TSH_ERP_Ecosystem
APP_ENV=production
DEBUG=False

# API
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=GENERATE_A_STRONG_RANDOM_KEY_HERE_32_CHARS_MIN
ALLOWED_HOSTS=erp.tsh.sale,www.erp.tsh.sale,YOUR_DROPLET_IP

# CORS
CORS_ORIGINS=https://erp.tsh.sale,https://www.erp.tsh.sale,https://shop.tsh.sale,https://www.tsh.sale
```

**Save and exit**

### Step 19: Setup Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

### Step 20: Create Systemd Service

```bash
sudo nano /etc/systemd/system/tsh-erp.service
```

**Paste:**
```ini
[Unit]
Description=TSH ERP FastAPI Application
After=network.target postgresql.service

[Service]
Type=notify
User=deploy
Group=deploy
WorkingDirectory=/home/deploy/TSH_ERP_Ecosystem
Environment="PATH=/home/deploy/TSH_ERP_Ecosystem/venv/bin"
Environment="PYTHONPATH=/home/deploy/TSH_ERP_Ecosystem"
EnvironmentFile=/home/deploy/TSH_ERP_Ecosystem/.env
ExecStart=/home/deploy/TSH_ERP_Ecosystem/venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/tsh-erp/access.log \
    --error-logfile /var/log/tsh-erp/error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and exit**

```bash
# Create log directory
sudo mkdir -p /var/log/tsh-erp
sudo chown deploy:deploy /var/log/tsh-erp

# Start service
sudo systemctl daemon-reload
sudo systemctl enable tsh-erp
sudo systemctl start tsh-erp

# Check status
sudo systemctl status tsh-erp
```

---

## 🎯 Phase 7: Deploy TSH Online Store (Next.js)

### Step 21: Clone Online Store

```bash
cd /home/deploy
git clone https://github.com/YOUR_USERNAME/tsh-online-store.git
cd tsh-online-store
```

### Step 22: Create Environment File

```bash
nano .env.local
```

**Paste:**
```env
# Database - Local PostgreSQL
DATABASE_URL=postgresql://tsh_admin:YOUR_POSTGRES_PASSWORD@localhost:5432/tsh_erp

# Supabase (now using local DB, but keeping URL format)
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_DROPLET_IP
NEXT_PUBLIC_SUPABASE_ANON_KEY=not_needed_anymore
SUPABASE_SERVICE_ROLE_KEY=not_needed_anymore

# Zoho API
ZOHO_CLIENT_ID=1000.RYRPK7578ZRKN6K4HKNF4LKL2CC9IQ
ZOHO_CLIENT_SECRET=a39a5dcdc057a8490cb7960d1400f62ce14edd6455
ZOHO_REFRESH_TOKEN=1000.46b59c983826f1ac35a620f243c490f2.8417561af04f558a86cc412eb58ba0e9
ZOHO_ORGANIZATION_ID=748369814

# Cron Secret
CRON_SECRET=GENERATE_ANOTHER_STRONG_RANDOM_KEY_HERE

# Site URL
NEXT_PUBLIC_SITE_URL=https://www.tsh.sale
```

**Save and exit**

### Step 23: Install and Build

```bash
# Install dependencies
npm install

# Build for production
npm run build
```

### Step 24: Start with PM2

```bash
# Start Next.js with PM2
pm2 start npm --name "tsh-online-store" -- start

# Save PM2 configuration
pm2 save

# Check status
pm2 list
pm2 logs tsh-online-store
```

---

## 🎯 Phase 8: Configure Nginx for All Services

### Step 25: Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/tsh-all
```

**Paste:**
```nginx
# Upstream backends
upstream fastapi_backend {
    server 127.0.0.1:8000;
}

upstream nextjs_frontend {
    server 127.0.0.1:3000;
}

# Redirect all HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name erp.tsh.sale shop.tsh.sale www.tsh.sale tsh.sale;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# ERP Frontend & API (erp.tsh.sale)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name erp.tsh.sale;

    # SSL will be configured by Certbot

    client_max_body_size 100M;

    # API Endpoints
    location /api/ {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }

    # Static files
    location /static/ {
        alias /home/deploy/TSH_ERP_Ecosystem/app/static/;
        expires 30d;
    }

    location /images/ {
        alias /home/deploy/TSH_ERP_Ecosystem/app/images/;
        expires 30d;
    }

    # React Frontend
    location / {
        root /home/deploy/TSH_ERP_Ecosystem/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
    }
}

# Online Store (shop.tsh.sale & www.tsh.sale)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name shop.tsh.sale www.tsh.sale tsh.sale;

    # SSL will be configured by Certbot

    client_max_body_size 50M;

    # Next.js Application
    location / {
        proxy_pass http://nextjs_frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Next.js static files
    location /_next/static/ {
        proxy_pass http://nextjs_frontend;
        proxy_cache_valid 200 60m;
        add_header Cache-Control "public, immutable";
    }
}
```

**Save and exit**

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tsh-all /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

---

## 🎯 Phase 9: Configure DNS

### Step 26: Add DNS Records

Add these A records in your domain registrar:

```
Type: A  |  Host: @           |  Value: YOUR_DROPLET_IP  |  TTL: 300
Type: A  |  Host: www         |  Value: YOUR_DROPLET_IP  |  TTL: 300
Type: A  |  Host: erp         |  Value: YOUR_DROPLET_IP  |  TTL: 300
Type: A  |  Host: shop        |  Value: YOUR_DROPLET_IP  |  TTL: 300
```

Wait 5-10 minutes, then test:
```bash
ping www.tsh.sale
ping erp.tsh.sale
ping shop.tsh.sale
```

---

## 🎯 Phase 10: Setup SSL Certificates

### Step 27: Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo mkdir -p /var/www/certbot
```

### Step 28: Obtain Certificates

```bash
# Get certificates for all domains
sudo certbot --nginx \
  -d tsh.sale \
  -d www.tsh.sale \
  -d shop.tsh.sale \
  -d erp.tsh.sale \
  --email khaleel@tsh.sale \
  --agree-tos \
  --no-eff-email

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## 🎯 Phase 11: Setup Automated Backups

### Step 29: Create Backup Script

```bash
sudo nano /usr/local/bin/backup-tsh.sh
```

**Paste:**
```bash
#!/bin/bash

# TSH Complete Backup Script
BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/tsh-backup-$DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
export PGPASSWORD='YOUR_POSTGRES_PASSWORD'
pg_dump -h localhost -U tsh_admin -d tsh_erp | gzip > "$BACKUP_FILE-database.sql.gz"

# Backup application files
tar -czf "$BACKUP_FILE-files.tar.gz" \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  /home/deploy/TSH_ERP_Ecosystem \
  /home/deploy/tsh-online-store

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "tsh-backup-*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "tsh-backup-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

**Save and exit**

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-tsh.sh

# Test backup
sudo /usr/local/bin/backup-tsh.sh
```

### Step 30: Schedule Daily Backups

```bash
# Edit crontab
sudo crontab -e
```

**Add:**
```cron
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-tsh.sh >> /var/log/tsh-backup.log 2>&1
```

**Save and exit**

---

## 🎯 Phase 12: Update Mobile Apps

### Step 31: Update Flutter App Configuration

On your local Mac:

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/06_tsh_salesperson_app
```

Edit `lib/config/app_config.dart`:

```dart
// Update to use VPS domain
static const String baseUrl = 'https://erp.tsh.sale';
static const String apiEndpoint = '/api';
```

Rebuild and deploy mobile app.

---

## 🎉 Migration Complete!

Your complete TSH system is now running on a single DigitalOcean VPS!

**Access Points:**
- Online Store: https://www.tsh.sale
- ERP Frontend: https://erp.tsh.sale
- ERP API: https://erp.tsh.sale/api
- API Docs: https://erp.tsh.sale/api/docs

**What You've Achieved:**
- ✅ Complete control over all infrastructure
- ✅ Local PostgreSQL database (faster, no external dependencies)
- ✅ Both applications on one server
- ✅ Automated daily backups
- ✅ SSL certificates for all domains
- ✅ No more Supabase costs (if you cancel)
- ✅ No more Vercel egress limits

**Monthly Cost:**
- DigitalOcean VPS: $24/month (or $18/month for smaller)
- Total: **$24/month** (vs $0 before, but with full control)

---

## 📊 Maintenance Commands

```bash
# View all services status
sudo systemctl status tsh-erp
pm2 status

# View logs
sudo journalctl -u tsh-erp -f
pm2 logs tsh-online-store

# Restart services
sudo systemctl restart tsh-erp
pm2 restart tsh-online-store

# Check database
psql -h localhost -U tsh_admin -d tsh_erp

# Check disk space
df -h

# Check memory
free -h
```

---

## 🆘 Need Help?

Common issues are documented in the main guide. If you get stuck:
1. Check service logs
2. Verify database connection
3. Test with curl from localhost first
4. Check firewall rules

**Made with ❤️ for TSH - Complete VPS Solution**
