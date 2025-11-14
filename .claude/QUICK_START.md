# TSH ERP Quick Start Hub

**Your Starting Point for TSH ERP Development**
Last Updated: November 13, 2025

---

## 🚀 Welcome to TSH ERP!

This is your central quick start hub. Choose the guide relevant to your needs:

---

## ⚠️ CRITICAL: Authorization Framework

**🔒 TSH ERP uses HYBRID AUTHORIZATION: ABAC + RBAC + RLS**

**EVERY endpoint, service, and database query MUST implement all three layers:**

1. **RBAC** (Role-Based Access Control) - "Can this role perform this action?"
2. **ABAC** (Attribute-Based Access Control) - "Do user attributes satisfy policy?"
3. **RLS** (Row-Level Security) - "Which specific rows can this user see?"

```python
# ✅ CORRECT: All three layers
@router.get("/orders")
async def get_orders(
    user: User = Depends(require_role([...])),           # RBAC
    abac: User = Depends(check_abac_permission(...)),    # ABAC
    db: Session = Depends(get_db)
):
    service = OrderService(db, user)  # RLS
    return await service.get_orders()

# ❌ WRONG: Security violation
@router.get("/orders")
async def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()  # Missing all 3 layers!
```

**📖 Detailed Documentation:**
- [AUTHORIZATION_FRAMEWORK.md](./AUTHORIZATION_FRAMEWORK.md) - Complete framework guide
- [ARCHITECTURE_RULES.md § Security Patterns](./ARCHITECTURE_RULES.md) - Implementation patterns
- [AI_CONTEXT_RULES.md § Rule 3](./AI_CONTEXT_RULES.md) - Framework context

**This framework is NON-NEGOTIABLE. All code must comply.**

---

## 📚 Core Quick Starts

### For New Developers

**[Complete Setup Guide](../docs/README.md)**
- System overview
- Architecture
- First-time setup
- Development environment

### For Backend Development

**[BFF Quick Start](../docs/guides/quick-start/BFF_QUICK_START.md)**
- Backend for Frontend pattern
- Mobile API development
- Creating new BFF endpoints

### For Frontend/Mobile Development

**[Consumer App Quick Start](../mobile/flutter_apps/10_tsh_consumer_app/QUICK_START.md)**
- Flutter web app setup
- API integration
- Building and deploying

**[Salesperson App Quick Start](../docs/reports/TSH_SALESPERSON_APP_QUICK_START.md)**
- Mobile sales app
- Field operations
- Offline capabilities

---

## 🔧 Integration Quick Starts

### Zoho Integration

**[Zoho Sync Guide](../docs/integrations/zoho/ZOHO_SYNC_GUIDE.md)**
- Setting up Zoho connection
- Webhook configuration
- MCP tools setup

**[TDS Integration](../docs/integrations/tds/TDS_INTEGRATION_GUIDE.md)**
- Data sync engine
- Queue management
- Monitoring dashboard

---

## 🏗️ Infrastructure Quick Starts

### Deployment

**[Deployment Guide](./DEPLOYMENT_GUIDE.md)** ⭐ **START HERE for deployments**
- Complete deployment workflow
- CI/CD pipeline
- Environment setup

**[Docker Quick Reference](../docs/docker/README.md)**
- Docker setup
- Container management
- Local development

### CI/CD

**[CI/CD Quickstart](../docs/ci-cd/QUICKSTART.md)**
- GitHub Actions setup
- Automated testing
- Deployment automation

---

## 🔐 Security & Auth

### Authorization Framework (REQUIRED) ⭐

**[Authorization Framework Guide](./AUTHORIZATION_FRAMEWORK.md)** 🔒 **CRITICAL - READ FIRST**
- Hybrid ABAC + RBAC + RLS model
- Implementation patterns
- Role definitions and policies
- Security best practices

### OAuth Setup

