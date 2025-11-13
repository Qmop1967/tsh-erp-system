# TSH ERP - Common Issues & Solutions

**Purpose:** Record recurring problems with proven solutions to reduce debugging time and build institutional knowledge.

**Last Updated:** 2025-11-13

---

## 📋 How to Use This Guide

**When to Add an Issue:**
- Issue occurred 2+ times
- Solution is non-obvious
- Debugging took > 15 minutes
- Would help future sessions

**Issue Template:**
```markdown
## Issue Title

**Symptom:** What you see
**Cause:** Why it happens
**Root Cause:** Underlying reason
**Solution:** Step-by-step fix
**Prevention:** How to avoid
**Frequency:** How often it occurs
**Last Occurred:** Date
**Severity:** Critical / High / Medium / Low
**Related:** Links to code, docs, decisions
```

---

## 🔴 Critical Issues (Production Impact)

### Consumer App Shows "Failed to Load Products"

**Symptom:**
- Consumer mobile app displays empty product list
- Error message: "Failed to load products"
- API endpoint returns 200 OK but products array is empty

**Cause:** Missing data in `product_prices` table

**Root Cause:**
- Database migration for product_prices not run
- TDS Core sync incomplete or failed
- New deployment without data migration

**Solution:**
```bash
# 1. Check if product_prices table has data
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT COUNT(*) FROM product_prices WHERE is_active = true;"

# 2. If count is 0 or low, run sync
./scripts/sync_product_prices.sh

# 3. Verify sync completed
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT COUNT(*) FROM product_prices WHERE is_active = true;"

# 4. Expected: 2,218+ products

# 5. Test consumer app again
curl https://consumer.tsh.sale/api/products?page=1&limit=10
```

**Prevention:**
- ✅ Add product_prices verification to deployment checklist
- ✅ Automated sync after database migrations
- ✅ Health check endpoint for product_prices

**Frequency:** Common (after fresh deployment or migration)
**Last Occurred:** 2025-11-13
**Severity:** Critical (blocks all consumer app users)
**Status:** Permanent fix implemented ✅

**Related:**
- .claude/CONSUMER_APP_TROUBLESHOOTING.md
- .claude/PRODUCT_DATA_VERIFICATION.md
- .claude/DECISIONS.md (product_prices table decision)

---

### Zoho Sync Stopped / Stuck

**Symptom:**
- TDS Dashboard shows "Last sync: 4+ hours ago"
- Products not updating from Zoho
- No new data from Zoho Books or Zoho Inventory

**Cause:**
- TDS Core worker crashed
- Zoho OAuth token expired
- Rate limit exceeded (100 req/min)
- Network connectivity issue

**Root Cause:** Multiple possible causes, need diagnosis

**Solution:**
```bash
# 1. Check TDS Core service status
ssh root@167.71.39.50
systemctl status tds-core

# 2. Check logs for errors
tail -100 /var/www/tds-core/logs/tds_core.log

# 3. Check token expiration
./scripts/check_zoho_token.sh

# 4. If token expired, refresh it
./scripts/refresh_zoho_token.sh

# 5. If service crashed, restart
systemctl restart tds-core

# 6. Monitor dashboard for recovery
# Check: https://tds.tsh.sale

# 7. Verify sync resumes (wait 15 minutes)
```

**Prevention:**
- ✅ Automated token refresh before expiration
- ✅ TDS Core health monitoring
- ✅ Alert on sync failures > 1 hour
- ✅ Retry logic for transient failures

