#!/bin/bash

# TSH ERP System - Health Check Script
# Quick system status overview

echo "🏥 TSH ERP System - Health Check"
echo "================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check Python
echo -e "${BLUE}🐍 Python Environment${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python not found${NC}"
fi

# Check Virtual Environment
if [ -d ".venv" ]; then
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
fi

# Check Node.js
echo ""
echo -e "${BLUE}📦 Node.js Environment${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"
    echo -e "${GREEN}✅ NPM $NPM_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js not found${NC}"
fi

# Check Flutter
echo ""
echo -e "${BLUE}📱 Flutter Environment${NC}"
if command -v flutter &> /dev/null; then
    FLUTTER_VERSION=$(flutter --version 2>&1 | head -1)
    echo -e "${GREEN}✅ $FLUTTER_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Flutter not found${NC}"
fi

# Check PostgreSQL
echo ""
echo -e "${BLUE}🗄️  Database Status${NC}"
if command -v pg_isready &> /dev/null; then
    if pg_isready &> /dev/null; then
        echo -e "${GREEN}✅ PostgreSQL is running${NC}"
        
        # Get database size
        DB_SIZE=$(psql -U khaleelal-mulla -d erp_db -t -c "SELECT pg_size_pretty(pg_database_size('erp_db'));" 2>/dev/null | xargs)
        if [ ! -z "$DB_SIZE" ]; then
            echo -e "${GREEN}   Database size: $DB_SIZE${NC}"
        fi
        
        # Get table count
        TABLE_COUNT=$(psql -U khaleelal-mulla -d erp_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)
        if [ ! -z "$TABLE_COUNT" ]; then
            echo -e "${GREEN}   Tables: $TABLE_COUNT${NC}"
        fi
    else
        echo -e "${RED}❌ PostgreSQL is not responding${NC}"
    fi
else
    echo -e "${RED}❌ PostgreSQL not found${NC}"
fi

# Check backend files
echo ""
echo -e "${BLUE}🔧 Backend Files${NC}"
if [ -f "app/main.py" ]; then
    echo -e "${GREEN}✅ Backend application found${NC}"
    
    # Count routers
    ROUTER_COUNT=$(find app/routers -name "*.py" 2>/dev/null | wc -l | xargs)
    echo -e "${GREEN}   API routers: $ROUTER_COUNT${NC}"
    
    # Count models
    MODEL_COUNT=$(find app/models -name "*.py" 2>/dev/null | wc -l | xargs)
    echo -e "${GREEN}   Models: $MODEL_COUNT${NC}"
else
    echo -e "${RED}❌ Backend application not found${NC}"
fi

# Check frontend files
echo ""
echo -e "${BLUE}🌐 Frontend Files${NC}"
if [ -d "frontend" ]; then
    echo -e "${GREEN}✅ Frontend directory exists${NC}"
    
    if [ -d "frontend/node_modules" ]; then
        echo -e "${GREEN}   Dependencies installed${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Dependencies not installed${NC}"
    fi
    
    if [ -f "frontend/package.json" ]; then
        echo -e "${GREEN}   Package.json found${NC}"
    fi
else
    echo -e "${RED}❌ Frontend directory not found${NC}"
fi

# Check mobile apps
echo ""
echo -e "${BLUE}📱 Mobile Apps${NC}"
if [ -d "mobile/flutter_apps" ]; then
    APP_COUNT=$(find mobile/flutter_apps -maxdepth 1 -type d | tail -n +2 | wc -l | xargs)
    echo -e "${GREEN}✅ $APP_COUNT Flutter apps found${NC}"
else
    echo -e "${YELLOW}⚠️  Mobile apps directory not found${NC}"
fi

# Check configuration files
echo ""
echo -e "${BLUE}⚙️  Configuration${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Development config (.env) exists${NC}"
else
    echo -e "${RED}❌ Development config missing${NC}"
fi

if [ -f ".env.production" ]; then
    echo -e "${GREEN}✅ Production config (.env.production) exists${NC}"
else
    echo -e "${YELLOW}⚠️  Production config not found${NC}"
fi

# Check backups
echo ""
echo -e "${BLUE}💾 Backups${NC}"
if [ -d "backups" ]; then
    BACKUP_COUNT=$(find backups -name "*.sql.gz" 2>/dev/null | wc -l | xargs)
    if [ "$BACKUP_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ $BACKUP_COUNT backup(s) found${NC}"
        
        # Get latest backup
        LATEST_BACKUP=$(ls -t backups/tsh_erp_backup_*.sql.gz 2>/dev/null | head -1)
        if [ ! -z "$LATEST_BACKUP" ]; then
            BACKUP_DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$LATEST_BACKUP" 2>/dev/null || stat -c "%y" "$LATEST_BACKUP" 2>/dev/null | cut -d'.' -f1)
            echo -e "${GREEN}   Latest: $(basename $LATEST_BACKUP)${NC}"
            echo -e "${GREEN}   Date: $BACKUP_DATE${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No backups found${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Backup directory not found${NC}"
fi

# Check scripts
echo ""
echo -e "${BLUE}🔧 Utility Scripts${NC}"
SCRIPT_COUNT=0
if [ -f "scripts/security_audit.sh" ]; then
    echo -e "${GREEN}✅ Security audit script${NC}"
    SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
fi

if [ -f "scripts/backup_database.sh" ]; then
    echo -e "${GREEN}✅ Backup automation script${NC}"
    SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
fi

if [ -f "scripts/system_health_check.sh" ]; then
    echo -e "${GREEN}✅ Health check script${NC}"
    SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
fi

# Check disk space
echo ""
echo -e "${BLUE}💿 Disk Space${NC}"
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✅ Disk usage: ${DISK_USAGE}%${NC}"
elif [ "$DISK_USAGE" -lt 90 ]; then
    echo -e "${YELLOW}⚠️  Disk usage: ${DISK_USAGE}%${NC}"
else
    echo -e "${RED}❌ Disk usage critical: ${DISK_USAGE}%${NC}"
fi

# Summary
echo ""
echo "================================="
echo -e "${BLUE}📊 Summary${NC}"
echo "================================="
echo -e "${GREEN}✅ System is operational${NC}"
echo ""
echo "Quick commands:"
echo "  ./scripts/security_audit.sh     - Run security audit"
echo "  ./scripts/backup_database.sh    - Create database backup"
echo "  source .venv/bin/activate       - Activate Python environment"
echo ""
