#!/bin/bash

################################################################################
# Docker Setup Validation Script
# TSH ERP System
################################################################################
#
# This script validates that all Docker improvements are properly configured
#
# Usage:
#   ./scripts/validate_docker_setup.sh
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNINGS++))
}

check_file() {
    if [ -f "$1" ]; then
        log_pass "File exists: $1"
        return 0
    else
        log_fail "File missing: $1"
        return 1
    fi
}

check_pattern() {
    if grep -q "$2" "$1" 2>/dev/null; then
        log_pass "$3"
        return 0
    else
        log_fail "$3"
        return 1
    fi
}

################################################################################
# Validation Tests
################################################################################

echo ""
echo "=========================================="
echo "   Docker Setup Validation"
echo "=========================================="
echo ""

log_info "Starting validation of Docker improvements..."
echo ""

# Test 1: Check docker-compose.yml exists
log_info "Test 1: Core Configuration Files"
check_file "docker-compose.yml"
check_file "docker-compose.dev.yml"
check_file "Dockerfile"
check_file ".dockerignore"
echo ""

# Test 2: Redis volume persistence
log_info "Test 2: Redis Volume Persistence"
if check_pattern "docker-compose.yml" "redis_data:/data" "Redis volume mounted"; then
    check_pattern "docker-compose.yml" "redis_data:" "Redis volume defined in volumes section"
fi
echo ""

# Test 3: Resource limits
log_info "Test 3: Resource Limits"
check_pattern "docker-compose.yml" "limits:" "Resource limits configured"
check_pattern "docker-compose.yml" "cpus:" "CPU limits set"
check_pattern "docker-compose.yml" "memory:" "Memory limits set"
echo ""

# Test 4: Non-root user in Dockerfile
log_info "Test 4: Security - Non-root User"
check_pattern "Dockerfile" "useradd.*appuser" "Non-root user created"
check_pattern "Dockerfile" "USER appuser" "Running as non-root user"
echo ""

# Test 5: Dynamic worker count
log_info "Test 5: Dynamic Worker Configuration"
check_pattern "Dockerfile" '\${UVICORN_WORKERS}' "Worker count uses environment variable"
echo ""

# Test 6: Nginx volume mounts
log_info "Test 6: Nginx Static File Serving"
check_pattern "docker-compose.yml" "./uploads:/app/uploads" "Uploads volume mounted for nginx"
check_pattern "docker-compose.yml" "./static:/app/static" "Static files volume mounted for nginx"
echo ""

# Test 7: Image versioning
log_info "Test 7: Image Versioning"
check_pattern "docker-compose.yml" "tsh-erp:\${VERSION:-latest}" "Image versioning configured"
check_pattern "docker-compose.yml" "tags:" "Build tags specified"
echo ""

# Test 8: Backup scripts
log_info "Test 8: Backup and Restore Scripts"
if check_file "scripts/docker_backup.sh"; then
    if [ -x "scripts/docker_backup.sh" ]; then
        log_pass "Backup script is executable"
    else
        log_warn "Backup script exists but not executable"
    fi
fi

if check_file "scripts/docker_restore.sh"; then
    if [ -x "scripts/docker_restore.sh" ]; then
        log_pass "Restore script is executable"
    else
        log_warn "Restore script exists but not executable"
    fi
fi
echo ""

# Test 9: SSL scripts and documentation
log_info "Test 9: SSL Configuration"
check_file "scripts/generate_self_signed_cert.sh"
check_file "docs/docker/SSL_SETUP.md"

if [ -d "nginx/ssl" ]; then
    log_pass "SSL directory exists"
    if [ -f "nginx/ssl/fullchain.pem" ] && [ -f "nginx/ssl/privkey.pem" ]; then
        log_pass "SSL certificates present"
    else
        log_warn "SSL certificates not configured (expected for fresh setup)"
    fi
else
    log_warn "SSL directory doesn't exist yet"
fi
echo ""

# Test 10: Documentation
log_info "Test 10: Documentation"
check_file "docs/docker/README.md"
check_file "docs/deployment/DEPLOYMENT_STRATEGY.md"
check_file "DOCKER_IMPROVEMENTS_SUMMARY.md"
echo ""

# Test 11: .dockerignore optimization
log_info "Test 11: .dockerignore Optimization"
if [ -f ".dockerignore" ]; then
    LINES=$(wc -l < .dockerignore)
    if [ "$LINES" -gt 100 ]; then
        log_pass ".dockerignore is comprehensive ($LINES lines)"
    else
        log_warn ".dockerignore might need more entries ($LINES lines)"
    fi

    check_pattern ".dockerignore" "deployment/" "Deployment directory excluded"
    check_pattern ".dockerignore" "secrets/" "Secrets directory excluded"
fi
echo ""

# Test 12: Compose file validation
log_info "Test 12: Docker Compose Syntax"
if command -v docker &> /dev/null; then
    if docker compose config > /dev/null 2>&1; then
        log_pass "Docker Compose syntax is valid"
    else
        log_fail "Docker Compose syntax has errors"
        echo "  Run: docker compose config"
    fi
else
    log_warn "Docker not installed, skipping syntax check"
fi
echo ""

# Test 13: Environment files
log_info "Test 13: Environment Configuration"
if [ -f ".env" ] || [ -f ".env.dev" ] || [ -f ".env.production" ]; then
    log_warn "Environment files found (good, but ensure they're git-ignored)"
else
    log_warn "No environment files found (create from config/env.example)"
fi

if [ -f "config/env.example" ]; then
    log_pass "Environment template exists"
else
    log_warn "Environment template missing"
fi
echo ""

# Test 14: Directory structure
log_info "Test 14: Required Directories"
DIRS=("logs" "uploads" "backups" "nginx" "scripts")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        log_pass "Directory exists: $dir/"
    else
        log_warn "Directory missing: $dir/ (will be created automatically)"
    fi
done
echo ""

################################################################################
# Summary
################################################################################

echo ""
echo "=========================================="
echo "   Validation Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}Passed:${NC}   $PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC}   $FAILED"
echo ""

# Overall result
if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ All checks passed! Docker setup is production-ready.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Setup is good but has $WARNINGS warnings. Review above.${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ Found $FAILED critical issues. Please fix before deploying.${NC}"
    exit 1
fi
