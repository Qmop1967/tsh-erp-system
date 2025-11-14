#!/bin/bash
#
# Validate State Script - TSH ERP Ecosystem
# Validates .claude/state/current-phase.json structure and content
#
# Usage: ./validate-state.sh [--verbose]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STATE_FILE=".claude/state/current-phase.json"
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose|-v)
      VERBOSE=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--verbose]"
      echo ""
      echo "Options:"
      echo "  --verbose, -v   Show detailed validation output"
      echo "  --help, -h      Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Helper functions
log_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
  echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
  echo -e "${RED}✗${NC} $1"
}

log_verbose() {
  if [ "$VERBOSE" = true ]; then
    echo -e "  ${NC}→${NC} $1"
  fi
}

# Track validation results
VALIDATION_PASSED=true
ERROR_COUNT=0
WARNING_COUNT=0

# Check if file exists
if [ ! -f "$STATE_FILE" ]; then
  log_error "State file not found: $STATE_FILE"
  exit 1
fi

log_info "Validating state file: $STATE_FILE"
echo ""

# 1. Validate JSON syntax
log_info "Checking JSON syntax..."
if python3 -c "import json; json.load(open('$STATE_FILE'))" 2>/dev/null; then
  log_success "JSON syntax is valid"
else
  log_error "Invalid JSON syntax"
  VALIDATION_PASSED=false
  ((ERROR_COUNT++))
  exit 1
fi

# 2. Validate required fields using Python
log_info "Checking required fields..."

VALIDATION_RESULT=$(python3 << 'EOF'
import json
import sys
from datetime import datetime

# Load state
with open('.claude/state/current-phase.json', 'r') as f:
    state = json.load(f)

# Track results
errors = []
warnings = []

# Required top-level fields
required_fields = [
    'schema_version',
    'last_updated',
    'updated_by',
    'project_phase',
    'phase_constraints',
    'integration_status',
    'phase_success_criteria',
    'deployment_status',
    'feature_flags',
    'scale_metrics',
    'technical_stack',
    'next_milestones',
    'change_log'
]

for field in required_fields:
    if field not in state:
        errors.append(f"Missing required field: {field}")

# Validate project_phase structure
if 'project_phase' in state:
    phase_fields = ['name', 'version', 'status', 'phase_description', 'can_write_to_zoho']
    for field in phase_fields:
        if field not in state['project_phase']:
            errors.append(f"Missing project_phase.{field}")

# Validate integration_status
if 'integration_status' in state:
    required_integrations = ['zoho_books', 'zoho_inventory', 'tds_core']
    for integration in required_integrations:
        if integration not in state['integration_status']:
            warnings.append(f"Missing integration: {integration}")

# Validate deployment_status
if 'deployment_status' in state:
    if 'environments' in state['deployment_status']:
        required_envs = ['production', 'staging']
        for env in required_envs:
            if env not in state['deployment_status']['environments']:
                errors.append(f"Missing environment: {env}")

# Validate timestamps
if 'last_updated' in state:
    try:
        datetime.fromisoformat(state['last_updated'].replace('Z', '+00:00'))
    except:
        errors.append("Invalid timestamp format in last_updated")

# Validate schema version
if 'schema_version' in state:
    version = state['schema_version']
    if not version or not isinstance(version, str):
        errors.append("Invalid schema_version")

# Output results
print(f"ERRORS:{len(errors)}")
for error in errors:
    print(f"ERROR:{error}")

print(f"WARNINGS:{len(warnings)}")
for warning in warnings:
    print(f"WARNING:{warning}")
EOF
)

# Parse validation results
while IFS= read -r line; do
  if [[ $line == ERRORS:* ]]; then
    FIELD_ERROR_COUNT="${line#ERRORS:}"
    ERROR_COUNT=$((ERROR_COUNT + FIELD_ERROR_COUNT))
    if [ "$FIELD_ERROR_COUNT" -eq 0 ]; then
      log_success "All required fields present"
    fi
  elif [[ $line == ERROR:* ]]; then
    log_error "${line#ERROR:}"
    VALIDATION_PASSED=false
  elif [[ $line == WARNINGS:* ]]; then
    FIELD_WARNING_COUNT="${line#WARNINGS:}"
    WARNING_COUNT=$((WARNING_COUNT + FIELD_WARNING_COUNT))
  elif [[ $line == WARNING:* ]]; then
    log_warning "${line#WARNING:}"
  fi
done <<< "$VALIDATION_RESULT"

# 3. Validate data types and values
log_info "Checking data types and values..."

