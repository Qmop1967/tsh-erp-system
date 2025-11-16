# ✅ Quick Start Checklist - DigitalOcean Deployment

Use this checklist to track your deployment progress.

---

## 📋 Pre-Deployment Checklist

- [ ] DigitalOcean account created and payment method added
- [ ] Domain name registered (e.g., `erp.tsh.sale`)
- [ ] SSH key generated on local machine
- [ ] GitHub repository is up to date
- [ ] PostgreSQL database credentials ready
- [ ] Email address for SSL certificate notifications

---

## 🚀 Phase 1: DigitalOcean Setup (15 minutes)

- [ ] **Create Droplet**
  - [ ] Select Ubuntu 22.04 LTS
  - [ ] Choose $12/month plan (2GB RAM)
  - [ ] Add SSH key
  - [ ] Set hostname: `tsh-erp-production`
  - [ ] Note droplet IP address: `___________________`

- [ ] **Initial Connection**
  - [ ] SSH into server: `ssh root@YOUR_DROPLET_IP`
  - [ ] Update system: `apt update && apt upgrade -y`

---

## 🛠️ Phase 2: Server Configuration (30 minutes)

- [ ] **Create Deploy User**
  - [ ] Create user: `adduser deploy`
  - [ ] Add to sudo: `usermod -aG sudo deploy`
  - [ ] Copy SSH keys to deploy user
  - [ ] Test login: `ssh deploy@YOUR_DROPLET_IP`

- [ ] **Configure Firewall**
  - [ ] Allow SSH (22)
  - [ ] Allow HTTP (80)
  - [ ] Allow HTTPS (443)
  - [ ] Enable firewall: `ufw --force enable`

- [ ] **Install Software**
  - [ ] Python 3.11 installed
  - [ ] Node.js 18 installed
  - [ ] Nginx installed and running
  - [ ] Supervisor installed

---

## 📦 Phase 3: Application Setup (30 minutes)

- [ ] **Clone Repository**
  - [ ] Repository cloned to `/home/deploy/TSH_ERP_Ecosystem`
  - [ ] Ownership set to deploy user

- [ ] **Backend Setup**
  - [ ] Virtual environment created
  - [ ] Dependencies installed
  - [ ] Gunicorn installed

- [ ] **Frontend Setup**
  - [ ] NPM dependencies installed
  - [ ] Production build created (`npm run build`)

- [ ] **Environment Configuration**
  - [ ] `.env` file created
  - [ ] Database URL configured
  - [ ] PostgreSQL credentials configured
  - [ ] Secret key generated and set

---

## ⚙️ Phase 4: Service Configuration (20 minutes)

- [ ] **Systemd Service**
  - [ ] Service file created: `/etc/systemd/system/tsh-erp.service`
  - [ ] Log directory created: `/var/log/tsh-erp`
  - [ ] Service enabled and started
  - [ ] Service status checked: `sudo systemctl status tsh-erp`

- [ ] **Nginx Configuration**
  - [ ] Config file created: `/etc/nginx/sites-available/tsh-erp`
  - [ ] Symlink created in sites-enabled
  - [ ] Default site removed
  - [ ] Configuration tested: `sudo nginx -t`
  - [ ] Nginx reloaded

---

## 🌐 Phase 5: DNS & SSL (30 minutes)

- [ ] **DNS Configuration**
  - [ ] A record added for `erp` subdomain
  - [ ] A record added for `www.erp` subdomain
  - [ ] DNS propagation verified (wait 5-10 minutes)
  - [ ] Ping test successful: `ping erp.tsh.sale`

- [ ] **SSL Certificate**
  - [ ] Certbot installed
  - [ ] Certificate obtained for domain
  - [ ] HTTPS tested in browser
  - [ ] Auto-renewal tested: `sudo certbot renew --dry-run`

---

## 🧪 Phase 6: Testing & Verification (15 minutes)

- [ ] **Application Access**
  - [ ] Frontend loads: `https://erp.tsh.sale`
  - [ ] API responding: `https://erp.tsh.sale/api/health`
  - [ ] API docs accessible: `https://erp.tsh.sale/api/docs`

- [ ] **Functionality Tests**
  - [ ] Login working
  - [ ] Dashboard loading
  - [ ] Database connection working
  - [ ] Static files serving correctly

- [ ] **Mobile App Update**
  - [ ] Mobile app API URL updated
  - [ ] Mobile app rebuilt
  - [ ] Mobile app tested with production API

---

## 📊 Phase 7: Monitoring Setup (Optional, 15 minutes)

- [ ] **Logging**
  - [ ] Application logs accessible
  - [ ] Nginx logs accessible
  - [ ] Log rotation configured

- [ ] **Monitoring**
  - [ ] Uptime monitoring configured (UptimeRobot)
  - [ ] Error tracking configured (Sentry)
  - [ ] Performance monitoring configured

---

## 🔒 Phase 8: Security Hardening (Optional, 20 minutes)

- [ ] **SSH Security**
  - [ ] Password authentication disabled
  - [ ] Root login disabled
  - [ ] SSH port changed (optional)

- [ ] **Application Security**
  - [ ] Environment variables secured
  - [ ] File permissions checked
  - [ ] CORS configured correctly
  - [ ] Rate limiting configured

---

## 📝 Post-Deployment Notes

**Droplet Information:**
```
IP Address: ___________________
Domain: ___________________
SSH User: deploy
SSH Port: 22
```

**Important Directories:**
```
Application: /home/deploy/TSH_ERP_Ecosystem
Logs: /var/log/tsh-erp
Nginx Config: /etc/nginx/sites-available/tsh-erp
Service File: /etc/systemd/system/tsh-erp.service
```

**Common Commands:**
```bash
# Restart application
sudo systemctl restart tsh-erp

# View logs
sudo journalctl -u tsh-erp -f

# Deploy updates
cd /home/deploy/TSH_ERP_Ecosystem && ./deploy.sh
```

---

## 🎉 Deployment Complete!

**Estimated Total Time: 2-3 hours**

Your TSH ERP system is now live on DigitalOcean! 🚀

**Next Steps:**
1. ✅ Test all functionality thoroughly
2. ✅ Update mobile apps with production API URL
3. ✅ Set up regular backups
4. ✅ Configure monitoring and alerts
5. ✅ Document any custom configurations

---

## 📞 Need Help?

**Common Issues:**
- Service won't start: Check logs with `sudo journalctl -u tsh-erp -n 50`
- Nginx errors: Test config with `sudo nginx -t`
- Database issues: Verify connection string in `.env`
- SSL issues: Check certbot logs: `sudo certbot certificates`

**Support Resources:**
- DigitalOcean Community: https://www.digitalocean.com/community
- FastAPI Documentation: https://fastapi.tiangolo.com
- Nginx Documentation: https://nginx.org/en/docs/

---

**Made with ❤️ for TSH**
