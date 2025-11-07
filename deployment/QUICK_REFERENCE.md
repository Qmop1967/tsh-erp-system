# 🚀 Quick Reference - All-in-One VPS Migration

**Quick copy-paste commands for experienced users**

---

## 📦 VPS Specs

```
Recommended: $24/month
- 4 GB RAM
- 2 vCPUs
- 80 GB SSD
- Ubuntu 22.04 LTS
```

---

## ⚡ Quick Setup Commands

### 1. Initial Setup (5 min)
```bash
# Update system
apt update && apt upgrade -y

# Create user
adduser deploy
usermod -aG sudo deploy
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh

# Firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

### 2. Install Software (10 min)
```bash
su - deploy

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Python 3.11
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Nginx & PM2
sudo apt install -y nginx
sudo npm install -g pm2
pm2 startup

# Certbot
sudo apt install -y certbot python3-certbot-nginx
```

### 3. Setup Database (5 min)
```bash
sudo -i -u postgres
psql

CREATE DATABASE tsh_erp;
CREATE USER tsh_admin WITH ENCRYPTED PASSWORD 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE tsh_erp TO tsh_admin;
ALTER DATABASE tsh_erp OWNER TO tsh_admin;
\c tsh_erp
GRANT ALL ON SCHEMA public TO tsh_admin;
\q
exit
```

### 4. Import Self-Hosted PostgreSQL Data (10 min)
```bash
# On local Mac - Export from Self-Hosted PostgreSQL
export PGPASSWORD='TSH@2025Secure!Production'
pg_dump -h localhost -p 5432 \
  -U tsh_app_user -d tsh_erp \
  --clean --if-exists --no-owner --no-privileges \
  -f local PostgreSQL_backup.sql

# Upload to VPS
scp local PostgreSQL_backup.sql deploy@YOUR_IP:/home/deploy/

# On VPS - Import
export PGPASSWORD='YOUR_STRONG_PASSWORD'
psql -h localhost -U tsh_admin -d tsh_erp -f ~/local PostgreSQL_backup.sql
```

### 5. Deploy TSH ERP (15 min)
```bash
cd /home/deploy
git clone YOUR_REPO_URL TSH_ERP_Ecosystem
cd TSH_ERP_Ecosystem

# Backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn uvicorn[standard]

# Create .env
cat > .env << EOF
DATABASE_URL=postgresql://tsh_admin:YOUR_PASSWORD@localhost:5432/tsh_erp
PYTHONPATH=/home/deploy/TSH_ERP_Ecosystem
SECRET_KEY=$(openssl rand -base64 32)
EOF

# Frontend
cd frontend
npm install
npm run build
cd ..
```

### 6. Create Systemd Service (5 min)
```bash
sudo tee /etc/systemd/system/tsh-erp.service > /dev/null << EOF
[Unit]
Description=TSH ERP FastAPI
After=network.target postgresql.service

[Service]
Type=notify
User=deploy
WorkingDirectory=/home/deploy/TSH_ERP_Ecosystem
Environment="PATH=/home/deploy/TSH_ERP_Ecosystem/venv/bin"
EnvironmentFile=/home/deploy/TSH_ERP_Ecosystem/.env
ExecStart=/home/deploy/TSH_ERP_Ecosystem/venv/bin/gunicorn app.main:app \
  --workers 4 --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo mkdir -p /var/log/tsh-erp
sudo chown deploy:deploy /var/log/tsh-erp
sudo systemctl daemon-reload
sudo systemctl enable --now tsh-erp
```

### 7. Deploy Online Store (10 min)
```bash
cd /home/deploy
git clone YOUR_ONLINE_STORE_REPO tsh-online-store
cd tsh-online-store

# Create .env.local
cat > .env.local << EOF
DATABASE_URL=postgresql://tsh_admin:YOUR_PASSWORD@localhost:5432/tsh_erp
ZOHO_CLIENT_ID=1000.RYRPK7578ZRKN6K4HKNF4LKL2CC9IQ
ZOHO_CLIENT_SECRET=a39a5dcdc057a8490cb7960d1400f62ce14edd6455
ZOHO_REFRESH_TOKEN=1000.46b59c983826f1ac35a620f243c490f2.8417561af04f558a86cc412eb58ba0e9
ZOHO_ORGANIZATION_ID=748369814
CRON_SECRET=$(openssl rand -base64 32)
NEXT_PUBLIC_SITE_URL=https://www.tsh.sale
EOF

npm install
npm run build
pm2 start npm --name "tsh-online-store" -- start
pm2 save
```

### 8. Configure Nginx (see full guide)

### 9. Setup SSL (5 min)
```bash
sudo certbot --nginx \
  -d tsh.sale -d www.tsh.sale -d shop.tsh.sale -d erp.tsh.sale \
  --email YOUR_EMAIL --agree-tos --no-eff-email
```

---

## 🔧 Daily Commands

```bash
# Restart services
sudo systemctl restart tsh-erp
pm2 restart tsh-online-store

# View logs
sudo journalctl -u tsh-erp -f
pm2 logs tsh-online-store

# Database backup
pg_dump -h localhost -U tsh_admin -d tsh_erp | gzip > backup.sql.gz

# Check status
sudo systemctl status tsh-erp
pm2 status
```

---

## 📁 Important Paths

```
Database: postgresql://tsh_admin@localhost:5432/tsh_erp
ERP: /home/deploy/TSH_ERP_Ecosystem
Store: /home/deploy/tsh-online-store
Logs: /var/log/tsh-erp/
Backups: /home/deploy/backups/
Nginx: /etc/nginx/sites-available/tsh-all
```

---

## 🌐 DNS Records

```
A    @       YOUR_DROPLET_IP
A    www     YOUR_DROPLET_IP
A    erp     YOUR_DROPLET_IP
A    shop    YOUR_DROPLET_IP
```

---

## ✅ Testing

```bash
# Test locally first
curl http://localhost:8000/health
curl http://localhost:3000

# Test externally
curl https://erp.tsh.sale/api/health
curl https://www.tsh.sale
```

---

**Total Setup Time: ~2 hours**
**Monthly Cost: $24**
