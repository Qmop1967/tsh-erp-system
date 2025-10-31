# 🚀 DigitalOcean VPS Deployment Guide - TSH ERP Ecosystem

Complete step-by-step guide to deploy TSH ERP system on DigitalOcean VPS.

---

## 📋 Prerequisites

- DigitalOcean account
- Domain name (e.g., `erp.tsh.sale` or `api.tsh.sale`)
- GitHub repository access
- Local terminal access

---

## 🎯 Phase 1: Create DigitalOcean Droplet

### Step 1: Create Droplet

1. **Login to DigitalOcean**
   - Go to https://cloud.digitalocean.com
   - Click "Create" → "Droplets"

2. **Choose Configuration**
   ```
   Region: Choose closest to Iraq (Frankfurt or Amsterdam recommended)

   Image: Ubuntu 22.04 LTS x64

   Droplet Size:
   - Basic Plan
   - Regular CPU
   - $12/month: 2 GB RAM / 1 vCPU / 50 GB SSD
   ```

3. **Authentication**
   - Choose "SSH Key" (Recommended)
   - Click "New SSH Key"
   - Run on your Mac:
   ```bash
   # Generate SSH key if you don't have one
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

   # Copy public key
   cat ~/.ssh/id_rsa.pub
   ```
   - Paste the output into DigitalOcean

4. **Hostname**
   ```
   tsh-erp-production
   ```

5. **Click "Create Droplet"**
   - Wait 1-2 minutes for creation
   - Note the IP address (e.g., `134.122.xx.xx`)

---

## 🎯 Phase 2: Initial Server Setup

### Step 2: Connect to Server

```bash
# SSH into your droplet (replace with your IP)
ssh root@YOUR_DROPLET_IP

# You should see: root@tsh-erp-production:~#
```

### Step 3: Update System

```bash
# Update package list
apt update

# Upgrade all packages
apt upgrade -y

# Install essential tools
apt install -y curl wget git vim ufw
```

### Step 4: Create Deploy User

```bash
# Create a non-root user for deployments
adduser deploy

# Add to sudo group
usermod -aG sudo deploy

# Set up SSH for deploy user
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

### Step 5: Configure Firewall

```bash
# Allow SSH
ufw allow 22/tcp

# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS
ufw allow 443/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

---

## 🎯 Phase 3: Install Required Software

### Step 6: Install Python 3.11

```bash
# Switch to deploy user
su - deploy

# Install Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Verify installation
python3.11 --version  # Should show: Python 3.11.x
```

### Step 7: Install Node.js 18

```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version   # Should show: v18.x.x
npm --version    # Should show: 9.x.x
```

### Step 8: Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### Step 9: Install Supervisor (Process Manager)

```bash
# Install Supervisor
sudo apt install -y supervisor

# Start Supervisor
sudo systemctl start supervisor
sudo systemctl enable supervisor
```

---

## 🎯 Phase 4: Clone and Setup Application

### Step 10: Clone Repository

```bash
# Navigate to home directory
cd /home/deploy

# Clone your repository (replace with your repo URL)
git clone https://github.com/YOUR_USERNAME/TSH_ERP_Ecosystem.git

# Set ownership
sudo chown -R deploy:deploy TSH_ERP_Ecosystem
cd TSH_ERP_Ecosystem
```

### Step 11: Setup Python Backend

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn uvicorn[standard]
```

### Step 12: Setup React Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Go back to root
cd ..
```

---

## 🎯 Phase 5: Configure Environment Variables

### Step 13: Create Environment File

```bash
# Create .env file
nano .env
```

**Paste the following (update with your values):**

