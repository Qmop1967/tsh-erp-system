#!/bin/bash
# Orixoon Pre-Deployment Testing Orchestrator
# Runs all test phases in sequence
# Blocks deployment on critical failures, allows warnings
# Supports auto-healing mode

set -e  # Exit on error (but we handle this ourselves)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse command line arguments
AUTO_HEAL=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto-heal)
            AUTO_HEAL=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "Orixoon Pre-Deployment Testing Orchestrator"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --auto-heal    Enable automatic healing of detected issues"
            echo "  --dry-run      Dry run mode (show what would be healed without doing it)"
            echo "  --help         Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$AGENT_DIR")")"

# Create report directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="$AGENT_DIR/reports/$TIMESTAMP"
mkdir -p "$REPORT_DIR"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   🚀 Orixoon Pre-Deployment Testing${NC}"
if [ "$AUTO_HEAL" = true ]; then
    echo -e "${CYAN}   🔧 Auto-Healing: ENABLED${NC}"
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}   ⚠️  Dry Run Mode: ON (no changes will be made)${NC}"
    fi
fi
echo -e "${BLUE}   Report: $REPORT_DIR${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env.production" ]; then
    echo -e "${BLUE}Loading environment from .env.production${NC}"
    export $(grep -v '^#' "$PROJECT_ROOT/.env.production" | xargs)
fi

# Set Python path
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Track overall status
OVERALL_STATUS=0
CRITICAL_FAILURES=0
WARNINGS=0

# Function to run a test phase
run_phase() {
    local phase_num=$1
    local phase_name=$2
    local script_name=$3
    local is_critical=$4  # "critical" or "warning"

    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Phase $phase_num: $phase_name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

    # Run the script
    if python3 "$SCRIPT_DIR/$script_name" > "$REPORT_DIR/$script_name.json" 2>&1; then
        echo -e "${GREEN}✅ $phase_name: PASSED${NC}"
        return 0
    else
        EXIT_CODE=$?

        if [ "$is_critical" = "critical" ]; then
            echo -e "${RED}❌ $phase_name: FAILED (CRITICAL)${NC}"
            CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
            OVERALL_STATUS=1
            return 1
        else
            echo -e "${YELLOW}⚠️  $phase_name: FAILED (WARNING)${NC}"
            WARNINGS=$((WARNINGS + 1))
            return 2
        fi
    fi
}

# Phase 1: Pre-Flight Checks (CRITICAL)
run_phase 1 "Pre-Flight Checks" "01_pre_flight_check.py" "critical"
if [ $? -eq 1 ]; then
    echo -e "\n${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}   ❌ PRE-FLIGHT CHECKS FAILED${NC}"
    echo -e "${RED}   Deployment BLOCKED${NC}"
    echo -e "${RED}   Check report: $REPORT_DIR/01_pre_flight_check.py.json${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    exit 1
fi

# Phase 2: Service Health (CRITICAL) - with auto-healing support
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Phase 2: Service Health${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Build command with auto-heal flags if enabled
HEALTH_CMD="python3 $SCRIPT_DIR/02_service_health.py"
if [ "$AUTO_HEAL" = true ]; then
    HEALTH_CMD="$HEALTH_CMD --auto-heal"
    if [ "$DRY_RUN" = true ]; then
        HEALTH_CMD="$HEALTH_CMD --dry-run"
    fi
fi

# Run service health check
if $HEALTH_CMD > "$REPORT_DIR/02_service_health.json" 2>&1; then
    echo -e "${GREEN}✅ Service Health: PASSED${NC}"
else
    EXIT_CODE=$?
    echo -e "${RED}❌ Service Health: FAILED${NC}"
    CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
    OVERALL_STATUS=1

    echo -e "\n${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}   ❌ SERVICE HEALTH CHECKS FAILED${NC}"
    echo -e "${RED}   Deployment BLOCKED${NC}"
    echo -e "${RED}   Check report: $REPORT_DIR/02_service_health.py.json${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    exit 1
fi

# Phase 3: Database Validation (CRITICAL)
run_phase 3 "Database Validation" "03_database_validator.py" "critical"
if [ $? -eq 1 ]; then
    echo -e "\n${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}   ❌ DATABASE VALIDATION FAILED${NC}"
    echo -e "${RED}   Deployment BLOCKED${NC}"
    echo -e "${RED}   Check report: $REPORT_DIR/03_database_validator.py.json${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    exit 1
fi

# Phase 4: BFF Endpoint Validation (WARNING)
run_phase 4 "BFF Endpoint Validation" "04_bff_validator.py" "warning"

# Phase 5: Zoho Integration Test (WARNING)
run_phase 5 "Zoho Integration Test" "05_zoho_integration_test.py" "warning"

# Phase 6: Flutter API Tests (CRITICAL)
run_phase 6 "Flutter API Tests" "06_flutter_api_tester.py" "critical"
if [ $? -eq 1 ]; then
    echo -e "\n${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}   ❌ FLUTTER API TESTS FAILED${NC}"
    echo -e "${RED}   Deployment BLOCKED${NC}"
    echo -e "${RED}   Check report: $REPORT_DIR/06_flutter_api_tester.py.json${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    exit 1
fi

# Phase 7: Visual Price Verification (WARNING - requires MCP)
run_phase 7 "Visual Price Verification" "07_visual_price_verify.py" "warning"

# Phase 8: E2E Workflows (WARNING)
run_phase 8 "End-to-End Workflows" "08_e2e_workflows.py" "warning"

# Phase 9: Performance Baseline (WARNING)
run_phase 9 "Performance Baseline" "09_performance_baseline.py" "warning"

# Phase 10: Post-Deployment Verification (WARNING for now)
run_phase 10 "Post-Deployment Verification" "10_post_deploy_verify.py" "warning"

# Generate summary report
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   📊 ORIXOON TEST SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

if [ $CRITICAL_FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All critical tests PASSED${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS warning(s) detected${NC}"
        echo -e "${GREEN}Deployment ALLOWED with warnings${NC}"
    else
        echo -e "${GREEN}Deployment ALLOWED${NC}"
    fi
else
    echo -e "${RED}❌ $CRITICAL_FAILURES critical failure(s)${NC}"
    echo -e "${RED}Deployment BLOCKED${NC}"
fi

echo -e "\n${BLUE}Full report available in: $REPORT_DIR${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

# Exit with appropriate code
if [ $OVERALL_STATUS -eq 0 ]; then
    exit 0
else
    exit 1
fi
