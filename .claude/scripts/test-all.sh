#!/bin/bash
#
# Integration Test Suite - TSH ERP Ecosystem
# Tests all Claude Code automation scripts
#
# Usage: ./test-all.sh [--verbose]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

VERBOSE=false
TESTS_PASSED=0
TESTS_FAILED=0

# Parse arguments
if [[ "$1" == "--verbose" ]]; then
  VERBOSE=true
fi

# Helper functions
log_header() {
  echo ""
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${CYAN}  $1${NC}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
}

log_test() {
  echo -e "${BLUE}►${NC} $1"
}

log_success() {
  echo -e "  ${GREEN}✓${NC} $1"
  TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_failure() {
  echo -e "  ${RED}✗${NC} $1"
  TESTS_FAILED=$((TESTS_FAILED + 1))
}

log_warning() {
  echo -e "  ${YELLOW}⚠${NC} $1"
}

log_verbose() {
  if [ "$VERBOSE" = true ]; then
    echo -e "    ${NC}→ $1${NC}"
  fi
}

# Test functions
test_files_exist() {
  log_test "Checking if all files exist..."

  local files=(
    ".claude/CLAUDE.md"
    ".claude/state/current-phase.json"
    ".claude/.mcp.json"
    ".claude/scripts/update-state.sh"
    ".claude/scripts/validate-state.sh"
    ".claude/scripts/bump-version.sh"
    ".claude/scripts/mcp-analytics.py"
    ".claude/scripts/setup-cron.sh"
    ".claude/scripts/README.md"
    ".claude/SCRIPTS_QUICK_START.md"
    ".claude/ENHANCEMENT_CHANGELOG_NOV14.md"
    ".claude/AUTOMATION_COMPLETE_SUMMARY.md"
  )

  for file in "${files[@]}"; do
    if [ -f "$file" ]; then
      log_verbose "Found: $file"
    else
      log_failure "Missing: $file"
      return 1
    fi
  done

  log_success "All required files exist"
}

test_scripts_executable() {
  log_test "Checking if scripts are executable..."

  local scripts=(
    ".claude/scripts/update-state.sh"
    ".claude/scripts/validate-state.sh"
    ".claude/scripts/bump-version.sh"
    ".claude/scripts/mcp-analytics.py"
    ".claude/scripts/setup-cron.sh"
  )

  for script in "${scripts[@]}"; do
    if [ -x "$script" ]; then
      log_verbose "Executable: $script"
    else
      log_failure "Not executable: $script"
      return 1
    fi
  done

  log_success "All scripts are executable"
}

test_json_validity() {
  log_test "Validating JSON files..."

  local json_files=(
    ".claude/state/current-phase.json"
    ".claude/.mcp.json"
  )

  for json_file in "${json_files[@]}"; do
    if python3 -m json.tool "$json_file" > /dev/null 2>&1; then
      log_verbose "Valid JSON: $json_file"
    else
      log_failure "Invalid JSON: $json_file"
      return 1
    fi
  done

  log_success "All JSON files are valid"
}

test_state_validation() {
  log_test "Running state validation..."

  if ./.claude/scripts/validate-state.sh > /dev/null 2>&1; then
    log_success "State validation passed"
  else
    log_failure "State validation failed"
    return 1
  fi
}

test_mcp_analytics() {
  log_test "Testing MCP analytics..."

  # Check if usage log exists
  if [ -f ".claude/state/mcp_usage_log.json" ]; then
    log_verbose "Usage log found"

    # Test report generation
    if python3 .claude/scripts/mcp-analytics.py --report > /dev/null 2>&1; then
      log_success "MCP analytics working"
    else
      log_failure "MCP analytics failed"
      return 1
    fi
  else
    log_warning "No usage log found (expected for new installation)"
    log_success "MCP analytics script exists and is executable"
  fi
}

test_version_tracking() {
  log_test "Checking version tracking..."

  # Check CLAUDE.md has version
  if grep -q "^\*\*Version:\*\*" .claude/CLAUDE.md; then
    VERSION=$(grep "^\*\*Version:\*\*" .claude/CLAUDE.md | sed 's/\*\*Version:\*\* //' | xargs)
    log_verbose "CLAUDE.md version: $VERSION"
  else
    log_failure "CLAUDE.md missing version header"
    return 1
  fi

  # Check state file has version
  if grep -q '"schema_version"' .claude/state/current-phase.json; then
    SCHEMA_VERSION=$(python3 -c "import json; print(json.load(open('.claude/state/current-phase.json'))['schema_version'])")
    log_verbose "State file schema: $SCHEMA_VERSION"
  else
    log_failure "State file missing schema_version"
    return 1
  fi

  # Check MCP config has version
  if grep -q '"version"' .claude/.mcp.json; then
    MCP_VERSION=$(python3 -c "import json; print(json.load(open('.claude/.mcp.json'))['version'])")
    log_verbose "MCP config version: $MCP_VERSION"
  else
    log_failure "MCP config missing version"
    return 1
  fi

  log_success "Version tracking is properly configured"
}

test_git_hook() {
  log_test "Checking Git pre-commit hook..."

  if [ -f ".git/hooks/pre-commit" ]; then
    if [ -x ".git/hooks/pre-commit" ]; then
      log_verbose "Pre-commit hook is executable"
      log_success "Git pre-commit hook is installed"
    else
      log_failure "Pre-commit hook exists but is not executable"
      return 1
    fi
  else
    log_warning "Git pre-commit hook not installed (optional)"
  fi
}

test_documentation() {
  log_test "Checking documentation completeness..."

  # Check main docs
  if [ -f ".claude/scripts/README.md" ]; then
    local readme_size=$(wc -c < ".claude/scripts/README.md")
    if [ "$readme_size" -gt 10000 ]; then
      log_verbose "README.md size: ${readme_size} bytes"
      log_success "Comprehensive documentation found"
    else
      log_warning "README.md seems incomplete"
    fi
  else
    log_failure "README.md not found"
    return 1
  fi

  # Check quick start
  if [ -f ".claude/SCRIPTS_QUICK_START.md" ]; then
    log_verbose "Quick start guide found"
  else
    log_failure "Quick start guide not found"
    return 1
  fi

  log_success "Documentation is complete"
}

test_state_structure() {
  log_test "Validating state file structure..."

  # Required top-level fields
  local required_fields=(
    "schema_version"
    "last_updated"
    "project_phase"
    "phase_constraints"
    "integration_status"
    "deployment_status"
    "feature_flags"
    "scale_metrics"
  )

  for field in "${required_fields[@]}"; do
    if python3 -c "import json, sys; data=json.load(open('.claude/state/current-phase.json')); sys.exit(0 if '$field' in data else 1)" 2>/dev/null; then
      log_verbose "Field present: $field"
    else
      log_failure "Missing required field: $field"
      return 1
    fi
  done

  log_success "State file structure is valid"
}

test_mcp_configuration() {
  log_test "Validating MCP configuration..."

  # Check for required sections
  local required_sections=(
    "mcpServers"
    "agent_mcp_requirements"
    "task_detection_rules"
    "enablement_rules"
    "token_budget"
  )

  for section in "${required_sections[@]}"; do
    if python3 -c "import json, sys; data=json.load(open('.claude/.mcp.json')); sys.exit(0 if '$section' in data else 1)" 2>/dev/null; then
      log_verbose "Section present: $section"
    else
      log_failure "Missing required section: $section"
      return 1
    fi
  done

  log_success "MCP configuration is valid"
}

# Run all tests
main() {
  log_header "TSH ERP Claude Code Automation - Integration Test Suite"

  echo "Running comprehensive tests..."
  echo ""

  # Core tests
  test_files_exist
  test_scripts_executable
  test_json_validity
  test_state_validation

  # Functionality tests
  test_mcp_analytics
  test_version_tracking
  test_git_hook

  # Documentation tests
  test_documentation

  # Structure tests
  test_state_structure
  test_mcp_configuration

  # Summary
  log_header "Test Summary"

  local total_tests=$((TESTS_PASSED + TESTS_FAILED))

  echo "  Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
  if [ $TESTS_FAILED -gt 0 ]; then
    echo "  Tests Failed: ${RED}$TESTS_FAILED${NC}"
  else
    echo "  Tests Failed: $TESTS_FAILED"
  fi
  echo "  Total Tests:  $total_tests"
  echo ""

  if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  ✓ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "🎉 Claude Code automation is fully functional!"
    echo ""
    echo "Next steps:"
    echo "  • Review quick start: cat .claude/SCRIPTS_QUICK_START.md"
    echo "  • View full docs: cat .claude/scripts/README.md"
    echo "  • Install cron job: ./.claude/scripts/setup-cron.sh install"
    echo ""
    exit 0
  else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}  ✗ SOME TESTS FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Please review the failures above and fix them."
    echo ""
    echo "For detailed output, run:"
    echo "  $0 --verbose"
    echo ""
    exit 1
  fi
}

# Run main
main