**[OAuth Update Guide](../docs/guides/quick-start/OAUTH_UPDATE_QUICKSTART.md)**
- OAuth 2.0 configuration
- Token management
- Security best practices

### MCP (Model Context Protocol)

**[MCP Quick Start](../docs/setup/MCP_QUICK_START.md)**
- Claude integration
- MCP server setup
- Available tools

---

## 📱 Mobile Apps Quick Starts

All Flutter apps have their own Quick Start guides:

| App | Location | Purpose |
|-----|----------|---------|
| **Consumer App** | `/mobile/flutter_apps/10_tsh_consumer_app/QUICK_START.md` | Customer shopping interface |
| **Salesperson App** | `/mobile/flutter_apps/06_tsh_salesperson_app/POS_QUICK_START.md` | Field sales & POS |
| **Admin App** | `/mobile/flutter_apps/01_tsh_admin_app/README.md` | Mobile ERP management |

---

## 🎯 By Use Case

### "I want to deploy to production"
→ [Deployment Guide](./DEPLOYMENT_GUIDE.md)

### "I want to add a new API endpoint"
→ [BFF Quick Start](../docs/guides/quick-start/BFF_QUICK_START.md)

### "I want to integrate with Zoho"
→ [Zoho Sync Guide](../docs/integrations/zoho/ZOHO_SYNC_GUIDE.md)

### "I want to set up CI/CD"
→ [CI/CD Quickstart](../docs/ci-cd/QUICKSTART.md)

### "I want to build the mobile app"
→ [Consumer App Quick Start](../mobile/flutter_apps/10_tsh_consumer_app/QUICK_START.md)

### "I'm new to the project"
→ Start with [Project README](../docs/README.md) then [Architecture Rules](./ARCHITECTURE_RULES.md)

---

## 🏃 30-Second Quick Starts

### Backend Developer (First Time)

```bash
# 1. Clone repo
git clone https://github.com/your-org/tsh-erp.git
cd tsh-erp

# 2. Copy environment
cp .env.example .env

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker-compose exec api alembic upgrade head

# 5. Open
open http://localhost:8000/docs
```

### Frontend Developer (First Time)

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev

# 4. Open
open http://localhost:5173
```

### Mobile Developer (First Time)

```bash
# 1. Navigate to app
cd mobile/flutter_apps/10_tsh_consumer_app

# 2. Get dependencies
flutter pub get

# 3. Run
flutter run -d chrome
```

### DevOps (First Time Deployment)

```bash
# 1. Configure secrets in GitHub
gh secret set VPS_HOST
gh secret set VPS_SSH_KEY
# ... (see Deployment Guide for full list)

# 2. Push to develop (staging)
git push origin develop

# 3. Monitor deployment
gh run watch

# 4. After staging verification, merge to main
gh pr create --base main --head develop
```

---

## 📖 Reference Documentation

### Architecture
- [Architecture Rules](./ARCHITECTURE_RULES.md) - Core principles
- [BFF Architecture](../docs/architecture/BFF_ARCHITECTURE.md) - Backend for Frontend pattern
- [Docker Deployment](./DOCKER_DEPLOYMENT_GUIDE.md) - Container architecture

### Operations
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Complete deployment reference
- [TDS Integration](../docs/integrations/tds/TDS_INTEGRATION_GUIDE.md) - Data sync
- [Zoho Sync](../docs/integrations/zoho/ZOHO_SYNC_GUIDE.md) - Zoho integration

### Development
- [Project Vision](./PROJECT_VISION.md) - Long-term goals
- [Code Templates](./CODE_TEMPLATES.md) - Boilerplate code
- [Working Together](./WORKING_TOGETHER.md) - Collaboration guide

---

## 🆘 Need Help?

### Troubleshooting
1. Check the specific guide for your task (above)
2. Review [common issues](#) in each guide's troubleshooting section
3. Search archived docs in `/archived/consolidation_2025/`

### Getting Support
- **Slack:** #tsh-erp-support
- **Issues:** GitHub Issues
- **Email:** dev-team@tsh.sale

### Contributing
See [CONTRIBUTING.md](../docs/CONTRIBUTING.md)

---

## 🗺️ Documentation Map

```
.claude/
├── QUICK_START.md              ⭐ YOU ARE HERE
├── ARCHITECTURE_RULES.md       (Core architecture)
├── DEPLOYMENT_GUIDE.md         (Deployment master guide)
└── DOCKER_DEPLOYMENT_GUIDE.md  (Docker specifics)

