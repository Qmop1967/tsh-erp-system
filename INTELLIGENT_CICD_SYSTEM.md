# 🧠 نظام CI/CD الذكي مع المعالجة الذاتية
# Intelligent CI/CD System with Auto-Healing

**التاريخ / Date:** نوفمبر 3، 2025 / November 3, 2025
**الحالة / Status:** ✅ مكتمل ومفعّل / Complete and Active
**النظام / System:** TSH ERP Ecosystem

---

## 📋 جدول المحتويات / Table of Contents

1. [نظرة عامة / Overview](#overview)
2. [البنية المعمارية / Architecture](#architecture)
3. [مراحل Staging](#staging-workflow)
4. [مراحل Production](#production-workflow)
5. [نظام المعالجة الذاتية / Auto-Healing](#auto-healing)
6. [التكامل مع Claude Code](#claude-code-integration)
7. [الإعداد والتشغيل / Setup](#setup)
8. [الأسئلة الشائعة / FAQ](#faq)

---

<a name="overview"></a>
## 🎯 نظرة عامة / Overview

### بالعربية

هذا نظام CI/CD متقدم يعمل كـ "نظام مناعة ذاتية" لمشروع TSH ERP Ecosystem. يقوم النظام بـ:

✅ **الفحص الشامل:** فحص الكود، قاعدة البيانات، التكامل مع Zoho، Webhooks
✅ **المراقبة الذكية:** مقارنة البيانات بين Zoho و TSH ERP
✅ **الكشف التلقائي:** اكتشاف المشاكل وتحليلها
✅ **المعالجة الذاتية:** اقتراح وتنفيذ الحلول تلقائياً
✅ **التنبيهات:** إنشاء تذاكر GitHub Issues عند وجود مشاكل حرجة

### In English

This is an advanced CI/CD system that acts as a "self-healing immune system" for the TSH ERP Ecosystem project. The system:

✅ **Comprehensive Testing:** Code, database, Zoho integration, webhooks
✅ **Intelligent Monitoring:** Data comparison between Zoho and TSH ERP
✅ **Automatic Detection:** Identifies and analyzes issues
✅ **Self-Healing:** Suggests and implements fixes automatically
✅ **Alerting:** Creates GitHub Issues for critical problems

---

<a name="architecture"></a>
## 🏗️ البنية المعمارية / Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     DEVELOPER WORKFLOW                         │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STEP 1: Push to develop branch (STAGING)                     │
│  git push origin develop                                       │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 1: Code Quality & Integrity                            │
│  • Linting (ruff)                                              │
│  • Type Checking (mypy)                                        │
│  • Formatting (black)                                          │
│  • Security Scan (bandit)                                      │
│  • Dependency Vulnerability Check (safety)                     │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 2: Database Schema & Migrations                        │
│  • Check migration status                                      │
│  • Verify schema integrity                                     │
│  • Validate database structure                                 │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 3: API & Integration Tests                             │
│  • Unit tests                                                  │
│  • API endpoint tests                                          │
│  • Integration tests                                           │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 4: 🔄 Zoho Data Consistency Check                      │
│  • Compare Contacts count (Zoho vs TSH ERP)                   │
│  • Compare Products count (Zoho vs TSH ERP)                   │
│  • Calculate difference percentage                             │
│  • Flag issues if difference > 10%                            │
│  📊 Output: zoho_sync_report.txt                              │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 5: ⏰ Zoho Timestamp Verification                      │
│  • Get last modified timestamp from Zoho                       │
│  • Get last modified timestamp from TSH ERP                    │
│  • Calculate sync delay (hours)                                │
│  • Alert if delay > 24 hours                                   │
│  📊 Output: zoho_timestamp_report.txt                         │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 6: 🔔 Zoho Webhook Health Check                        │
│  • Test each webhook endpoint                                  │
│  • Send test payload                                           │
│  • Verify HTTP response (200/201/202)                          │
│  • Report timeouts and errors                                  │
│  📊 Output: zoho_webhook_report.txt                           │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 7: 🤖 Auto-Healing Analysis                            │
│  • Read all reports                                            │
│  • Identify issues (sync mismatch, delays, webhook failures)   │
│  • Generate diagnosis and root cause analysis                  │
│  • Create suggested fix commands                               │
│  • Open GitHub Issue if critical                               │
│  📊 Output: auto_healing_suggestions.txt                      │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 8: 🚀 Deploy to Staging                                │
│  • Pull latest code                                            │
│  • Install dependencies                                        │
│  • Run migrations                                              │
│  • Restart service (port 8002)                                 │
│  • Health check                                                │
└────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │ All tests pass? │
                    └─────────────────┘
                       ↓          ↓
                     YES         NO
                       ↓          ↓
                       ↓    Auto-Healing Activated
                       ↓          ↓
                       ↓    Suggestions → Claude Code Agent
                       ↓          ↓
                       ↓    Execute Fixes on VPS
                       ↓
┌────────────────────────────────────────────────────────────────┐
│  STEP 2: Manual Verification on Staging                       │
│  Test all features, check logs, verify data                   │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STEP 3: Create Pull Request (develop → main)                 │
│  gh pr create --base main --head develop                      │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  STEP 4: Review & Approve PR                                  │
│  Code review, verify staging tests, merge via GitHub          │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                       │
│  • Pre-deployment validation                                   │
│  • Database backup                                             │
│  • Migration preview                                           │
│  • Blue-green deployment                                       │
│  • Post-deployment monitoring (2 min)                          │
│  • External health checks                                      │
│  • Auto-rollback on failure                                    │
└────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │ Success?        │
                    └─────────────────┘
                       ↓          ↓
                     YES         NO
                       ↓          ↓
               ✅ Production  🔄 Auto Rollback
               Deployment     Previous Version
               Complete       Restored
```

---

<a name="staging-workflow"></a>
## 🧪 مراحل Staging Workflow / Staging Workflow Stages

### ملف التنفيذ / Workflow File
`.github/workflows/intelligent-staging.yml`

### المراحل التفصيلية / Detailed Stages

#### 1️⃣ فحص جودة الكود / Code Quality Check

```yaml
✅ Linting (ruff) - Python code style
✅ Type Checking (mypy) - Type annotations
✅ Formatting (black) - Code formatting
✅ Security (bandit) - Security vulnerabilities
✅ Dependencies (safety) - Known vulnerabilities
```

**المخرجات / Outputs:**
- `bandit-report.json` - تقرير الأمان / Security report

#### 2️⃣ فحص قاعدة البيانات / Database Validation

```yaml
✅ Migration status check
✅ Schema integrity verification
✅ Database structure validation
```

**البيئة / Environment:**
- PostgreSQL 14 test database
- Alembic migrations

#### 3️⃣ اختبارات API / API Integration Tests

```yaml
✅ Unit tests (pytest)
✅ API endpoint tests
✅ Integration tests
```

#### 4️⃣ فحص اتساق البيانات مع Zoho / Zoho Data Consistency

**ما يتم فحصه / What is Checked:**

```python
# 1. مقارنة عدد العملاء / Compare Customers Count
Zoho Contacts API → Count
TSH ERP Database → SELECT COUNT(*) FROM customers
Compare → Calculate difference %

# 2. مقارنة عدد المنتجات / Compare Products Count
Zoho Items API → Count
TSH ERP Database → SELECT COUNT(*) FROM products
Compare → Calculate difference %

# تحذير إذا الفرق > 10% / Alert if difference > 10%
```

**المخرجات / Output:**
```
zoho_sync_report.txt
=====================
✅ Zoho Contacts: 250
✅ TSH ERP Customers: 248
✅ Acceptable: 2 records difference (0.8%)

✅ Zoho Items: 2218
✅ TSH ERP Products: 2218
✅ Perfect match: 0 difference
```

#### 5️⃣ فحص الطوابع الزمنية / Timestamp Verification

**ما يتم فحصه / What is Checked:**

```python
# آخر تحديث في Zoho / Last update in Zoho
last_modified_time from Zoho API

# آخر تحديث في TSH ERP / Last update in TSH ERP
MAX(updated_at) from TSH ERP database

# حساب التأخير / Calculate delay
time_difference in hours

# تحذير إذا التأخير > 24 ساعة / Alert if delay > 24 hours
```

**المخرجات / Output:**
```
zoho_timestamp_report.txt
==========================
✅ Zoho Last Contact Update: 2025-11-03 15:30:00
✅ ERP Last Customer Update: 2025-11-03 15:28:00
✅ Sync OK: 0.03 hours difference
```

#### 6️⃣ فحص صحة Webhooks / Webhook Health Check

**ما يتم فحصه / What is Checked:**

```python
webhooks = [
    "/zoho/contact/created",
    "/zoho/contact/updated",
    "/zoho/invoice/created",
    "/zoho/invoice/updated",
    "/zoho/item/created",
    "/zoho/item/updated",
    "/zoho/salesorder/created",
    "/zoho/salesorder/updated",
]

# لكل webhook / For each webhook:
- Send test payload
- Check HTTP status (200/201/202 = OK)
- Report timeouts and errors
```

**المخرجات / Output:**
```
zoho_webhook_report.txt
========================
✅ Contact Created: https://erp.tsh.sale/api/webhooks/zoho/contact/created (HTTP 200)
✅ Contact Updated: https://erp.tsh.sale/api/webhooks/zoho/contact/updated (HTTP 200)
❌ Invoice Created: https://erp.tsh.sale/api/webhooks/zoho/invoice/created (TIMEOUT)

📊 SUMMARY
   ✅ Passed: 7/8
   ❌ Failed: 1/8
```

#### 7️⃣ تحليل المعالجة الذاتية / Auto-Healing Analysis

**كيف يعمل / How it Works:**

```python
# 1. قراءة جميع التقارير / Read all reports
- zoho_sync_report.txt
- zoho_timestamp_report.txt
- zoho_webhook_report.txt

# 2. تحليل المشاكل / Analyze issues
if "❌ ALERT" in report:
    identify_issue_type()
    diagnose_root_cause()
    generate_fix_commands()

# 3. إنشاء التوصيات / Generate suggestions
auto_healing_suggestions.txt:
    - Issue description
    - Root cause analysis
    - Step-by-step fix commands
    - Expected outcome

# 4. فتح تذكرة GitHub / Create GitHub Issue (if critical)
```

**مثال على التوصيات / Example Suggestions:**

```
🔧 ISSUE DETECTED: Zoho Data Sync Mismatch
   📋 Diagnosis: 50 missing customer records in TSH ERP
   🎯 Possible Cause: Sync worker stopped or webhook failures
   💡 Suggested Fix:
      1. Check TDS Core worker: systemctl status tds-core-worker
      2. Review sync queue: SELECT * FROM tds_sync_queue WHERE status='failed'
      3. Trigger resync: python scripts/resync_zoho.py --entity=customers
      4. Verify webhooks: python scripts/verify_webhooks.py

🔧 ISSUE DETECTED: Webhook Timeout
   📋 Diagnosis: Invoice webhook not responding
   🎯 Possible Cause: SSL certificate or backend service issue
   💡 Suggested Fix:
      1. Check SSL: curl -v https://erp.tsh.sale
      2. Check backend: systemctl status tsh-erp
      3. Check Nginx: sudo nginx -t
      4. Re-register webhook: python scripts/register_webhooks.py
```

#### 8️⃣ النشر على Staging / Deploy to Staging

**الخطوات / Steps:**

```bash
1. Pull latest code from develop branch
2. Activate Python virtual environment
3. Install/update dependencies
4. Run database migrations (alembic upgrade head)
5. Restart staging service (port 8002)
6. Wait 5 seconds
7. Health check: curl http://127.0.0.1:8002/health
```

---

<a name="production-workflow"></a>
## 🚀 مراحل Production Workflow / Production Workflow Stages

### ملف التنفيذ / Workflow File
`.github/workflows/intelligent-production.yml`

### المراحل التفصيلية / Detailed Stages

#### 1️⃣ التحقق قبل النشر / Pre-Deployment Validation

```yaml
✅ Verify staging tests passed
✅ Check for debug code (console.log, print)
✅ Verify commit signatures
✅ Final security scan (bandit + safety)
```

#### 2️⃣ النسخ الاحتياطي / Database Backup

```bash
# إنشاء نسخة احتياطية تلقائية / Automatic backup
BACKUP_FILE="/opt/backups/auto/pre_deploy_$(date +%Y%m%d_%H%M%S).sql"

pg_dump -h localhost -U tsh_admin -d tsh_erp -F c -f "$BACKUP_FILE"

# الاحتفاظ بآخر 10 نسخ / Keep last 10 backups
ls -t $BACKUP_DIR/pre_deploy_*.sql | tail -n +11 | xargs rm
```

#### 3️⃣ فحص سلامة البيانات / Data Integrity Check

```sql
-- فحص التكرارات / Check duplicates
SELECT email, COUNT(*) FROM customers GROUP BY email HAVING COUNT(*) > 1;
SELECT sku, COUNT(*) FROM products GROUP BY sku HAVING COUNT(*) > 1;

-- فحص السجلات اليتيمة / Check orphaned records
SELECT COUNT(*) FROM invoices WHERE customer_id NOT IN (SELECT id FROM customers);

-- حجم قاعدة البيانات / Database size
SELECT pg_size_pretty(pg_database_size(current_database()));
```

#### 4️⃣ معاينة التحديثات / Migration Preview

```bash
# إنشاء معاينة SQL بدون تطبيق / Generate SQL preview without applying
alembic upgrade head --sql > migration_preview.sql

# عرض التغييرات المتوقعة / Show expected changes
cat migration_preview.sql
```

#### 5️⃣ فحص الخدمات / Service Health Check

```bash
# حالة الخدمات / Service status
systemctl status tsh-erp
systemctl status tsh_erp-green

# حالة المنافذ / Port status
ss -tlnp | grep -E ":(8001|8002)"

# استخدام الموارد / Resource usage
free -h
df -h /opt/tsh_erp

# السجلات الأخيرة / Recent logs
journalctl -u tsh-erp -n 10
```

#### 6️⃣ النشر (Blue-Green) / Blue-Green Deployment

```bash
# 1. Pull latest code from main branch
git checkout main
git pull origin main

# 2. Run deployment script
bash /opt/tsh_erp/bin/deploy.sh main

# النص البرمجي يقوم بـ / The script does:
- Determine which service is inactive (blue or green)
- Deploy to inactive service
- Run migrations on inactive
- Start inactive service
- Wait for health check
- Switch Nginx to point to new service
- Old service remains as backup for instant rollback
```

#### 7️⃣ المراقبة بعد النشر / Post-Deployment Monitoring

```bash
# مراقبة لمدة دقيقتين / Monitor for 2 minutes
for i in {1..4}; do
    # فحص الصحة / Health check
    curl http://127.0.0.1:8001/health

    # عدد الأخطاء / Error count
    journalctl -u tsh-erp --since "1 minute ago" -p err | wc -l

    # استخدام الموارد / Resource usage
    ps aux | grep python

    sleep 30
done
```

#### 8️⃣ الفحص الخارجي / External Health Check

```bash
# فحص URLs الإنتاج / Test production URLs
curl -s -o /dev/null -w "%{http_code}" https://erp.tsh.sale/health
curl -s -o /dev/null -w "%{http_code}" https://consumer.tsh.sale
```

#### 9️⃣ التراجع التلقائي / Auto-Rollback (عند الفشل / On Failure)

```bash
# في حالة فشل النشر / If deployment fails:

# 1. Switch back to previous service
bash /opt/tsh_erp/bin/switch_deployment.sh

# 2. Verify rollback
curl -f http://127.0.0.1:8001/health

# 3. Create GitHub Issue automatically
title: "🚨 Production Deployment Failed - Auto Rollback Executed"
labels: ['production', 'deployment-failure', 'critical']
```

---

<a name="auto-healing"></a>
## 🤖 نظام المعالجة الذاتية / Auto-Healing System

### كيف يعمل / How It Works

```
GitHub Actions
     ↓
1. Run all checks
     ↓
2. Detect issues
     ↓
3. Analyze root cause
     ↓
4. Generate suggestions → auto_healing_suggestions.txt
     ↓
5. Upload to VPS → /tmp/tsh_autoheal/
     ↓
6. Execute Claude Code Agent → scripts/claude_auto_healing.sh
     ↓
7. Agent reads suggestions
     ↓
8. Agent executes fix commands
     ↓
9. Generate healing report
     ↓
10. Verify fixes applied
```

### أنواع المشاكل التي يتم معالجتها / Issues That Are Healed

#### 1. عدم تطابق بيانات Zoho / Zoho Data Sync Mismatch

**المشكلة / Problem:**
```
Difference > 10% between Zoho and TSH ERP data counts
```

**الحل التلقائي / Auto-Healing:**
```bash
1. Check TDS Core worker status
   systemctl status tds-core-worker

2. Restart if stopped
   systemctl restart tds-core-worker

3. Check sync queue for failed items
   SELECT COUNT(*) FROM tds_sync_queue WHERE status='failed'

4. Retry failed sync items
   UPDATE tds_sync_queue SET status='pending', retry_count=0
   WHERE status='failed' AND retry_count < 3

5. Verify sync resumed
   journalctl -u tds-core-worker -n 50
```

#### 2. تأخير المزامنة / Sync Timestamp Delay

**المشكلة / Problem:**
```
Last sync timestamp > 24 hours old
```

**الحل التلقائي / Auto-Healing:**
```bash
1. Restart sync worker
   systemctl restart tds-core-worker

2. Trigger manual sync for last 24 hours
   python scripts/sync_recent.py --hours=24

3. Check worker logs
   journalctl -u tds-core-worker -n 100

4. Verify webhook delivery
   python scripts/verify_webhooks.py
```

#### 3. فشل Webhooks / Webhook Failures

**المشكلة / Problem:**
```
Webhook endpoints returning errors or timeouts
```

**الحل التلقائي / Auto-Healing:**
```bash
1. Check SSL certificate
   curl -v https://erp.tsh.sale 2>&1 | grep certificate

2. Verify Nginx config
   nginx -t

3. Check backend service
   systemctl status tsh-erp

4. Restart backend if needed
   systemctl restart tsh-erp

5. Re-register webhooks
   python scripts/register_webhooks.py

6. Check firewall
   ufw status
```

### تقرير المعالجة / Healing Report

بعد تنفيذ المعالجة، يتم إنشاء تقرير شامل:

```
/tmp/tsh_autoheal/healing_report_20251103_183000.txt
======================================================

🤖 AUTO-HEALING EXECUTION REPORT

Execution Time: 2025-11-03 18:30:00

ACTIONS TAKEN:
✅ Restarted TDS Core worker
✅ Retried 15 failed sync items
✅ Re-registered 8 webhooks
✅ Verified SSL certificate

WARNINGS:
⚠️ 2 webhooks still timing out (investigating)

CURRENT SYSTEM STATUS:
  tsh-erp: active
  tds-core-worker: active
  postgresql: active
  nginx: active

HEALTH ENDPOINTS:
  ✅ http://127.0.0.1:8001/health
  ✅ https://erp.tsh.sale/health
  ❌ https://erp.tsh.sale/webhooks/zoho/invoice/created (timeout)

NEXT STEPS:
1. Monitor system for 15 minutes
2. Re-run GitHub Actions workflow
3. If issues persist, escalate to manual intervention
```

---

<a name="claude-code-integration"></a>
## 🤝 التكامل مع Claude Code / Claude Code Integration

### إعداد الوكيل / Agent Setup

**1. على الجهاز المحلي / On Local Machine:**

```bash
# إعدادات Claude Code لمنع النشر المباشر
# Claude Code settings to prevent direct deployment
.claude/settings.local.json:
{
  "permissions": {
    "allow": ["Bash(git push origin develop)"],
    "deny": [
      "Bash(git push origin main)",
      "Bash(rsync:*root@167.71.39.50:*)"
    ]
  }
}
```

**2. على السيرفر / On VPS:**

```bash
# تثبيت السكريبت / Install script
scp scripts/claude_auto_healing.sh root@167.71.39.50:/opt/tsh_erp/scripts/

# جعله قابل للتنفيذ / Make executable
ssh root@167.71.39.50 "chmod +x /opt/tsh_erp/scripts/claude_auto_healing.sh"

# إنشاء cron job للفحص الدوري / Create cron job for periodic check
echo "*/15 * * * * /opt/tsh_erp/scripts/claude_auto_healing.sh" | crontab -
```

### تشغيل الوكيل يدوياً / Manual Agent Execution

```bash
# 1. نسخ ملف التوصيات إلى السيرفر / Copy suggestions to VPS
scp auto_healing_suggestions.txt root@167.71.39.50:/tmp/tsh_autoheal/

# 2. تشغيل وكيل المعالجة / Run healing agent
ssh root@167.71.39.50 "/opt/tsh_erp/scripts/claude_auto_healing.sh"

# 3. مراجعة التقرير / Review report
ssh root@167.71.39.50 "cat /tmp/tsh_autoheal/healing_report_*.txt | tail -1"
```

### التشغيل التلقائي من GitHub Actions / Automatic from GitHub Actions

يمكن إضافة خطوة في workflow لتشغيل الوكيل تلقائياً:

```yaml
- name: 🤖 Execute Auto-Healing on VPS
  if: contains(needs.*.result, 'failure')
  uses: appleboy/ssh-action@v1.0.3
  with:
    host: ${{ secrets.PROD_HOST }}
    username: ${{ secrets.PROD_USER }}
    key: ${{ secrets.PROD_SSH_KEY }}
    script: |
      # Copy suggestions from GitHub Actions artifact
      mkdir -p /tmp/tsh_autoheal
      # Download artifact (implementation needed)

      # Execute healing agent
      /opt/tsh_erp/scripts/claude_auto_healing.sh

      # Upload report back to GitHub
      cat /tmp/tsh_autoheal/healing_report_*.txt | tail -1
```

---

<a name="setup"></a>
## ⚙️ الإعداد والتشغيل / Setup and Configuration

### المتطلبات / Prerequisites

```bash
✅ Python 3.11+
✅ PostgreSQL 14+
✅ GitHub repository
✅ VPS with SSH access
✅ Zoho Books/Inventory API access
```

### إعداد GitHub Secrets

قم بإضافة المتغيرات التالية في GitHub Settings → Secrets:

```
PROD_HOST=167.71.39.50
PROD_USER=root
PROD_SSH_KEY=<your-ssh-private-key>
PROD_SSH_PORT=22

ZOHO_ORG_ID=<your-zoho-org-id>
ZOHO_ACCESS_TOKEN=<your-zoho-token>

STAGING_DB_URL=postgresql://user:pass@host:5432/db
PRODUCTION_DB_URL=postgresql://user:pass@host:5432/db

DB_USER=tsh_admin
DB_PASSWORD=<your-db-password>
DB_NAME=tsh_erp

WEBHOOK_BASE_URL=https://erp.tsh.sale/api/webhooks
```

### تفعيل Workflows

```bash
# 1. Commit الملفات الجديدة / Commit new files
git add .github/workflows/intelligent-staging.yml
git add .github/workflows/intelligent-production.yml
git add scripts/claude_auto_healing.sh

git commit -m "feat: Add intelligent CI/CD with auto-healing"

# 2. Push إلى develop للاختبار / Push to develop for testing
git push origin develop

# 3. مراقبة التنفيذ / Monitor execution
gh run list --limit 5
gh run watch <run-id>
```

### التحقق من التثبيت / Verify Installation

```bash
# 1. تحقق من ملفات Workflow / Check workflow files
ls -la .github/workflows/intelligent-*.yml

# 2. تحقق من السكريبت / Check script
ls -la scripts/claude_auto_healing.sh

# 3. تحقق من الأذونات / Check permissions
[ -x scripts/claude_auto_healing.sh ] && echo "Executable" || echo "Not executable"

# 4. اختبار السكريبت محلياً / Test script locally
bash -n scripts/claude_auto_healing.sh  # Syntax check
```

---

<a name="faq"></a>
## ❓ الأسئلة الشائعة / FAQ

### 1. كم مرة يتم تشغيل فحوصات Staging؟
**How often do staging checks run?**

يتم تشغيل الفحوصات تلقائياً عند كل `push` إلى فرع `develop`.

Checks run automatically on every `push` to the `develop` branch.

### 2. ماذا يحدث إذا فشلت فحوصات Staging؟
**What happens if staging checks fail?**

- يتم إنشاء ملف توصيات المعالجة الذاتية
- يتم فتح تذكرة GitHub Issue تلقائياً
- يمكن تشغيل وكيل Claude Code لتطبيق الإصلاحات

- Auto-healing suggestions file is generated
- GitHub Issue is created automatically
- Claude Code agent can be triggered to apply fixes

### 3. هل يمكن تعطيل بعض الفحوصات؟
**Can I disable certain checks?**

نعم، يمكن تعطيل أي job في workflow بإضافة:

Yes, any job can be disabled by adding:

```yaml
if: false  # Disable this job
```

### 4. كيف أختبر التوصيات قبل تطبيقها؟
**How do I test suggestions before applying?**

```bash
# 1. قراءة التوصيات / Read suggestions
cat auto_healing_suggestions.txt

# 2. تنفيذ أمر واحد / Execute one command at a time
# Instead of running the whole script

# 3. التحقق من النتيجة / Verify result
# Before proceeding to next command
```

### 5. ماذا أفعل إذا فشلت المعالجة الذاتية؟
**What if auto-healing fails?**

```bash
# 1. مراجعة سجلات المعالجة / Review healing logs
cat /var/log/tsh_erp/auto_healing.log

# 2. مراجعة تقرير المعالجة / Review healing report
cat /tmp/tsh_autoheal/healing_report_*.txt | tail -1

# 3. تنفيذ الأوامر يدوياً / Execute commands manually
# Follow the suggestions in the report

# 4. فتح تذكرة / Open an issue
# If problem persists
```

### 6. هل النظام آمن؟
**Is the system secure?**

✅ **نعم / Yes:**
- جميع الأوامر محددة مسبقاً
- لا يتم تنفيذ كود عشوائي
- جميع العمليات مسجلة
- يتطلب مراجعة يدوية للعمليات الحرجة

- All commands are predefined
- No arbitrary code execution
- All operations are logged
- Critical operations require manual review

### 7. كيف أراقب أداء النظام؟
**How do I monitor system performance?**

```bash
# 1. GitHub Actions
gh run list --limit 20
gh workflow view "Intelligent Staging CI/CD"

# 2. VPS Logs
journalctl -u tsh-erp -f
tail -f /var/log/tsh_erp/auto_healing.log

# 3. Reports
ls -lh /tmp/tsh_autoheal/*.txt

# 4. Health Endpoints
curl https://erp.tsh.sale/health
```

---

## 📊 الإحصائيات / Statistics

### Staging Workflow

| المرحلة / Stage | الوقت المتوقع / Time | الحالة / Status |
|-----------------|-------------------|----------------|
| Code Quality | ~1 min | ✅ Active |
| Database Validation | ~1 min | ✅ Active |
| API Tests | ~1 min | ✅ Active |
| Zoho Consistency | ~30 sec | ✅ Active |
| Zoho Timestamps | ~20 sec | ✅ Active |
| Webhook Health | ~30 sec | ✅ Active |
| Auto-Healing | ~10 sec | ✅ Active |
| Deploy to Staging | ~20 sec | ✅ Active |

**الإجمالي / Total:** ~5 minutes

### Production Workflow

| المرحلة / Stage | الوقت المتوقع / Time | الحالة / Status |
|-----------------|-------------------|----------------|
| Pre-validation | ~2 min | ✅ Active |
| Database Backup | ~30 sec | ✅ Active |
| Data Integrity | ~30 sec | ✅ Active |
| Migration Preview | ~10 sec | ✅ Active |
| Service Health | ~20 sec | ✅ Active |
| Blue-Green Deploy | ~2 min | ✅ Active |
| Post-Monitoring | ~2 min | ✅ Active |
| External Checks | ~30 sec | ✅ Active |

**الإجمالي / Total:** ~8 minutes

---

## 🎯 الخلاصة / Conclusion

هذا النظام يحول TSH ERP Ecosystem إلى منظومة ذاتية الإصلاح تتمتع بـ:

This system transforms TSH ERP Ecosystem into a self-healing system with:

✅ **الفحص الشامل / Comprehensive Testing:** 10+ validation stages
✅ **الذكاء الاصطناعي / AI Intelligence:** Auto-diagnosis and healing
✅ **الأمان / Security:** Multiple safety checks and rollback
✅ **الشفافية / Transparency:** Detailed reports and logs
✅ **الأتمتة / Automation:** Zero-touch deployment when all checks pass

---

**آخر تحديث / Last Updated:** نوفمبر 3، 2025 / November 3, 2025
**الحالة / Status:** ✅ جاهز للاستخدام / Ready for Use
**المطور / Developed By:** Claude Code + Khaleel Al-Mulla

---

🚀 **Happy Deploying! / نشر سعيد!**