```env
# Database Configuration (Supabase)
DATABASE_URL=postgresql://postgres.trjjglxhteqnzmyakxhe:Zcbbm.97531tsh@aws-1-eu-north-1.pooler.supabase.com:5432/postgres

# Supabase Configuration
SUPABASE_URL=https://trjjglxhteqnzmyakxhe.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRyampnbHhodGVxbnpteWFreGhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3NzU4ODksImV4cCI6MjA3NTM1MTg4OX0.2bCdqhSA-Dg1hFbybh3uWfmmra5vhzENaT6dr--JIRU
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY

# Application Settings
PYTHONPATH=/home/deploy/TSH_ERP_Ecosystem
APP_ENV=production
DEBUG=False

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=CHANGE_THIS_TO_STRONG_RANDOM_KEY_IN_PRODUCTION
ALLOWED_HOSTS=erp.tsh.sale,www.erp.tsh.sale,YOUR_DROPLET_IP

# CORS Settings
CORS_ORIGINS=https://erp.tsh.sale,https://www.erp.tsh.sale
```

**Save and exit:** `Ctrl+X`, then `Y`, then `Enter`

---

## 🎯 Phase 6: Configure Systemd Service

### Step 14: Create Systemd Service File

```bash
# Create service file
sudo nano /etc/systemd/system/tsh-erp.service
```

**Paste the following:**

```ini
[Unit]
Description=TSH ERP FastAPI Application
After=network.target

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
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/tsh-erp/access.log \
    --error-logfile /var/log/tsh-erp/error.log \
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and exit**

### Step 15: Create Log Directory

```bash
# Create log directory
sudo mkdir -p /var/log/tsh-erp
sudo chown deploy:deploy /var/log/tsh-erp
```

### Step 16: Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable tsh-erp

# Start service
sudo systemctl start tsh-erp

# Check status
sudo systemctl status tsh-erp

# Check logs
sudo journalctl -u tsh-erp -f
```

---

## 🎯 Phase 7: Configure Nginx

### Step 17: Create Nginx Configuration

```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/tsh-erp
```

**Paste the following (replace erp.tsh.sale with your domain):**

```nginx
# Upstream for FastAPI backend
upstream fastapi_backend {
    server 127.0.0.1:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name erp.tsh.sale www.erp.tsh.sale;

    # Allow Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name erp.tsh.sale www.erp.tsh.sale;

    # SSL Configuration (will be added by Certbot)
    # ssl_certificate /etc/letsencrypt/live/erp.tsh.sale/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/erp.tsh.sale/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Logs
    access_log /var/log/nginx/tsh-erp-access.log;
    error_log /var/log/nginx/tsh-erp-error.log;

    # Max upload size
    client_max_body_size 100M;

    # API Endpoints
    location /api/ {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }

    # Static files and images
    location /static/ {
        alias /home/deploy/TSH_ERP_Ecosystem/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /images/ {
        alias /home/deploy/TSH_ERP_Ecosystem/app/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /public/ {
        alias /home/deploy/TSH_ERP_Ecosystem/frontend/public/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # React Frontend (serve built files)
    location / {
        root /home/deploy/TSH_ERP_Ecosystem/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, must-revalidate";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

**Save and exit**

### Step 18: Enable Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/tsh-erp /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

---

## 🎯 Phase 8: Configure Domain DNS

### Step 19: Add DNS Records

**Go to your domain registrar (Namecheap, GoDaddy, etc.)**

Add the following DNS records:

```
Type: A
Host: erp (or api, or whatever subdomain you want)
Value: YOUR_DROPLET_IP
TTL: 300

Type: A
Host: www.erp
Value: YOUR_DROPLET_IP
TTL: 300
```

**Wait 5-10 minutes for DNS propagation**

Test with:
```bash
# From your local machine
ping erp.tsh.sale
```

---

## 🎯 Phase 9: Install SSL Certificate

### Step 20: Install Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Create webroot directory
sudo mkdir -p /var/www/certbot
sudo chown -R deploy:deploy /var/www/certbot
```

### Step 21: Obtain SSL Certificate

```bash
# Get certificate (replace with your email and domain)
sudo certbot --nginx -d erp.tsh.sale -d www.erp.tsh.sale --email your_email@example.com --agree-tos --no-eff-email

# Test auto-renewal
sudo certbot renew --dry-run
```