TYPE_VALIDATION=$(python3 << 'EOF'
import json

with open('.claude/state/current-phase.json', 'r') as f:
    state = json.load(f)

errors = []

# Check boolean fields
if 'project_phase' in state:
    if 'can_write_to_zoho' in state['project_phase']:
        if not isinstance(state['project_phase']['can_write_to_zoho'], bool):
            errors.append("can_write_to_zoho must be boolean")

# Check numeric fields
if 'project_phase' in state:
    if 'phase_completion_percentage' in state['project_phase']:
        pct = state['project_phase']['phase_completion_percentage']
        if not isinstance(pct, (int, float)) or pct < 0 or pct > 100:
            errors.append("phase_completion_percentage must be between 0 and 100")

# Check array fields
if 'phase_constraints' in state:
    for key, value in state['phase_constraints'].items():
        if not isinstance(value, list):
            errors.append(f"phase_constraints.{key} must be an array")

if 'next_milestones' in state:
    if not isinstance(state['next_milestones'], list):
        errors.append("next_milestones must be an array")

if 'change_log' in state:
    if not isinstance(state['change_log'], list):
        errors.append("change_log must be an array")

# Output results
print(f"ERRORS:{len(errors)}")
for error in errors:
    print(f"ERROR:{error}")
EOF
)

# Parse type validation results
TYPE_ERROR_COUNT=0
while IFS= read -r line; do
  if [[ $line == ERRORS:* ]]; then
    TYPE_ERROR_COUNT="${line#ERRORS:}"
    ERROR_COUNT=$((ERROR_COUNT + TYPE_ERROR_COUNT))
    if [ "$TYPE_ERROR_COUNT" -eq 0 ]; then
      log_success "All data types are correct"
    fi
  elif [[ $line == ERROR:* ]]; then
    log_error "${line#ERROR:}"
    VALIDATION_PASSED=false
  fi
done <<< "$TYPE_VALIDATION"

# 4. Check for consistency
log_info "Checking data consistency..."

CONSISTENCY_CHECK=$(python3 << 'EOF'
import json

with open('.claude/state/current-phase.json', 'r') as f:
    state = json.load(f)

warnings = []

# Check if feature flags match integration status
if 'integration_status' in state and 'feature_flags' in state:
    # If TDS Core is operational, relevant features should be enabled
    if state['integration_status'].get('tds_core', {}).get('status') == 'operational':
        if not state['feature_flags'].get('zoho_write_enabled', False):
            # This is actually correct for Phase 1
            pass

# Check if phase constraints match can_write_to_zoho
if 'project_phase' in state and 'phase_constraints' in state:
    can_write = state['project_phase'].get('can_write_to_zoho', False)
    constraints = str(state['phase_constraints'])

    if can_write and 'NO writes' in constraints:
        warnings.append("Inconsistency: can_write_to_zoho=true but constraints say NO writes")
    if not can_write and 'NO writes' not in constraints:
        warnings.append("Inconsistency: can_write_to_zoho=false but constraints don't mention it")

# Output results
print(f"WARNINGS:{len(warnings)}")
for warning in warnings:
    print(f"WARNING:{warning}")
EOF
)

# Parse consistency check results
while IFS= read -r line; do
  if [[ $line == WARNINGS:* ]]; then
    CONSISTENCY_WARNING_COUNT="${line#WARNINGS:}"
    WARNING_COUNT=$((WARNING_COUNT + CONSISTENCY_WARNING_COUNT))
    if [ "$CONSISTENCY_WARNING_COUNT" -eq 0 ]; then
      log_success "Data is consistent"
    fi
  elif [[ $line == WARNING:* ]]; then
    log_warning "${line#WARNING:}"
  fi
done <<< "$CONSISTENCY_CHECK"

# 5. Verbose output
if [ "$VERBOSE" = true ]; then
  echo ""
  log_info "Detailed State Information:"

  python3 << 'EOF'
import json

with open('.claude/state/current-phase.json', 'r') as f:
    state = json.load(f)

print(f"  Schema Version: {state.get('schema_version', 'N/A')}")
print(f"  Last Updated: {state.get('last_updated', 'N/A')}")
print(f"  Updated By: {state.get('updated_by', 'N/A')}")
print(f"  Phase: {state.get('project_phase', {}).get('name', 'N/A')}")
print(f"  Phase Version: {state.get('project_phase', {}).get('version', 'N/A')}")
print(f"  Phase Completion: {state.get('project_phase', {}).get('phase_completion_percentage', 'N/A')}%")
print(f"  Can Write to Zoho: {state.get('project_phase', {}).get('can_write_to_zoho', 'N/A')}")
print(f"  Total Milestones: {len(state.get('next_milestones', []))}")
print(f"  Change Log Entries: {len(state.get('change_log', []))}")
EOF
fi

# Summary
echo ""
log_info "Validation Summary:"
echo "  📋 Total Checks: 4"
echo "  ✓ Passed: $((4 - (ERROR_COUNT > 0 ? 1 : 0)))"
if [ $ERROR_COUNT -gt 0 ]; then
  echo "  ✗ Errors: $ERROR_COUNT"
fi
if [ $WARNING_COUNT -gt 0 ]; then
  echo "  ⚠ Warnings: $WARNING_COUNT"
fi

echo ""
if [ "$VALIDATION_PASSED" = true ]; then
  log_success "State file validation PASSED!"
  if [ $WARNING_COUNT -gt 0 ]; then
    log_warning "Found $WARNING_COUNT warning(s) - review recommended"
  fi
  exit 0
else
  log_error "State file validation FAILED!"
  log_error "Found $ERROR_COUNT error(s) - please fix before proceeding"
  exit 1
fi
