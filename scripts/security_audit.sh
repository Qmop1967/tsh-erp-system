#!/bin/bash

# TSH ERP System - Security Audit Script
# This script performs basic security checks before production deployment

echo "🔐 TSH ERP System - Security Audit"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ISSUES_FOUND=0

# Check 1: Verify .env file is not tracked by git
echo "📋 Check 1: Verifying .env security..."
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo -e "${RED}❌ CRITICAL: .env file is tracked by git!${NC}"
    echo "   Action: Remove .env from git tracking"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ .env file is not tracked by git${NC}"
fi

# Check 2: Verify SECRET_KEY is not default
echo ""
echo "📋 Check 2: Checking JWT SECRET_KEY..."
if grep -q "your-secret-key-here" .env 2>/dev/null; then
    echo -e "${RED}❌ CRITICAL: Default SECRET_KEY detected!${NC}"
    echo "   Action: Generate a strong random key"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ SECRET_KEY appears to be customized${NC}"
fi

# Check 3: Verify DEBUG is set appropriately
echo ""
echo "📋 Check 3: Checking DEBUG setting..."
if [ -f ".env.production" ]; then
    if grep -q "DEBUG=True" .env.production 2>/dev/null; then
        echo -e "${RED}❌ CRITICAL: DEBUG=True in production config!${NC}"
        echo "   Action: Set DEBUG=False for production"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ DEBUG is disabled in production config${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  WARNING: .env.production file not found${NC}"
fi

# Check 4: Check for sensitive files in git
echo ""
echo "📋 Check 4: Checking for sensitive files..."
SENSITIVE_FILES=("*.key" "*.pem" "*.p12" "*.jks" "credentials.json" "secrets.json")
for pattern in "${SENSITIVE_FILES[@]}"; do
    if git ls-files | grep -q "$pattern"; then
        echo -e "${RED}❌ WARNING: Sensitive files ($pattern) found in git${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
done
echo -e "${GREEN}✅ No obvious sensitive files in git${NC}"

# Check 5: Verify requirements.txt has pinned versions
echo ""
echo "📋 Check 5: Checking dependency versions..."
if grep -q "==" config/requirements.txt; then
    echo -e "${GREEN}✅ Dependencies have pinned versions${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: Some dependencies may not have pinned versions${NC}"
fi

# Check 6: Check for TODO or FIXME in critical files
echo ""
echo "📋 Check 6: Checking for unresolved TODOs..."
TODO_COUNT=$(grep -r "TODO\|FIXME" app/ --include="*.py" 2>/dev/null | wc -l)
if [ "$TODO_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $TODO_COUNT TODO/FIXME comments in code${NC}"
    echo "   Review and resolve critical ones before production"
else
    echo -e "${GREEN}✅ No TODO/FIXME comments found${NC}"
fi

# Check 7: Verify CORS settings
echo ""
echo "📋 Check 7: Checking CORS configuration..."
if grep -q '"http://localhost' .env.production 2>/dev/null; then
    echo -e "${RED}❌ WARNING: localhost in production CORS settings${NC}"
    echo "   Action: Update CORS_ORIGINS with production domains"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ CORS settings appear production-ready${NC}"
fi

# Check 8: Check database credentials
echo ""
echo "📋 Check 8: Checking database configuration..."
if [ -f ".env.production" ]; then
    if grep -q "username:password" .env.production; then
        echo -e "${RED}❌ CRITICAL: Default database credentials in production${NC}"
        echo "   Action: Update with actual production credentials"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ Database credentials appear customized${NC}"
    fi
fi

# Check 9: Verify SSL/HTTPS settings
echo ""
echo "📋 Check 9: Checking SSL/HTTPS configuration..."
if [ -f ".env.production" ]; then
    if grep -q "HTTPS_ONLY=True\|ENABLE_SSL=True" .env.production; then
        echo -e "${GREEN}✅ HTTPS/SSL is enabled in production config${NC}"
    else
        echo -e "${YELLOW}⚠️  WARNING: HTTPS/SSL settings not found${NC}"
    fi
fi

# Summary
echo ""
echo "=================================="
echo "📊 Security Audit Summary"
echo "=================================="
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No critical security issues found!${NC}"
    echo -e "${GREEN}System appears ready for production deployment.${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $ISSUES_FOUND security issue(s)${NC}"
    echo -e "${RED}Please address these issues before production deployment.${NC}"
    exit 1
fi
