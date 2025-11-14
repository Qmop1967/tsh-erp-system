#!/bin/bash
#
# Bump Version Script - TSH ERP Ecosystem
# Manages semantic versioning for Claude Code configuration
#
# Usage: ./bump-version.sh [major|minor|patch] "Change description"
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLAUDE_FILE=".claude/CLAUDE.md"
STATE_FILE=".claude/state/current-phase.json"
MCP_FILE=".claude/.mcp.json"

# Parse arguments
if [ $# -lt 2 ]; then
  echo "Usage: $0 [major|minor|patch] \"Change description\""
  echo ""
  echo "Examples:"
  echo "  $0 patch \"Fixed typo in documentation\""
  echo "  $0 minor \"Added new feature tracking\""
  echo "  $0 major \"Complete configuration restructure\""
  exit 1
fi

BUMP_TYPE=$1
CHANGE_DESC=$2

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
  echo -e "${RED}✗${NC} Invalid bump type: $BUMP_TYPE"
  echo "  Must be one of: major, minor, patch"
  exit 1
fi

# Helper functions
log_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
  echo -e "${GREEN}✓${NC} $1"
}

log_error() {
  echo -e "${RED}✗${NC} $1"
}

# Check if files exist
for file in "$CLAUDE_FILE" "$STATE_FILE" "$MCP_FILE"; do
  if [ ! -f "$file" ]; then
    log_error "Required file not found: $file"
    exit 1
  fi
done

log_info "Starting version bump: $BUMP_TYPE"
echo ""

# Get current version from CLAUDE.md
CURRENT_VERSION=$(grep "^\*\*Version:\*\*" "$CLAUDE_FILE" | sed 's/\*\*Version:\*\* //' | xargs)

if [ -z "$CURRENT_VERSION" ]; then
  log_error "Could not find current version in $CLAUDE_FILE"
  exit 1
fi

log_info "Current version: $CURRENT_VERSION"

# Parse version
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

# Bump version
case "$BUMP_TYPE" in
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  patch)
    PATCH=$((PATCH + 1))
    ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
CURRENT_DATE=$(date +%Y-%m-%d)

log_success "New version: $NEW_VERSION"
echo ""

# Update CLAUDE.md
log_info "Updating CLAUDE.md..."

# Update version header
sed -i.bak "s/^\*\*Version:\*\* .*$/\*\*Version:\*\* $NEW_VERSION/" "$CLAUDE_FILE"
sed -i.bak "s/^\*\*Last Updated:\*\* .*$/\*\*Last Updated:\*\* $CURRENT_DATE/" "$CLAUDE_FILE"

# Add to version history
VERSION_HISTORY_LINE=$(grep -n "^v[0-9]\+\.[0-9]\+\.[0-9]\+ (" "$CLAUDE_FILE" | head -1 | cut -d: -f1)

if [ -n "$VERSION_HISTORY_LINE" ]; then
  # Create new version entry
  NEW_ENTRY="v$NEW_VERSION ($CURRENT_DATE):\n  - $CHANGE_DESC\n"
  sed -i.bak "${VERSION_HISTORY_LINE}i\\
$NEW_ENTRY" "$CLAUDE_FILE"
else
  log_error "Could not find version history section"
fi

log_success "Updated CLAUDE.md"

# Update state file
log_info "Updating state file..."

python3 << EOF
import json
from datetime import datetime

# Load state
with open('$STATE_FILE', 'r') as f:
    state = json.load(f)

# Update last_updated
state['last_updated'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
state['updated_by'] = 'bump-version.sh'

# Add to change log
if 'change_log' not in state:
    state['change_log'] = []

state['change_log'].insert(0, {
    'version': '$NEW_VERSION',
    'date': '$CURRENT_DATE',
    'changes': ['$CHANGE_DESC'],
    'bump_type': '$BUMP_TYPE'
})

# Keep only last 10 entries
state['change_log'] = state['change_log'][:10]

# Save
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print("State file updated")
EOF

log_success "Updated state file"

# Update MCP file
log_info "Updating MCP configuration..."

python3 << EOF
import json
from datetime import datetime

# Load MCP config
with open('$MCP_FILE', 'r') as f:
    mcp = json.load(f)

# Update last_updated
mcp['last_updated'] = '$CURRENT_DATE'

# Add to change log if MCP-related change
if any(keyword in '$CHANGE_DESC'.lower() for keyword in ['mcp', 'server', 'integration']):
    if 'change_log' not in mcp:
        mcp['change_log'] = []

    mcp['change_log'].insert(0, {
        'version': '$NEW_VERSION',
        'date': '$CURRENT_DATE',
        'changes': ['$CHANGE_DESC']
    })

    # Keep only last 10 entries
    mcp['change_log'] = mcp['change_log'][:10]

# Save
with open('$MCP_FILE', 'w') as f:
    json.dump(mcp, f, indent=2)

print("MCP config updated")
EOF

log_success "Updated MCP configuration"

# Clean up backup files
rm -f "${CLAUDE_FILE}.bak"

# Summary
echo ""
log_info "Version Bump Summary:"
echo "  📌 Old Version: $CURRENT_VERSION"
echo "  📌 New Version: $NEW_VERSION"
echo "  📝 Change: $CHANGE_DESC"
echo "  📅 Date: $CURRENT_DATE"
echo ""
echo "  Files Updated:"
echo "    ✓ $CLAUDE_FILE"
echo "    ✓ $STATE_FILE"
echo "    ✓ $MCP_FILE"

echo ""
log_success "Version bump complete!"
log_info "Don't forget to commit these changes:"
echo ""
echo "  git add $CLAUDE_FILE $STATE_FILE $MCP_FILE"
echo "  git commit -m \"chore: bump version to $NEW_VERSION\""
echo ""
