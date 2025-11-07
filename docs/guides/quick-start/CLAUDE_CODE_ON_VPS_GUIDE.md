# 🚀 دليل تشغيل Claude Code على VPS Ubuntu
# Running Claude Code on Ubuntu VPS Server

**Target Server:** 167.71.39.50 (DigitalOcean VPS)
**OS:** Ubuntu 22.04 LTS
**Created:** 2025-10-31

---

## 📋 جدول المحتويات / Table of Contents

1. [المتطلبات الأساسية](#prerequisites)
2. [طريقة 1: التطوير المحلي مع SSH](#method-1-local-development)
3. [طريقة 2: VS Code Remote SSH](#method-2-vscode-remote)
4. [طريقة 3: Claude Code CLI على السيرفر](#method-3-claude-on-server)
5. [طريقة 4: tmux + SSH Session](#method-4-tmux-session)
6. [الخيار الموصى به](#recommended-approach)

---

## 🔧 المتطلبات الأساسية / Prerequisites

### على جهازك المحلي (Local Machine):

✅ **Claude Code Installed**
```bash
# Verify Claude Code is installed
claude --version
```

✅ **SSH Access to Server**
```bash
# Test SSH connection
ssh root@167.71.39.50 "echo 'Connection successful'"
```

✅ **VS Code (Optional)**
```bash
# For Remote Development
code --version
```

### على السيرفر (VPS):

✅ **Node.js 18+** (for Claude Code)
```bash
ssh root@167.71.39.50 "node --version"
# If not installed: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
# sudo apt-get install -y nodejs
```

✅ **Git**
```bash
ssh root@167.71.39.50 "git --version"
```

---

## 🎯 طريقة 1: التطوير المحلي مع SSH (الموصى بها)
## Method 1: Local Development with SSH (Recommended)

**المبدأ:** تشغيل Claude Code على جهازك المحلي، مع تنفيذ الأوامر على السيرفر عبر SSH.

### المزايا:
- ✅ سهولة الاستخدام
- ✅ واجهة Claude Code الكاملة
- ✅ لا حاجة لتثبيت Claude Code على السيرفر
- ✅ يعمل الآن بدون تعديلات

### الخطوات:

#### 1. افتح Claude Code على جهازك
```bash
# From your TSH_ERP_Ecosystem directory
claude
```

#### 2. استخدم SSH في الأوامر
```bash
# Example: Check TDS Core on server
ssh root@167.71.39.50 "systemctl status tds-core"

# Deploy files
rsync -avz app/ root@167.71.39.50:/root/TSH_ERP/app/

# Run commands remotely
ssh root@167.71.39.50 "cd /root/TSH_ERP && systemctl restart tsh-erp"
```

#### 3. استخدم أوامر Claude Code العادية
```
أنت: "please check the TDS Core status on the server"
Claude: [سيقوم بتنفيذ ssh root@167.71.39.50 "systemctl status tds-core"]

أنت: "deploy the updated consumer_api.py to the server"
Claude: [سيقوم بتنفيذ scp/rsync للملف]
```

### 🎯 هذا ما تفعله حالياً! وهو الأفضل ✅

---

## 🖥️ طريقة 2: VS Code Remote SSH
## Method 2: VS Code Remote Development

**المبدأ:** فتح السيرفر في VS Code وتشغيل Claude Code من داخله.

### الخطوات:

#### 1. تثبيت VS Code Remote Extension
```bash
# Install on local machine
code --install-extension ms-vscode-remote.remote-ssh
```

#### 2. إعداد SSH Config
```bash
# Edit ~/.ssh/config
cat >> ~/.ssh/config <<'EOF'
Host tsh-vps
    HostName 167.71.39.50
    User root
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
```

#### 3. الاتصال بالسيرفر
1. افتح VS Code
2. اضغط `F1` → `Remote-SSH: Connect to Host`
3. اختر `tsh-vps`
4. سيفتح VS Code متصلاً بالسيرفر

#### 4. تثبيت Claude Code على السيرفر
```bash
# On the server (inside VS Code terminal)
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

#### 5. تشغيل Claude Code
```bash
# Inside VS Code terminal connected to server
cd /root/TSH_ERP
claude
```

### المزايا:
- ✅ التطوير مباشرة على السيرفر
- ✅ لا حاجة لـ rsync/scp
- ✅ التغييرات فورية
- ✅ استخدام كامل موارد السيرفر

### العيوب:
- ❌ يتطلب تثبيت Claude Code على السيرفر
- ❌ يتطلب اتصال إنترنت مستقر
- ❌ قد يكون بطيئاً مع Latency عالية

---

## 🔧 طريقة 3: Claude Code CLI على السيرفر
## Method 3: Claude Code CLI Directly on Server

**المبدأ:** تشغيل Claude Code مباشرة من terminal السيرفر.

### الخطوات:

#### 1. تثبيت Node.js على السيرفر
```bash
ssh root@167.71.39.50

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Verify
node --version  # Should be v20.x
npm --version
```

#### 2. تثبيت Claude Code
```bash
# On server
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
```

#### 3. إعداد API Key
```bash
# On server
export ANTHROPIC_API_KEY="your-api-key"

# Or add to ~/.bashrc
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.bashrc
source ~/.bashrc
```

#### 4. تشغيل Claude Code
```bash
# Navigate to project
cd /root/TSH_ERP

# Start Claude Code
claude

# Now you can interact with Claude directly on the server!
```

### المزايا:
- ✅ تطوير مباشر على السيرفر
- ✅ لا Latency
- ✅ استخدام موارد السيرفر
- ✅ مفيد للمهام الثقيلة

### العيوب:
- ❌ يتطلب SSH session نشط
- ❌ إذا انقطع الاتصال، تفقد الجلسة
- ❌ يستهلك موارد السيرفر

---

## 📱 طريقة 4: tmux + SSH Session (للجلسات الطويلة)
## Method 4: tmux for Persistent Sessions

**المبدأ:** استخدام tmux للحفاظ على جلسة Claude Code حتى لو انقطع SSH.

### الخطوات:

#### 1. تثبيت tmux على السيرفر
```bash
ssh root@167.71.39.50
apt-get update
apt-get install -y tmux
```

#### 2. إنشاء tmux session
```bash
# Start new session
tmux new -s claude-dev

# Inside tmux, start Claude Code
cd /root/TSH_ERP
claude
```

#### 3. Detach من الجلسة
```bash
# Press: Ctrl+B then D
# Session continues running in background
```

#### 4. العودة للجلسة لاحقاً
```bash
# SSH back to server
ssh root@167.71.39.50

# Reattach to session
tmux attach -t claude-dev

# Your Claude Code session is still there! 🎉
```

#### tmux أوامر مهمة:

| الأمر | الوظيفة |
|-------|---------|
| `Ctrl+B D` | Detach من الجلسة |
| `tmux ls` | قائمة الجلسات |
| `tmux attach -t <name>` | العودة للجلسة |
| `tmux kill-session -t <name>` | حذف جلسة |
| `Ctrl+B C` | نافذة جديدة |
| `Ctrl+B N` | النافذة التالية |
| `Ctrl+B P` | النافذة السابقة |

### المزايا:
- ✅ الجلسة تستمر حتى بعد انقطاع SSH
- ✅ يمكن العودة من أي مكان
- ✅ مفيد للمهام الطويلة
- ✅ تعدد النوافذ

### العيوب:
- ❌ يتطلب تعلم tmux
- ❌ يستهلك موارد السيرفر باستمرار

---

## 🎯 الخيار الموصى به / Recommended Approach

### للتطوير اليومي: **طريقة 1** ✅

**استخدم Claude Code محلياً مع SSH commands**

**لماذا؟**
- ✅ **الأسرع**: لا Latency
- ✅ **الأسهل**: لا تثبيت إضافي
- ✅ **الأكثر موثوقية**: يعمل حتى مع انقطاع إنترنت متقطع
- ✅ **الأفضل للأداء**: جهازك أسرع من السيرفر
- ✅ **هذا ما تفعله حالياً!**

### للمهام الثقيلة: **طريقة 3 + طريقة 4** 🔧

**Claude Code على السيرفر مع tmux**

**متى؟**
- بناء مشاريع كبيرة
- معالجة بيانات ضخمة
- مهام تستغرق ساعات
- عندما تحتاج موارد السيرفر

---

## 📝 سير العمل الموصى به / Recommended Workflow

### السيناريو العادي:

```bash
# 1. على جهازك المحلي
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# 2. افتح Claude Code
claude

# 3. اطلب من Claude تنفيذ مهام على السيرفر
"please check TDS Core status on the server"
"please deploy the updated API to production"
"please restart the services on the server"

# Claude سيستخدم ssh/scp/rsync تلقائياً! ✅
```

### السيناريو المتقدم (عمل طويل):

```bash
# 1. اتصل بالسيرفر
ssh root@167.71.39.50

# 2. ابدأ tmux session
tmux new -s deploy-tds

# 3. شغّل Claude Code
cd /opt/tds_core
claude

# 4. اطلب مهام طويلة
"deploy TDS Core completely with all services"
"run full database migration"
"setup monitoring dashboard"

# 5. Detach (Ctrl+B D) وأغلق الـ SSH
# العمل يستمر على السيرفر!

# 6. العودة لاحقاً
ssh root@167.71.39.50
tmux attach -t deploy-tds
# كل شيء ما زال يعمل! 🎉
```

---

## 🔐 نصائح أمنية / Security Tips

### 1. لا تضع API Key على السيرفر
```bash
# ❌ DON'T: Store API key on server in plain text
export ANTHROPIC_API_KEY="sk-..."

# ✅ DO: Use it locally and SSH for remote commands
# Your local Claude Code → SSH → Server
```

### 2. استخدم SSH Keys
```bash
# Generate SSH key (if not exists)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to server
ssh-copy-id root@167.71.39.50

# Now you can SSH without password! ✅
```

### 3. قيّد وصول SSH
```bash
# On server: /etc/ssh/sshd_config
PermitRootLogin prohibit-password  # No password login
PasswordAuthentication no          # Keys only
AllowUsers deploy                  # Specific users only
```

---

## 🧪 اختبار الإعداد / Testing Your Setup

### Test 1: Local Claude Code
```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
claude
# Ask: "What is this project about?"
```

### Test 2: SSH from Claude
```bash
# In Claude Code, ask:
"please run 'hostname' command on server 167.71.39.50"
# Should return server hostname
```

### Test 3: File Transfer
```bash
# In Claude Code, ask:
"please create a test file test.txt and upload it to /tmp/ on the server"
# Should use scp/rsync
```

### Test 4: Remote Execution
```bash
# In Claude Code, ask:
"please check what services are running on the server"
# Should run: ssh root@167.71.39.50 "systemctl list-units --type=service --state=running"
```

---

## 🚨 استكشاف الأخطاء / Troubleshooting

### Problem 1: SSH Connection Refused

```bash
# Test connection
ping 167.71.39.50

# Check SSH service
ssh -v root@167.71.39.50

# Check firewall
ssh root@167.71.39.50 "ufw status"
```

### Problem 2: Claude Code Not Found on Server

```bash
# Check Node.js
ssh root@167.71.39.50 "which node"

# Check npm
ssh root@167.71.39.50 "which npm"

# Reinstall Claude Code
ssh root@167.71.39.50 "npm install -g @anthropic-ai/claude-code"
```

### Problem 3: tmux Session Lost

```bash
# List all sessions
ssh root@167.71.39.50 "tmux ls"

# If exists, attach
ssh root@167.71.39.50 "tmux attach -t claude-dev"

# If crashed, check server logs
ssh root@167.71.39.50 "journalctl -xe"
```

### Problem 4: Slow SSH Connection

```bash
# Add to ~/.ssh/config
Host tsh-vps
    Compression yes
    TCPKeepAlive yes
    ServerAliveInterval 60

# Use SSH multiplexing
ControlMaster auto
ControlPath ~/.ssh/sockets/%r@%h-%p
ControlPersist 600
```

---

## 📊 مقارنة الطرق / Methods Comparison

| الميزة | طريقة 1 (محلي+SSH) | طريقة 2 (VS Code) | طريقة 3 (CLI) | طريقة 4 (tmux) |
|--------|---------------------|-------------------|---------------|----------------|
| **السهولة** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **السرعة** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **الموثوقية** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **موارد السيرفر** | ⭐⭐⭐⭐⭐ (لا) | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Latency** | ✅ منخفض | ⚠️ متوسط | ✅ صفر | ✅ صفر |
| **للمبتدئين** | ✅ مثالي | ✅ جيد | ⚠️ متوسط | ❌ صعب |
| **للمتقدمين** | ✅ ممتاز | ✅ ممتاز | ✅ ممتاز | ✅ ممتاز |

---

## 🎓 الخلاصة / Summary

### ✅ ما تفعله حالياً هو الأفضل!

**أنت تستخدم طريقة 1**: Claude Code محلياً مع SSH للسيرفر

**هذا مثالي لأنه:**
- سريع وسلس
- لا يستهلك موارد السيرفر
- لا يتطلب تثبيت إضافي
- يعمل بشكل ممتاز

### 📚 متى تستخدم الطرق الأخرى؟

- **طريقة 2 (VS Code Remote)**: عند الحاجة لتطوير مباشر على السيرفر
- **طريقة 3 (CLI)**: عند الحاجة لموارد السيرفر
- **طريقة 4 (tmux)**: للمهام التي تستغرق ساعات

### 🚀 نصيحة نهائية:

**استمر بما تفعله! ✅**

لكن احتفظ بـ tmux كخيار احتياطي للمهام الطويلة مثل:
- نشر TDS Core كاملاً
- ترحيل قاعدة بيانات كبيرة
- بناء مشاريع ضخمة

---

**آخر تحديث:** 2025-10-31
**المؤلف:** Khaleel Al-Mulla
**الحالة:** ✅ جاهز للاستخدام
