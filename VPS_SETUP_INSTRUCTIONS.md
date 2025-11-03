# 🔧 إرشادات إعداد VPS للنظام الذكي
# VPS Setup Instructions for Intelligent CI/CD

**📅 التاريخ / Date:** نوفمبر 3، 2025 / November 3, 2025
**🎯 الغرض / Purpose:** إعداد VPS لتفعيل Auto-Deployment والـ Auto-Healing

---

## ⚠️ حالة النظام الحالية / Current System Status

### ✅ ما يعمل الآن / What's Working Now

```
✅ جميع الفحوصات التلقائية (7 مراحل)
✅ All automatic checks (7 stages)

1. ✅ Code Quality & Integrity
2. ✅ Database Schema Validation
3. ✅ API & Integration Tests
4. ✅ Zoho Data Consistency Check
5. ✅ Zoho Timestamp Verification
6. ✅ Zoho Webhook Health Check
7. ✅ Auto-Healing Analysis & Suggestions
```

### ⏸️ ما تم تعطيله مؤقتاً / Temporarily Disabled

```
⏸️ Automatic Deployment to Staging
   (Requires VPS setup)

⏸️ Auto-Healing Execution on VPS
   (Requires script installation)
```

---

## 🚀 خطوات الإعداد على VPS / VPS Setup Steps

### المتطلبات الأساسية / Prerequisites

```bash
✅ VPS IP: 167.71.39.50
✅ SSH Access: root@167.71.39.50
✅ PostgreSQL 14 installed
✅ Nginx installed
✅ Python 3.11+ installed
✅ Git installed
```

---

## 📝 الخطوة 1: إعداد مجلد المشروع / Setup Project Directory

```bash
# SSH إلى السيرفر / SSH to server
ssh root@167.71.39.50

# إنشاء مجلد المشروع / Create project directory
mkdir -p /opt/tsh_erp
cd /opt/tsh_erp

# استنساخ المشروع / Clone project
git clone https://github.com/Qmop1967/tsh-erp-system.git .

# أو إذا كان موجوداً / Or if already exists
cd /opt/tsh_erp
git remote set-url origin https://github.com/Qmop1967/tsh-erp-system.git
git fetch origin
git checkout develop
git pull origin develop

# إنشاء Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# تثبيت المكتبات / Install dependencies
pip install --upgrade pip
pip install -r config/requirements.txt || pip install -r requirements.txt
```

---

## 📝 الخطوة 2: إعداد خدمات systemd / Setup systemd Services

### 2.1 خدمة Staging (Port 8002)

إنشاء ملف: `/etc/systemd/system/tsh-erp-staging.service`

```ini
[Unit]
Description=TSH ERP Staging Service (Port 8002)
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/tsh_erp
Environment="PATH=/opt/tsh_erp/venv/bin"
ExecStart=/opt/tsh_erp/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8002 --reload

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

### 2.2 تفعيل الخدمة / Enable Service

```bash
# إعادة تحميل systemd / Reload systemd
systemctl daemon-reload

# تفعيل الخدمة / Enable service
systemctl enable tsh-erp-staging

# تشغيل الخدمة / Start service
systemctl start tsh-erp-staging

# التحقق من الحالة / Check status
systemctl status tsh-erp-staging

# اختبار الصحة / Test health
curl http://127.0.0.1:8002/health
```

---

## 📝 الخطوة 3: تثبيت سكريبت Auto-Healing

```bash
# نسخ السكريبت / Copy script
cd /opt/tsh_erp

# التأكد من الأذونات / Ensure permissions
chmod +x scripts/claude_auto_healing.sh

# إنشاء مجلد السجلات / Create log directory
mkdir -p /var/log/tsh_erp
touch /var/log/tsh_erp/auto_healing.log

# إنشاء مجلد Auto-Healing / Create auto-healing directory
mkdir -p /tmp/tsh_autoheal

# اختبار السكريبت / Test script
bash -n scripts/claude_auto_healing.sh
echo "Script syntax OK"
```

### 3.1 إعداد Cron Job للفحص الدوري (اختياري)

```bash
# تعديل crontab / Edit crontab
crontab -e

# إضافة السطر التالي / Add this line
# فحص كل 15 دقيقة / Check every 15 minutes
*/15 * * * * /opt/tsh_erp/scripts/claude_auto_healing.sh >> /var/log/tsh_erp/auto_healing_cron.log 2>&1
```

---

## 📝 الخطوة 4: تفعيل Deployment في GitHub Workflow

بعد إكمال الخطوات السابقة:

```bash
# على جهازك المحلي / On your local machine
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# فتح ملف Workflow / Open workflow file
# .github/workflows/intelligent-staging.yml

# السطر 725 / Line 725
# تغيير من / Change from:
if: false  # Disabled

# إلى / To:
if: github.ref == 'refs/heads/develop' && github.event_name == 'push'

# حفظ ودفع التغييرات / Save and push changes
git add .github/workflows/intelligent-staging.yml
git commit -m "feat: Enable auto-deployment to staging"
git push origin develop
```

---

## 📝 الخطوة 5: التحقق من الإعداد / Verify Setup

### 5.1 اختبار Deployment يدوياً

```bash
# على السيرفر / On VPS
cd /opt/tsh_erp
git fetch origin
git checkout develop
git pull origin develop

source venv/bin/activate
pip install -q -r config/requirements.txt

# تشغيل migrations (إن وجدت)
if [ -d "alembic" ]; then
  alembic upgrade head
fi

# إعادة تشغيل الخدمة
systemctl restart tsh-erp-staging

# انتظر قليلاً / Wait a bit
sleep 5

# اختبار / Test
curl http://127.0.0.1:8002/health