### Step 22: Verify HTTPS

Open browser and visit:
```
https://erp.tsh.sale
```

You should see your application running with a valid SSL certificate! 🎉

---

## 🎯 Phase 10: Setup Automatic Deployments (Optional)

### Step 23: Create Deploy Script

```bash
# Create deployment script
nano /home/deploy/TSH_ERP_Ecosystem/deploy.sh
```

**Paste the following:**

```bash
#!/bin/bash

# TSH ERP Deployment Script
# Run this script to deploy updates

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Navigate to project directory
cd /home/deploy/TSH_ERP_Ecosystem

# Pull latest code
echo "📥 Pulling latest code from Git..."
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update Python dependencies
echo "📦 Updating Python dependencies..."
pip install --upgrade -r requirements.txt

# Run database migrations (if any)
echo "🗄️  Running database migrations..."
# alembic upgrade head  # Uncomment if using Alembic

# Rebuild React frontend
echo "🎨 Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# Restart FastAPI service
echo "🔄 Restarting FastAPI service..."
sudo systemctl restart tsh-erp

# Reload Nginx
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

# Check service status
echo "✅ Checking service status..."
sudo systemctl status tsh-erp --no-pager

echo "✨ Deployment completed successfully!"
```

**Save and exit**

```bash
# Make script executable
chmod +x /home/deploy/TSH_ERP_Ecosystem/deploy.sh

# Allow deploy user to restart services without password
sudo visudo
```

**Add this line at the end:**
```
deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart tsh-erp, /bin/systemctl reload nginx, /bin/systemctl status tsh-erp
```

**Save and exit**

---

## 🎯 Phase 11: Update Flutter Mobile App

### Step 24: Update Mobile App API URL

On your local machine:

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/06_tsh_salesperson_app
```

Edit `lib/config/app_config.dart`:

```dart
// Change baseUrl from Supabase to your DigitalOcean domain
static const String baseUrl = 'https://erp.tsh.sale';
static const String apiEndpoint = '/api';
```

Rebuild and deploy the mobile app.

---

## 📊 Monitoring and Maintenance

### Useful Commands

```bash
# View FastAPI logs
sudo journalctl -u tsh-erp -f

# View Nginx access logs
sudo tail -f /var/log/nginx/tsh-erp-access.log

# View Nginx error logs
sudo tail -f /var/log/nginx/tsh-erp-error.log

# Restart FastAPI service
sudo systemctl restart tsh-erp

# Reload Nginx (without downtime)
sudo systemctl reload nginx

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
htop
```

### Regular Maintenance

```bash
# Update system packages (monthly)
sudo apt update && sudo apt upgrade -y

# Renew SSL certificate (automatic via cron, but you can force renewal)
sudo certbot renew

# Clean up old logs (if needed)
sudo journalctl --vacuum-time=30d
```

---

## 🎉 Deployment Complete!

Your TSH ERP system is now running on DigitalOcean VPS!

**Access Points:**
- **Frontend:** https://erp.tsh.sale
- **API:** https://erp.tsh.sale/api
- **API Docs:** https://erp.tsh.sale/api/docs

**Next Steps:**
1. Update mobile apps with new API URL
2. Test all functionality
3. Set up monitoring (optional: UptimeRobot, Sentry)
4. Configure automated backups

---

## 🆘 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u tsh-erp -n 50

# Check if port is in use
sudo lsof -i :8000

# Test if Python app runs manually
cd /home/deploy/TSH_ERP_Ecosystem
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Nginx errors
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

### Database connection issues
```bash
# Test database connection
cd /home/deploy/TSH_ERP_Ecosystem
source venv/bin/activate
python -c "from app.db.database import engine; print(engine.connect())"
```

---

## 📞 Support

If you encounter any issues:
1. Check logs first
2. Verify environment variables
3. Ensure all services are running
4. Check firewall rules

**Made with ❤️ for TSH**
