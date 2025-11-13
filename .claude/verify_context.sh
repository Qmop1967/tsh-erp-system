#!/bin/bash
# TSH ERP Context Verification Script
# Purpose: Quick verification that all critical documentation is present and readable
# Usage: ./.claude/verify_context.sh

echo "🔍 TSH ERP Context Verification"
echo "================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(dirname "$CLAUDE_DIR")"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check critical files
CRITICAL_FILES=(
    "CLAUDE.md"
    "AI_CONTEXT_RULES.md"
    "PROJECT_VISION.md"
    "QUICK_REFERENCE.md"
    "KNOWLEDGE_PORTAL.md"
    "ARCHITECTURE_RULES.md"
    "ZOHO_SYNC_RULES.md"
    "CODE_TEMPLATES.md"
    "TASK_PATTERNS.md"
    "FAILSAFE_PROTOCOL.md"
)

echo "✅ Checking critical documentation files..."
MISSING_COUNT=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$CLAUDE_DIR/$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗ MISSING${NC}: $file"
        ((MISSING_COUNT++))
    fi
done
echo ""

# Count total markdown files
TOTAL_MD=$(find "$CLAUDE_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | xargs)
if [ "$TOTAL_MD" -eq 23 ]; then
    echo -e "${GREEN}📊 Total documentation files: $TOTAL_MD (expected: 23) ✓${NC}"
elif [ "$TOTAL_MD" -gt 23 ]; then
    echo -e "${YELLOW}📊 Total documentation files: $TOTAL_MD (expected: 23) - Extra files present${NC}"
else
    echo -e "${RED}📊 Total documentation files: $TOTAL_MD (expected: 23) - Some files missing!${NC}"
fi
echo ""

# Check QUICK_START.txt
if [ -f "$CLAUDE_DIR/QUICK_START.txt" ]; then
    echo -e "${GREEN}✓${NC} QUICK_START.txt present"
else
    echo -e "${YELLOW}⚠${NC} QUICK_START.txt not found (optional)"
fi
echo ""

# Check agents and commands subdirectories
echo "📁 Checking subdirectories..."
if [ -d "$CLAUDE_DIR/agents" ]; then
    AGENT_COUNT=$(find "$CLAUDE_DIR/agents" -type f | wc -l | xargs)
    echo -e "  ${GREEN}✓${NC} agents/ directory ($AGENT_COUNT files)"
else
    echo -e "  ${YELLOW}⚠${NC} agents/ directory not found"
fi

if [ -d "$CLAUDE_DIR/commands" ]; then
    CMD_COUNT=$(find "$CLAUDE_DIR/commands" -type f | wc -l | xargs)
    echo -e "  ${GREEN}✓${NC} commands/ directory ($CMD_COUNT files)"
else
    echo -e "  ${YELLOW}⚠${NC} commands/ directory not found"
fi
echo ""

# Check recent git changes to .claude/
echo "📝 Recent documentation changes:"
cd "$PROJECT_ROOT" || exit 1
git log --oneline --max-count=5 -- .claude/ 2>/dev/null || echo "  (No git history available)"
echo ""

# Check working directory
CURRENT_DIR=$(pwd)
if [ "$CURRENT_DIR" = "$PROJECT_ROOT" ]; then
    echo -e "${GREEN}✓${NC} Working directory: $CURRENT_DIR (correct)"
else
    echo -e "${YELLOW}⚠${NC} Working directory: $CURRENT_DIR"
    echo -e "  ${YELLOW}→${NC} Suggested: cd $PROJECT_ROOT"
fi
echo ""

# Check project structure
echo "📂 Checking project structure..."
REQUIRED_DIRS=("app" "mobile" "scripts" "database" ".github")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $dir/"
    else
        echo -e "  ${RED}✗${NC} $dir/ missing"
    fi
done
echo ""

# Summary
echo "================================"
if [ "$MISSING_COUNT" -eq 0 ] && [ "$TOTAL_MD" -eq 23 ]; then
    echo -e "${GREEN}✅ Context verification PASSED${NC}"
    echo "   All critical documentation is present and accessible."
    echo ""
    echo "🚀 Ready to work on TSH ERP Ecosystem!"
else
    echo -e "${RED}⚠️  Context verification FAILED${NC}"
    echo "   $MISSING_COUNT critical file(s) missing"
    echo ""
    echo "⚠️  Please review missing files before proceeding."
fi
echo ""