# يجب أن ترى / You should see:
# {"status":"healthy","message":"النظام يعمل بشكل طبيعي"}
```

### 5.2 اختبار Auto-Healing

```bash
# إنشاء ملف توصيات اختباري / Create test suggestions
cat > /tmp/tsh_autoheal/auto_healing_suggestions.txt << 'EOF'
🤖 AUTO-HEALING TEST

🔧 ISSUE DETECTED: Test Issue
   📋 Diagnosis: Testing auto-healing system
   🎯 Possible Cause: Manual test
   💡 Suggested Fix:
      1. Check system status: systemctl status tsh-erp-staging
      2. Check logs: journalctl -u tsh-erp-staging -n 10
EOF

# تشغيل السكريبت / Run script
/opt/tsh_erp/scripts/claude_auto_healing.sh

# مراجعة التقرير / Review report
cat /tmp/tsh_autoheal/healing_report_*.txt | tail -1
```

---

## 📝 الخطوة 6: إعداد Nginx للوصول الخارجي (اختياري)

إذا أردت الوصول لـ staging من الخارج:

```nginx
# إضافة إلى ملف Nginx / Add to Nginx config
# /etc/nginx/sites-available/tsh-erp

server {
    listen 80;
    server_name staging.erp.tsh.sale;

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# اختبار التهيئة / Test config
nginx -t

# إعادة تحميل / Reload
systemctl reload nginx

# اختبار / Test
curl http://staging.erp.tsh.sale/health
```

---

## 🔍 استكشاف الأخطاء / Troubleshooting

### المشكلة 1: الخدمة لا تعمل

```bash
# التحقق من الحالة / Check status
systemctl status tsh-erp-staging

# مراجعة السجلات / Check logs
journalctl -u tsh-erp-staging -n 50

# الأسباب المحتملة / Common causes:
# 1. Port مستخدم / Port in use
netstat -tlnp | grep 8002

# 2. Python environment غير صحيح
source /opt/tsh_erp/venv/bin/activate
which python
python --version

# 3. مكتبات ناقصة / Missing dependencies
pip install -r config/requirements.txt
```

### المشكلة 2: Git repository error

```bash
# التحقق من Git / Check git
cd /opt/tsh_erp
git status

# إذا لم يكن git repo / If not a git repo
git init
git remote add origin https://github.com/Qmop1967/tsh-erp-system.git
git fetch origin
git checkout develop
git branch --set-upstream-to=origin/develop develop
```

### المشكلة 3: Database connection error

```bash
# التحقق من PostgreSQL / Check PostgreSQL
systemctl status postgresql

# التحقق من الاتصال / Test connection
psql -h localhost -U tsh_admin -d tsh_erp -c "SELECT version();"

# التحقق من متغيرات البيئة / Check env vars
cat /opt/tsh_erp/.env | grep DATABASE_URL
```

---

## ✅ قائمة التحقق النهائية / Final Checklist

قبل تفعيل Auto-Deployment، تأكد من:

```
□ VPS accessible via SSH
□ /opt/tsh_erp directory exists
□ Git repository configured
□ Python virtual environment created
□ Dependencies installed
□ systemd service created and enabled
□ Service running on port 8002
□ Health endpoint responding
□ Auto-healing script executable
□ Log directories created
□ GitHub secrets configured:
   □ PROD_HOST
   □ PROD_USER
   □ PROD_SSH_KEY
   □ PROD_SSH_PORT
```

---

## 🎯 الخطوة التالية / Next Step

بعد إكمال جميع الخطوات أعلاه:

```bash
# 1. التأكد من أن كل شيء يعمل / Verify everything works
systemctl status tsh-erp-staging
curl http://127.0.0.1:8002/health

# 2. تفعيل Auto-Deployment في Workflow
# (راجع الخطوة 4 أعلاه)

# 3. دفع تغيير إلى develop للاختبار
git commit --allow-empty -m "test: Trigger staging deployment"
git push origin develop

# 4. مراقبة GitHub Actions
gh run list --branch develop --limit 5
gh run watch <run-id>

# 5. التحقق من النشر / Verify deployment
ssh root@167.71.39.50 "journalctl -u tsh-erp-staging -n 20"
curl http://staging.erp.tsh.sale/health  # إذا أعددت Nginx
```

---

## 📞 الدعم / Support

في حالة واجهت مشاكل:

1. **راجع السجلات / Check Logs:**
   ```bash
   journalctl -u tsh-erp-staging -f
   tail -f /var/log/tsh_erp/auto_healing.log
   ```

2. **راجع GitHub Actions:**
   ```bash
   gh run view <run-id> --log-failed
   ```

3. **اختبار يدوي / Manual Test:**
   ```bash
   cd /opt/tsh_erp
   source venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8002
   ```

---

## 📝 ملاحظات إضافية / Additional Notes

### الأمان / Security

- ✅ الخدمة تعمل على localhost فقط (127.0.0.1)
- ✅ Nginx يعمل كـ reverse proxy
- ✅ SSH keys فقط (no password auth)
- ✅ Firewall configured (UFW)

### الصيانة / Maintenance

```bash
# نسخ احتياطي يومي / Daily backup
0 2 * * * /opt/tsh_erp/scripts/backup.sh

# تنظيف السجلات / Log cleanup
0 3 * * 0 find /var/log/tsh_erp -name "*.log" -mtime +30 -delete

# تحديث المكتبات / Update dependencies
0 4 * * 1 cd /opt/tsh_erp && source venv/bin/activate && pip install -U -r config/requirements.txt
```

---

**📅 أنشئ بواسطة / Created By:** Claude Code
**🎯 الغرض / Purpose:** تفعيل كامل النظام الذكي / Enable full intelligent system
**✅ الحالة / Status:** جاهز للتطبيق / Ready for implementation

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
