# TSH ERP System - VPS Deployment Guide

Complete guide for deploying TSH ERP System to a production VPS server.

---

## 📋 Prerequisites

### VPS Requirements:
- **OS**: Ubuntu 22.04 LTS (recommended)
- **RAM**: Minimum 4GB (8GB recommended)
- **CPU**: 2+ cores
- **Storage**: 50GB+ SSD
- **Network**: Public IP address
- **Domain**: erp.tsh.sale (or your domain)

### Required Software:
- Docker 24+
- Docker Compose 2+
- Git
- SSL Certificate (Let's Encrypt)

---

## 🚀 Step 1: Initial VPS Setup

### 1.1 Connect to VPS
```bash
ssh root@YOUR_VPS_IP
```

### 1.2 Update System
```bash
apt update && apt upgrade -y
```

### 1.3 Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Start Docker service
systemctl start docker
systemctl enable docker

# Verify installation
docker --version
```

### 1.4 Install Docker Compose
```bash
# Download Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 1.5 Install Git
```bash
apt install git -y
git --version
```

---

## 📦 Step 2: Deploy Application

### 2.1 Clone Repository
```bash
# Create application directory
mkdir -p /opt/tsh_erp
cd /opt/tsh_erp

# Clone from your Git repository
git clone https://github.com/YOUR_USERNAME/TSH_ERP_Ecosystem.git .

# Or upload via SCP
# scp -r /path/to/TSH_ERP_Ecosystem root@YOUR_VPS_IP:/opt/tsh_erp/
```

### 2.2 Configure Environment
```bash
# Copy production environment file
cp .env.production .env

# Edit environment variables
nano .env
```

**Important variables to configure:**
```env
# Database
DATABASE_URL=postgresql://tsh_admin:CHANGE_THIS_PASSWORD@postgres:5432/tsh_erp
DB_PASSWORD=CHANGE_THIS_PASSWORD

# JWT Secret (generate strong key)
SECRET_KEY=GENERATE_STRONG_RANDOM_KEY_HERE

# Domain
CORS_ORIGINS=["https://erp.tsh.sale", "https://www.erp.tsh.sale"]

# Zoho Integration
ZOHO_CLIENT_ID=your_zoho_client_id
ZOHO_CLIENT_SECRET=your_zoho_client_secret
ZOHO_REFRESH_TOKEN=your_zoho_refresh_token
```

**Generate strong SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.3 Build and Start Services
```bash
# Build Docker images
./deploy.sh build

# Start services
./deploy.sh start

# Check status
./deploy.sh status
```

---

## 🔐 Step 3: Configure SSL (HTTPS)

### 3.1 Install Certbot
```bash
apt install certbot python3-certbot-nginx -y
```

### 3.2 Obtain SSL Certificate
```bash
# Stop nginx temporarily
./deploy.sh stop

# Get certificate
certbot certonly --standalone -d erp.tsh.sale -d www.erp.tsh.sale

# Certificate will be saved to:
# /etc/letsencrypt/live/erp.tsh.sale/fullchain.pem
# /etc/letsencrypt/live/erp.tsh.sale/privkey.pem
```

### 3.3 Copy Certificates to Docker Volume
```bash
mkdir -p /opt/tsh_erp/nginx/ssl
cp /etc/letsencrypt/live/erp.tsh.sale/fullchain.pem /opt/tsh_erp/nginx/ssl/
cp /etc/letsencrypt/live/erp.tsh.sale/privkey.pem /opt/tsh_erp/nginx/ssl/
```

### 3.4 Set Up Auto-Renewal
```bash
# Add cron job for certificate renewal
crontab -e

# Add this line (renew at 2 AM daily)
0 2 * * * certbot renew --quiet && cp /etc/letsencrypt/live/erp.tsh.sale/*.pem /opt/tsh_erp/nginx/ssl/ && docker-compose restart nginx
```

### 3.5 Restart Services
```bash
./deploy.sh restart
```

---

## 🔍 Step 4: Verify Deployment

### 4.1 Check Service Health
```bash
# Check all services
docker-compose ps

# Should show all services as "healthy"
```

### 4.2 Test HTTP Access
```bash
curl http://erp.tsh.sale/health
# Should return: {"status": "healthy"}
```

### 4.3 Test HTTPS Access
```bash
curl https://erp.tsh.sale/health
# Should return: {"status": "healthy"}
```

### 4.4 Check Logs
```bash
# View application logs
./deploy.sh logs

# Or specific service
docker-compose logs app
docker-compose logs postgres
docker-compose logs nginx
```

---

## 🛠️ Step 5: Database Setup

### 5.1 Run Migrations
```bash
./deploy.sh migrate
```

### 5.2 Create Admin User (Optional)
```bash
# Connect to app container
docker-compose exec app bash

# Run Python script to create admin user
python3 -c "
from app.db.database import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService

db = SessionLocal()
admin = User(
    email='admin@tsh.sale',
    name='Administrator',
    password=AuthService.get_password_hash('CHANGE_THIS_PASSWORD'),
    role_id=1,
    is_active=True
)
db.add(admin)
db.commit()
print('Admin user created!')
"

exit
```

---

## 📊 Step 6: Monitor & Maintain

### 6.1 View System Status
```bash
# Service status
./deploy.sh status

# Resource usage
docker stats

# Disk usage
df -h
```

### 6.2 View Logs
```bash
# Real-time logs
./deploy.sh logs

# Specific service
docker-compose logs -f app
```

### 6.3 Create Database Backup
```bash
# Manual backup
./deploy.sh backup

# Backups saved to: /opt/tsh_erp/backups/
```

### 6.4 Set Up Automated Backups
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * cd /opt/tsh_erp && ./deploy.sh backup

# Keep only last 7 backups (add to crontab)
0 3 * * * find /opt/tsh_erp/backups -name "*.sql" -mtime +7 -delete
```

---

## 🔄 Step 7: Update Application

### 7.1 Pull Latest Code
```bash
cd /opt/tsh_erp
git pull origin main
```

### 7.2 Update and Restart
```bash
./deploy.sh update
```

This will:
- Pull latest code
- Rebuild Docker images
- Stop services
- Start services
- Run database migrations

---

## 🚨 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check memory
free -m

# Restart services
./deploy.sh restart
```

### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Connect to database manually
docker-compose exec postgres psql -U tsh_admin -d tsh_erp

# Test connection
\dt
```

### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in /opt/tsh_erp/nginx/ssl/fullchain.pem -text -noout

# Renew certificate manually
certbot renew --force-renewal
```

### High Memory Usage
```bash
# Check container resource usage
docker stats

# Restart services to clear memory
./deploy.sh restart
```

---

## 🔒 Security Best Practices

### 1. Firewall Configuration
```bash
# Install UFW
apt install ufw -y

# Allow SSH
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### 2. Change Default Passwords
- Database password in `.env`
- Admin user password
- SSH password (use SSH keys instead)

### 3. Regular Updates
```bash
# Update system packages weekly
apt update && apt upgrade -y

# Update Docker images monthly
./deploy.sh update
```

### 4. Monitor Logs
```bash
# Check for suspicious activity
grep -i "error\|fail\|unauthorized" /opt/tsh_erp/logs/*.log
```

---

## 📞 Support

If you encounter issues:
1. Check logs: `./deploy.sh logs`
2. Check status: `./deploy.sh status`
3. Restart services: `./deploy.sh restart`
4. Contact system administrator

---

## 📝 Quick Reference

### Common Commands
```bash
# Start system
./deploy.sh start

# Stop system
./deploy.sh stop

# Restart system
./deploy.sh restart

# View logs
./deploy.sh logs

# Check status
./deploy.sh status

# Run migrations
./deploy.sh migrate

# Create backup
./deploy.sh backup

# Update application
./deploy.sh update
```

### Service URLs
- **Application**: https://erp.tsh.sale
- **API Docs**: https://erp.tsh.sale/docs
- **Health Check**: https://erp.tsh.sale/health

---

**Deployment completed! 🎉**

Your TSH ERP System is now running in production on your VPS.
