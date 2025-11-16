#!/bin/bash
# TSH ERP - Git Worktree Creator for Parallel Claude Sessions
# Version: 1.0.0
# Usage: ./scripts/create-worktree.sh <agent> <feature> [base-branch]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
AGENT=$1
FEATURE=$2
BASE_BRANCH=${3:-develop}

# Display usage if arguments missing
if [ -z "$AGENT" ] || [ -z "$FEATURE" ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    echo "Usage: ./scripts/create-worktree.sh <agent> <feature> [base-branch]"
    echo ""
    echo "Arguments:"
    echo "  agent        - Agent type (database, api, security, testing, performance, etc.)"
    echo "  feature      - Feature name (product-catalog, order-management, etc.)"
    echo "  base-branch  - Base branch to create from (default: develop)"
    echo ""
    echo "Examples:"
    echo "  ./scripts/create-worktree.sh database product-catalog"
    echo "  ./scripts/create-worktree.sh api order-management develop"
    echo "  ./scripts/create-worktree.sh security mfa-implementation"
    echo "  ./scripts/create-worktree.sh testing e2e-coverage"
    echo ""
    exit 1
fi

# Capitalize first letter for directory name
capitalize() {
    echo "$1" | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1'
}

AGENT_CAP=$(capitalize "$AGENT")
FEATURE_CAP=$(capitalize "$FEATURE")

# Determine worktree path and branch name
WORKTREE_PATH="../TSH_ERP_${AGENT_CAP// /_}_${FEATURE_CAP// /_}"
BRANCH_NAME="${AGENT}/${FEATURE}"

# Display plan
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  TSH ERP - Creating Worktree for Parallel Session${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Agent:        $AGENT"
echo "  Feature:      $FEATURE"
echo "  Path:         $WORKTREE_PATH"
echo "  Branch:       $BRANCH_NAME"
echo "  Base Branch:  $BASE_BRANCH"
echo ""

# Check if worktree path already exists
if [ -d "$WORKTREE_PATH" ]; then
    echo -e "${RED}Error: Directory already exists: $WORKTREE_PATH${NC}"
    echo "Please remove it first or choose a different name."
    exit 1
fi

# Check if branch already exists
BRANCH_EXISTS=$(git branch --list "$BRANCH_NAME")
if [ -n "$BRANCH_EXISTS" ]; then
    echo -e "${YELLOW}Warning: Branch '$BRANCH_NAME' already exists${NC}"
    echo "Creating worktree from existing branch..."
    git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"
else
    echo -e "${GREEN}Creating new branch '$BRANCH_NAME' from '$BASE_BRANCH'...${NC}"
    git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" "$BASE_BRANCH"
fi

# Success message
echo ""
echo -e "${GREEN}✅ Worktree created successfully!${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Next Steps:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1. Navigate to worktree:"
echo -e "   ${YELLOW}cd $WORKTREE_PATH${NC}"
echo ""
echo "2. Open in VS Code:"
echo -e "   ${YELLOW}code .${NC}"
echo ""
echo "3. Start Claude Code session:"
echo -e "   ${YELLOW}claude${NC}"
echo ""
echo "4. Configure environment (if needed):"
echo -e "   ${YELLOW}cp .env.template .env${NC}"
echo -e "   ${YELLOW}# Edit .env with unique PORT and DATABASE_URL${NC}"
echo ""
echo "5. When done, push branch to GitHub:"
echo -e "   ${YELLOW}git add .${NC}"
echo -e "   ${YELLOW}git commit -m \"feat($AGENT): $FEATURE\"${NC}"
echo -e "   ${YELLOW}git push -u origin $BRANCH_NAME${NC}"
echo ""
echo "6. Clean up worktree when finished:"
echo -e "   ${YELLOW}cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem${NC}"
echo -e "   ${YELLOW}git worktree remove $WORKTREE_PATH${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# List all worktrees
echo -e "${GREEN}All Active Worktrees:${NC}"
git worktree list
echo ""