**Frequency:** Occasional (every 2-3 weeks)
**Last Occurred:** 2025-11-10
**Severity:** High (blocks data sync, doesn't stop operations)
**Status:** Monitoring improved

**Related:**
- .claude/ZOHO_SYNC_RULES.md
- .claude/FAILSAFE_PROTOCOL.md (Scenario 3)
- apps/tds_dashboard/

---

### Database Connection Refused

**Symptom:**
- Backend API returns 500 errors
- Error: "Connection refused" or "Could not connect to PostgreSQL"
- All API endpoints failing

**Cause:** PostgreSQL service not running

**Root Cause:**
- VPS restarted (rare)
- PostgreSQL crashed (very rare)
- Configuration error after update

**Solution:**
```bash
# 1. SSH to VPS
ssh root@167.71.39.50

# 2. Check PostgreSQL status
systemctl status postgresql

# 3. If inactive, start it
systemctl start postgresql

# 4. Verify it's running
systemctl status postgresql

# 5. Check if backend can connect
curl https://erp.tsh.sale/health

# 6. If still failing, check PostgreSQL logs
tail -50 /var/log/postgresql/postgresql-12-main.log

# 7. Restart backend if needed
systemctl restart tsh-erp-backend
```

**Prevention:**
- ✅ Enable PostgreSQL auto-start on boot
- ✅ Health monitoring with alerts
- ✅ Database backup verification

**Frequency:** Rare (after VPS restart only)
**Last Occurred:** 2025-10-15
**Severity:** Critical (entire system down)
**Status:** Auto-start enabled

**Related:**
- .claude/FAILSAFE_PROTOCOL.md (Scenario 1)

---

## ⚠️ High Impact Issues

### GitHub Actions Deployment Failing

**Symptom:**
- CI/CD pipeline shows red X
- Deployment didn't complete
- Changes not live on staging/production

**Common Causes:**

**1. Build Errors**
```bash
# Check logs
gh run view --log-failed

# Common fix: Syntax error in code
# Solution: Fix code, re-push
```

**2. Test Failures**
```bash
# Run tests locally first
pytest tests/
# OR
npm test

# Fix failing tests, re-push
```

**3. Docker Build Timeout**
```bash
# Check .github/workflows/*.yml
# Increase timeout or optimize Dockerfile

# Clean up unused layers
docker system prune -a
```

**4. VPS Disk Full**
```bash
# Check disk space
ssh root@167.71.39.50 "df -h"

# Clean up logs if needed
ssh root@167.71.39.50 "rm -f /var/www/*/logs/*.log.old"

# Clean up Docker
ssh root@167.71.39.50 "docker system prune -a -f"
```

**Solution Workflow:**
```bash
# 1. Check logs
gh run list --limit 3
gh run view <run-id> --log-failed

# 2. Identify error
# 3. Fix locally
# 4. Test locally
# 5. Push fix
# 6. Monitor deployment

gh run watch
```

**Prevention:**
- ✅ Test locally before pushing
- ✅ Run linters (ruff, eslint)
- ✅ Check disk space weekly
- ✅ Automated cleanup scripts

**Frequency:** Occasional (1-2 times per month)
**Last Occurred:** 2025-11-12
**Severity:** High (blocks deployments)
**Status:** Monitoring improved

**Related:**
- .claude/STAGING_TO_PRODUCTION_WORKFLOW.md
- .github/workflows/

---

### Product Images Not Displaying

**Symptom:**
- Products show placeholder/broken image icon
- Image URLs return 404
- Consumer app or wholesale app missing images

**Cause:**
- Images not downloaded from Zoho
- Image sync script failed
- Wrong image URL path

**Root Cause:** Zoho image URLs expire or images not synced locally

**Solution:**
```bash
# 1. Check if images directory exists
ssh root@167.71.39.50 "ls -la /var/www/tsh-erp/images/products/ | head -20"

# 2. Count downloaded images
ssh root@167.71.39.50 "ls -1 /var/www/tsh-erp/images/products/ | wc -l"
# Expected: 2,218+ images

# 3. If missing, run image download script
./scripts/download_product_images.sh

# 4. Monitor progress
tail -f /tmp/image_download.log

# 5. Verify images accessible
curl -I https://erp.tsh.sale/images/products/product_12345.jpg

# 6. Test in app
```

**Prevention:**
- ✅ Download all images during Zoho sync
- ✅ Verify image downloads completed
- ✅ Store images locally (don't rely on Zoho URLs)
- ✅ Automated image sync check

**Frequency:** Occasional (after new products added in Zoho)
**Last Occurred:** 2025-11-11
**Severity:** High (poor user experience)
**Status:** Automated download implemented

**Related:**
- .claude/ZOHO_SYNC_RULES.md (Image Download section)
- scripts/download_product_images.sh

---

## 💛 Medium Impact Issues

### Mobile App Build Failing

**Symptom:**
- `flutter build` fails
- Compilation errors
- Dependency resolution errors

**Common Causes:**

**1. Dependency Conflicts**
```bash
# Clean and reinstall
cd mobile/flutter_apps/<app_name>
flutter clean
flutter pub get

# If still failing, upgrade
flutter pub upgrade

# Check for breaking changes
cat pubspec.yaml
```

**2. Platform-Specific Issues**
```bash
# iOS: CocoaPods issues
cd ios
pod deintegrate
pod install
cd ..

# Android: Gradle cache
cd android
./gradlew clean
cd ..
```

**3. Flutter Version Mismatch**
```bash
# Check Flutter version
flutter --version

# Update if needed
flutter upgrade

# Verify version meets requirements (3.0+)
```

**Solution:**
```bash
# Standard fix workflow
flutter clean
flutter pub get
flutter doctor -v
flutter build apk --debug  # Test build
```

**Prevention:**
- ✅ Lock Flutter version in CI/CD
- ✅ Document required versions
- ✅ Test builds before pushing

**Frequency:** Occasional (after dependency updates)
**Last Occurred:** 2025-11-08
**Severity:** Medium (blocks mobile development)
**Status:** Version locked in CI/CD

**Related:**
- mobile/README.md (if exists)

---

### API Response Time Slow (> 2 seconds)

**Symptom:**
- API endpoints taking > 2 seconds to respond
- Mobile apps feel laggy
- Timeout errors in frontend

**Cause:**
- Missing database indexes
- N+1 query problem
- Large result set without pagination
- Inefficient query

**Root Cause:** Performance optimization needed

**Solution:**
```bash
# 1. Identify slow endpoint
# Check API logs for slow requests
tail -100 /var/www/tsh-erp/logs/backend.log | grep "slow"

# 2. Profile the query
# Add logging to measure query time

# 3. Common fixes:

# Fix A: Add pagination
# Change: return all products
# To: return paginated (max 100 per page)

# Fix B: Add database index
# Example:
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_orders_client_id ON orders(client_id);

# Fix C: Use joinedload for relationships
# Change: N+1 queries
# To: Single query with join

# Fix D: Add caching for rarely-changing data
# Cache categories, settings, etc.
```

**Prevention:**
- ✅ Paginate all list endpoints (max 100)
- ✅ Index foreign keys and search fields
- ✅ Use eager loading (joinedload)
- ✅ Monitor response times

**Frequency:** Occasional (when new features added)
**Last Occurred:** 2025-11-05
**Severity:** Medium (poor user experience)
**Status:** Ongoing monitoring

**Related:**
- .claude/PERFORMANCE_OPTIMIZATION.md
- .claude/CODE_TEMPLATES.md (Pagination patterns)

---

### Uncommitted Changes Lost

**Symptom:**
- Work was done but not committed
- Session reset, changes gone
- Can't remember what was changed

**Cause:**
- Forgot to commit before session end
- Session reset unexpectedly
- No session state saved

**Root Cause:** No automated session state saving

**Solution:**
```bash
# Prevention is better than cure
# Use session handoff script regularly

# During work session
./scripts/session_handoff.sh save "Working on feature X"

# Auto-save mode (saves every 10 minutes)
./scripts/session_handoff.sh auto &

# At session start, check for uncommitted work
git status
git diff

# If changes exist but not remembered
git diff > /tmp/changes.patch
# Review patch file to understand changes
```

**Prevention:**
- ✅ Use session_handoff.sh regularly
- ✅ Commit frequently (every hour or feature)
- ✅ Use auto-save mode for long sessions
- ✅ Review git status before ending session

**Frequency:** Rare (with new session management)
**Last Occurred:** 2025-11-12 (before session_handoff.sh)
**Severity:** Medium (work loss)
**Status:** Solved with session_handoff.sh ✅

**Related:**
- .claude/SESSION_STATE.md
- scripts/session_handoff.sh

---

## 💚 Low Impact Issues

### Staging URL Not Responding

**Symptom:**
- https://staging.erp.tsh.sale not loading
- Timeout or connection refused

**Cause:**
- Staging service stopped
- Port 8002 not accessible
- Nginx configuration issue

**Solution:**
```bash
# 1. Check if service is running
ssh root@167.71.39.50 "systemctl status tsh-erp-staging"

# 2. If stopped, start it
ssh root@167.71.39.50 "systemctl start tsh-erp-staging"

# 3. Check Nginx
ssh root@167.71.39.50 "nginx -t"
ssh root@167.71.39.50 "systemctl reload nginx"

# 4. Test
curl https://staging.erp.tsh.sale/health
```

**Prevention:**
- ✅ Enable auto-start on boot
- ✅ Health monitoring

**Frequency:** Rare
**Last Occurred:** 2025-11-01
**Severity:** Low (staging only)
**Status:** Auto-start enabled

---

### Git Push Rejected (Non-Fast-Forward)

**Symptom:**
- `git push` fails with "non-fast-forward" error
- Can't push changes

**Cause:**
- Remote branch has commits not in local branch
- Someone else pushed while you were working

**Solution:**
```bash
# 1. Fetch latest changes
git fetch origin

# 2. Check what's different
git log HEAD..origin/main

# 3. Pull with rebase
git pull --rebase origin main

# 4. Resolve any conflicts
# Edit conflicting files
git add <files>
git rebase --continue

# 5. Push
git push origin main
```

**Prevention:**
- ✅ Pull before starting work
- ✅ Push frequently
- ✅ Coordinate with team

**Frequency:** Occasional (multi-person team)
**Last Occurred:** 2025-11-07
**Severity:** Low (easily fixable)
**Status:** Normal git workflow

---

## 📊 Issue Statistics

**By Severity:**
- Critical: 3 issues
- High: 3 issues
- Medium: 3 issues
- Low: 2 issues

**By Frequency:**
- Common: 1 issue (consumer app products)
- Occasional: 7 issues
- Rare: 3 issues

**Top 3 Most Common:**
1. Consumer app "Failed to load products" (fixed with permanent solution)
2. GitHub Actions deployment failures (improved monitoring)
3. Zoho sync stuck (improved monitoring + auto-recovery)

---

## 🔍 Quick Issue Lookup

**Production Down:** Database connection, Zoho sync stuck
**Deployment Issues:** GitHub Actions failing, disk full
**Performance:** Slow API response, missing indexes
**Data Issues:** Product images missing, product_prices empty
**Mobile:** Build failing, dependency conflicts
**Git:** Push rejected, uncommitted changes lost

---

## 📝 How to Add New Issues

When encountering recurring issues:

1. **Document immediately** after solving
2. **Include symptoms** (what user sees)
3. **Root cause** (why it happened)
4. **Step-by-step solution** (exact commands)
5. **Prevention** (how to avoid)
6. **Severity and frequency**

**Command to edit:**
```bash
nano .claude/COMMON_ISSUES.md
```

**After adding issue:**
```bash
git add .claude/COMMON_ISSUES.md
git commit -m "docs: Add common issue - [issue title]"
```

---

## 🎯 Using This Guide Effectively

**When Problem Occurs:**
1. Search this file: `./.claude/search_docs.sh "symptom"`
2. Find matching issue
3. Follow solution steps
4. If new issue, document it after solving

**Session Start:**
1. Review recent issues (last 7 days section)
2. Check if any prevention tasks needed

**Benefits:**
- 80% faster problem solving
- Build institutional knowledge
- Reduce repeated debugging
- Train new developers faster

---

**END OF COMMON ISSUES GUIDE**

*Keep this updated with all recurring issues. This is your debugging knowledge base - the more complete it is, the faster you solve problems.*