docs/
├── README.md                   (Project overview)
├── architecture/               (Architecture docs)
├── deployment/                 (Deployment details)
├── integrations/              (External integrations)
│   ├── tds/                   (Data sync)
│   └── zoho/                  (Zoho Books/Inventory)
├── guides/quick-start/        (Specialized quick starts)
├── ci-cd/                     (CI/CD setup)
└── security/                  (Security guides)

mobile/flutter_apps/
└── */QUICK_START.md           (App-specific guides)
```

---

## ✅ Checklist for New Team Members

**Day 1:**
- [ ] Read [Project Vision](./PROJECT_VISION.md)
- [ ] 🔒 **REQUIRED:** Read [Authorization Framework](./AUTHORIZATION_FRAMEWORK.md)
- [ ] Review [Architecture Rules](./ARCHITECTURE_RULES.md)
- [ ] Set up development environment (see 30-second quick starts above)
- [ ] Run the app locally
- [ ] Join team communication channels

**Week 1:**
- [ ] 🔒 **REQUIRED:** Implement endpoint with all 3 authorization layers (RBAC + ABAC + RLS)
- [ ] Read relevant integration guide (Zoho/TDS)
- [ ] Review [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [ ] Make first small contribution
- [ ] Attend team standup

**Month 1:**
- [ ] Understand full architecture
- [ ] Review security patterns in existing code
- [ ] Deploy to staging environment
- [ ] Contribute to production deployment
- [ ] Help update documentation

---

## 🎓 Learning Paths

### Backend Engineer Path
1. 🔒 [Authorization Framework](./AUTHORIZATION_FRAMEWORK.md) **← START HERE**
2. [Architecture Rules](./ARCHITECTURE_RULES.md)
3. [BFF Architecture](../docs/architecture/BFF_ARCHITECTURE.md)
4. [BFF Quick Start](../docs/guides/quick-start/BFF_QUICK_START.md)
5. [TDS Integration](../docs/integrations/tds/TDS_INTEGRATION_GUIDE.md)
6. [Deployment Guide](./DEPLOYMENT_GUIDE.md)

### Frontend Engineer Path
1. 🔒 [Authorization Framework](./AUTHORIZATION_FRAMEWORK.md) **← START HERE**
2. [Architecture Rules](./ARCHITECTURE_RULES.md)
3. Frontend setup (see 30-second quick start)
4. [BFF API Documentation](../docs/api/BFF_API.md)
5. Consumer/Mobile app guides
6. [Deployment Guide](./DEPLOYMENT_GUIDE.md)

### DevOps Path
1. 🔒 [Authorization Framework](./AUTHORIZATION_FRAMEWORK.md) **← START HERE**
2. [Architecture Rules](./ARCHITECTURE_RULES.md)
3. [Docker Deployment](./DOCKER_DEPLOYMENT_GUIDE.md)
4. [Deployment Guide](./DEPLOYMENT_GUIDE.md)
5. [CI/CD Quickstart](../docs/ci-cd/QUICKSTART.md)
6. [TDS Integration](../docs/integrations/tds/TDS_INTEGRATION_GUIDE.md)

---

**Remember:** This is a hub, not a comprehensive guide. Click through to the specific guides for detailed instructions!

---

**Status:** ✅ Active
**Maintainer:** Dev Team
**Last Review:** November 13, 2025
**Next Review:** February 2026
