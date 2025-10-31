#!/bin/bash

# TSH ERP System Health Check Script
# Verifies all critical components are running properly

echo "🔍 TSH ERP System Health Check"
echo "================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track overall health
HEALTH_STATUS=0

# Function to check service
check_service() {
    local service_name=$1
    local check_command=$2
    local optional=${3:-false}

    echo -n "${BLUE}$service_name:${NC} "

    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Running${NC}"
        return 0
    else
        if [ "$optional" = true ]; then
            echo -e "${YELLOW}⚠️  Not Running (Optional)${NC}"
            return 0
        else
            echo -e "${RED}❌ Not Running${NC}"
            HEALTH_STATUS=1
            return 1
        fi
    fi
}

# 1. Check PostgreSQL Database
echo "📊 Database Layer"
echo "----------------"
check_service "PostgreSQL Server" "pg_isready -U khaleelal-mulla -d erp_db"

if [ $? -eq 0 ]; then
    # Check database connection count
    CONN_COUNT=$(psql -U khaleelal-mulla -d erp_db -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='erp_db';" 2>/dev/null | xargs)
    if [ ! -z "$CONN_COUNT" ]; then
        echo "   Active Connections: $CONN_COUNT"
    fi
fi
echo ""

# 2. Check FastAPI Backend
echo "🚀 Backend Layer"
echo "----------------"
check_service "FastAPI (localhost:8000)" "curl -s http://localhost:8000/health"
check_service "FastAPI (network:8000)" "curl -s http://192.168.68.51:8000/health"

# Check if authentication endpoint works
if curl -s http://localhost:8000/api/auth/login -X OPTIONS > /dev/null 2>&1; then
    echo -e "   Auth Endpoints: ${GREEN}✅ Accessible${NC}"
else
    echo -e "   Auth Endpoints: ${RED}❌ Not Accessible${NC}"
    HEALTH_STATUS=1
fi

# Check if accounting endpoint works
if curl -s http://localhost:8000/api/accounting/currencies -X OPTIONS > /dev/null 2>&1; then
    echo -e "   Accounting API: ${GREEN}✅ Accessible${NC}"
else
    echo -e "   Accounting API: ${RED}❌ Not Accessible${NC}"
    HEALTH_STATUS=1
fi
echo ""

# 3. Check React Frontend (Optional)
echo "⚛️  Frontend Layer"
echo "----------------"
check_service "React Admin (Vite)" "curl -s http://localhost:5173" true
echo ""

# 4. Check for recent errors in logs
echo "📝 Error Logs"
echo "----------------"
if [ -d "app/logs" ]; then
    ERROR_COUNT=$(find app/logs -name "*.log" -type f -mtime -1 -exec grep -c "ERROR\|CRITICAL" {} + 2>/dev/null | awk '{s+=$1} END {print s}')
    if [ -z "$ERROR_COUNT" ]; then
        ERROR_COUNT=0
    fi

    if [ "$ERROR_COUNT" -eq 0 ]; then
        echo -e "${GREEN}✅ No errors in last 24 hours${NC}"
    else
        echo -e "${YELLOW}⚠️  $ERROR_COUNT errors found in last 24 hours${NC}"
        echo "   Run: grep -r \"ERROR\" app/logs/ | tail -n 5"
    fi
else
    echo -e "${YELLOW}⚠️  Log directory not found${NC}"
fi
echo ""

# 5. Check Python process
echo "🐍 Python Processes"
echo "----------------"
UVICORN_COUNT=$(ps aux | grep -c "[u]vicorn app.main:app")
if [ "$UVICORN_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Uvicorn processes: $UVICORN_COUNT${NC}"
else
    echo -e "${RED}❌ No Uvicorn processes running${NC}"
    HEALTH_STATUS=1
fi
echo ""

# 6. Check disk space
echo "💾 System Resources"
echo "----------------"
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "Disk Usage: ${GREEN}$DISK_USAGE%${NC}"
else
    echo -e "Disk Usage: ${YELLOW}$DISK_USAGE% (Warning: Running low)${NC}"
fi

# Check memory usage
MEMORY_USAGE=$(ps aux | awk '{sum+=$4} END {print int(sum)}')
echo "Memory Usage: ${MEMORY_USAGE}%"
echo ""

# 7. Check critical ports
echo "🔌 Port Status"
echo "----------------"
check_port() {
    local port=$1
    local service=$2

    if lsof -i:$port > /dev/null 2>&1; then
        echo -e "Port $port ($service): ${GREEN}✅ In Use${NC}"
    else
        echo -e "Port $port ($service): ${RED}❌ Not Listening${NC}"
        HEALTH_STATUS=1
    fi
}

check_port 5432 "PostgreSQL"
check_port 8000 "FastAPI"
check_port 5173 "React (Optional)" || true
echo ""

# 8. Summary
echo "================================"
if [ $HEALTH_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ System Health: GOOD${NC}"
    echo -e "${GREEN}All critical services are running properly!${NC}"
    exit 0
else
    echo -e "${RED}❌ System Health: ISSUES DETECTED${NC}"
    echo -e "${RED}Please check the services marked with ❌ above.${NC}"
    exit 1
fi
