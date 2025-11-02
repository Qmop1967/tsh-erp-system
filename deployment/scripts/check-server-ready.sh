#!/bin/bash
################################################################################
# Pre-Deployment Server Check Script
# Verifies server is ready for deployment
# Usage: ./check-server-ready.sh [server-ip]
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Server IP from argument or default
SERVER="${1:-167.71.39.50}"
USER="${2:-root}"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TSH ERP - Pre-Deployment Server Readiness Check       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Server:${NC} $SERVER"
echo -e "${BLUE}User:${NC} $USER"
echo ""

# Check counter
PASSED=0
FAILED=0
WARNINGS=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# 1. Check SSH connectivity
echo -e "\n${BLUE}[1/10] Checking SSH connectivity...${NC}"
if ssh -o ConnectTimeout=10 -o BatchMode=yes "$USER@$SERVER" "echo connected" 2>/dev/null | grep -q "connected"; then
    check_pass "SSH connection successful"
else
    check_fail "Cannot connect via SSH (ensure SSH key is set up)"
    echo -e "       ${YELLOW}Run: ssh-copy-id $USER@$SERVER${NC}"
fi

# 2. Check directory structure
echo -e "\n${BLUE}[2/10] Checking deployment directories...${NC}"
DIRS_EXIST=$(ssh "$USER@$SERVER" "
    [ -d /opt/tsh_erp/releases/blue ] && echo 'blue' || echo ''
    [ -d /opt/tsh_erp/releases/green ] && echo 'green' || echo ''
    [ -d /opt/tsh_erp/venvs ] && echo 'venvs' || echo ''
    [ -d /opt/tsh_erp/shared/env ] && echo 'env' || echo ''
    [ -d /opt/tsh_erp/bin ] && echo 'bin' || echo ''
    [ -d /opt/backups ] && echo 'backups' || echo ''
" 2>/dev/null || echo "")

if echo "$DIRS_EXIST" | grep -q "blue"; then
    check_pass "/opt/tsh_erp/releases/blue exists"
else
    check_fail "/opt/tsh_erp/releases/blue missing"
fi

if echo "$DIRS_EXIST" | grep -q "green"; then
    check_pass "/opt/tsh_erp/releases/green exists"
else
    check_fail "/opt/tsh_erp/releases/green missing"
fi

if echo "$DIRS_EXIST" | grep -q "venvs"; then
    check_pass "/opt/tsh_erp/venvs exists"
else
    check_fail "/opt/tsh_erp/venvs missing"
fi

if echo "$DIRS_EXIST" | grep -q "env"; then
    check_pass "/opt/tsh_erp/shared/env exists"
else
    check_fail "/opt/tsh_erp/shared/env missing"
fi

if echo "$DIRS_EXIST" | grep -q "bin"; then
    check_pass "/opt/tsh_erp/bin exists"
else
    check_fail "/opt/tsh_erp/bin missing"
fi

# 3. Check deployment scripts
echo -e "\n${BLUE}[3/10] Checking deployment scripts...${NC}"
SCRIPTS=$(ssh "$USER@$SERVER" "
    [ -x /opt/tsh_erp/bin/deploy.sh ] && echo 'deploy' || echo ''
    [ -x /opt/tsh_erp/bin/rollback.sh ] && echo 'rollback' || echo ''
    [ -x /opt/tsh_erp/bin/healthcheck.sh ] && echo 'healthcheck' || echo ''
" 2>/dev/null || echo "")

if echo "$SCRIPTS" | grep -q "deploy"; then
    check_pass "deploy.sh exists and is executable"
else
    check_fail "deploy.sh missing or not executable"
fi

if echo "$SCRIPTS" | grep -q "rollback"; then
    check_pass "rollback.sh exists and is executable"
else
    check_warn "rollback.sh missing or not executable"
fi

if echo "$SCRIPTS" | grep -q "healthcheck"; then
    check_pass "healthcheck.sh exists and is executable"
else
    check_warn "healthcheck.sh missing or not executable"
fi

# 4. Check Python installation
echo -e "\n${BLUE}[4/10] Checking Python...${NC}"
PYTHON_VERSION=$(ssh "$USER@$SERVER" "python3 --version 2>&1" 2>/dev/null || echo "")
if [ -n "$PYTHON_VERSION" ]; then
    check_pass "Python installed: $PYTHON_VERSION"
else
    check_fail "Python 3 not found"
fi

# 5. Check PostgreSQL
echo -e "\n${BLUE}[5/10] Checking PostgreSQL...${NC}"
PG_VERSION=$(ssh "$USER@$SERVER" "psql --version 2>&1" 2>/dev/null || echo "")
if [ -n "$PG_VERSION" ]; then
    check_pass "PostgreSQL installed: $PG_VERSION"
else
    check_fail "PostgreSQL not found"
fi

# 6. Check Nginx
echo -e "\n${BLUE}[6/10] Checking Nginx...${NC}"
NGINX_STATUS=$(ssh "$USER@$SERVER" "systemctl is-active nginx 2>&1" 2>/dev/null || echo "inactive")
if [ "$NGINX_STATUS" = "active" ]; then
    check_pass "Nginx is running"
else
    check_fail "Nginx is not running"
fi

# 7. Check Nginx upstreams
echo -e "\n${BLUE}[7/10] Checking Nginx upstream configuration...${NC}"
NGINX_UPSTREAMS=$(ssh "$USER@$SERVER" "
    [ -f /etc/nginx/upstreams/tsh_erp_blue.conf ] && echo 'blue' || echo ''
    [ -f /etc/nginx/upstreams/tsh_erp_green.conf ] && echo 'green' || echo ''
    [ -L /etc/nginx/upstreams/tsh_erp_active.conf ] && echo 'active' || echo ''
" 2>/dev/null || echo "")

if echo "$NGINX_UPSTREAMS" | grep -q "blue"; then
    check_pass "Nginx blue upstream config exists"
else
    check_fail "Nginx blue upstream config missing"
fi

if echo "$NGINX_UPSTREAMS" | grep -q "green"; then
    check_pass "Nginx green upstream config exists"
else
    check_fail "Nginx green upstream config missing"
fi

if echo "$NGINX_UPSTREAMS" | grep -q "active"; then
    check_pass "Nginx active upstream symlink exists"
else
    check_fail "Nginx active upstream symlink missing"
fi

# 8. Check systemd services
echo -e "\n${BLUE}[8/10] Checking systemd services...${NC}"
SERVICES=$(ssh "$USER@$SERVER" "
    [ -f /etc/systemd/system/tsh_erp-blue.service ] && echo 'blue' || echo ''
    [ -f /etc/systemd/system/tsh_erp-green.service ] && echo 'green' || echo ''
" 2>/dev/null || echo "")

if echo "$SERVICES" | grep -q "blue"; then
    check_pass "tsh_erp-blue.service exists"
else
    check_fail "tsh_erp-blue.service missing"
fi

if echo "$SERVICES" | grep -q "green"; then
    check_pass "tsh_erp-green.service exists"
else
    check_fail "tsh_erp-green.service missing"
fi

# 9. Check environment configuration
echo -e "\n${BLUE}[9/10] Checking environment configuration...${NC}"
ENV_FILE=$(ssh "$USER@$SERVER" "[ -f /opt/tsh_erp/shared/env/prod.env ] && echo 'exists' || echo ''" 2>/dev/null || echo "")
if [ "$ENV_FILE" = "exists" ]; then
    check_pass "Production environment file exists"
else
    check_fail "Production environment file missing (/opt/tsh_erp/shared/env/prod.env)"
fi

# 10. Check Git
echo -e "\n${BLUE}[10/10] Checking Git installation...${NC}"
GIT_VERSION=$(ssh "$USER@$SERVER" "git --version 2>&1" 2>/dev/null || echo "")
if [ -n "$GIT_VERSION" ]; then
    check_pass "Git installed: $GIT_VERSION"
else
    check_fail "Git not found"
fi

# Summary
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   Summary                                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Server is ready for deployment!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Configure GitHub Secrets (see DEPLOY_NOW.md)"
    echo "2. Push to main branch to trigger automatic deployment"
    echo "   OR"
    echo "3. Run manual deployment: ssh $USER@$SERVER 'bash /opt/tsh_erp/bin/deploy.sh main'"
    exit 0
else
    echo -e "${RED}✗ Server is NOT ready for deployment${NC}"
    echo ""
    echo -e "${YELLOW}Fix the failed checks above before deploying${NC}"
    echo -e "${YELLOW}See DEPLOY_NOW.md for setup instructions${NC}"
    exit 1
fi
