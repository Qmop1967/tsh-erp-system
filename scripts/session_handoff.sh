#!/bin/bash
# TSH ERP - Session Handoff Script
# Purpose: Save and load session state for seamless continuity across Claude Code sessions
# Usage:
#   ./scripts/session_handoff.sh save "Working on feature X"
#   ./scripts/session_handoff.sh load
#   ./scripts/session_handoff.sh auto

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SESSION_STATE="$PROJECT_ROOT/.claude/SESSION_STATE.md"
BACKUP_DIR="$PROJECT_ROOT/.claude/session_backups"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Functions
show_usage() {
    echo "Usage: $0 {save|load|auto} [description]"
    echo ""
    echo "Modes:"
    echo "  save <description>  - Save current session state with description"
    echo "  load                - Load and display last session state"
    echo "  auto                - Auto-save mode (saves every 10 minutes)"
    echo ""
    echo "Examples:"
    echo "  $0 save \"Working on Zoho sync optimization\""
    echo "  $0 load"
    echo "  $0 auto"
}

save_session() {
    local DESCRIPTION="$1"
    if [ -z "$DESCRIPTION" ]; then
        DESCRIPTION="Session work in progress"
    fi

    echo -e "${BLUE}💾 Saving Session State...${NC}"
    echo ""

    # Backup current state if exists
    if [ -f "$SESSION_STATE" ]; then
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        cp "$SESSION_STATE" "$BACKUP_DIR/SESSION_STATE_$TIMESTAMP.md"
        echo -e "${GREEN}✓${NC} Backed up previous state"
    fi

    # Get current state
    CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    SESSION_ID="session-$(date +%Y-%m-%d-%H%M)"
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    GIT_STATUS=$(git status -s 2>/dev/null || echo "No git status available")
    UNCOMMITTED_COUNT=$(echo "$GIT_STATUS" | grep -c "^" || echo "0")
    LAST_COMMIT=$(git log -1 --oneline 2>/dev/null || echo "No commits")
    RECENT_COMMITS=$(git log --oneline -5 2>/dev/null || echo "No commit history")

    # Get modified files
    MODIFIED_FILES=$(git status -s 2>/dev/null | head -10 || echo "None")

    # Create new session state
    cat > "$SESSION_STATE" << EOF
# TSH ERP - Session State

**Purpose:** Track current work across Claude Code sessions for seamless continuity.

**Last Updated:** $CURRENT_TIME
**Session ID:** $SESSION_ID

---

## 🎯 Current Task

**Working On:** $DESCRIPTION
**Status:** In Progress
**Progress:** Active session
**Next Step:** Continue from where left off

**Files Modified:**
\`\`\`
$MODIFIED_FILES
\`\`\`

**Blockers:** None (update if needed)
**Dependencies:** None (update if needed)

---

## 📝 Recent Context (Last Session)

**Time Range:** Session started at $CURRENT_TIME

**Git Status:**
- Branch: $CURRENT_BRANCH
- Uncommitted changes: $UNCOMMITTED_COUNT file(s)
- Last commit: $LAST_COMMIT

**Recent Commits:**
\`\`\`
$RECENT_COMMITS
\`\`\`

**Key Activities:**
- $DESCRIPTION
- (Add more details manually as needed)

---

## 🌿 Active Branches

**Current Branch:** $CURRENT_BRANCH
**Status:** $([ "$UNCOMMITTED_COUNT" -eq "0" ] && echo "Clean" || echo "Uncommitted changes: $UNCOMMITTED_COUNT file(s)")
**Last Commit:** $LAST_COMMIT

**Branch Strategy:**
- Push to develop → Auto-deploy to staging
- Push to main → Auto-deploy to production

---

## ❓ Pending Questions

**For Khaleel:**
- (Add questions here)

**Technical Questions:**
- (Add technical questions here)

---

## 📌 Important Notes

**System State:**
- Working Directory: $PROJECT_ROOT
- Documentation: 24 files in .claude/
- Current Phase: Zoho Migration Phase 1 (read-only)
- Mode: Development (deploy anytime)

**Recent Work:**
- $DESCRIPTION

**Critical Reminders:**
- Always deploy ALL components together
- Never bypass TDS Core for Zoho operations
- Always include Arabic fields (name_ar, description_ar)
- Test on staging before production

---

## 🔄 Session Continuity

**To Resume This Session:**

1. **Load Session State:**
   \`\`\`bash
   ./scripts/session_handoff.sh load
   \`\`\`

2. **Check Recent Work:**
   \`\`\`bash
   ./scripts/session_context.sh
   \`\`\`

3. **Verify Context:**
   \`\`\`bash
   ./.claude/verify_context.sh
   \`\`\`

4. **Review Git Status:**
   \`\`\`bash
   git status
   git log --oneline -5
   \`\`\`

5. **Quick Reference:**
   \`\`\`bash
   cat .claude/QUICK_START.txt
   \`\`\`

**Expected State:**
- Working directory: $PROJECT_ROOT
- Branch: $CURRENT_BRANCH
- Task: $DESCRIPTION

---

## 🚀 Next Steps (When Resuming)

**Priority 0:** Review this session state and continue work

**Current Focus:**
- $DESCRIPTION

**Context Files to Read:**
- .claude/QUICK_REFERENCE.md (60-second refresh)
- .claude/PROJECT_VISION.md (business context)
- .claude/SESSION_STATE.md (this file)

---

## 📊 Session Metrics

**Session Start:** $CURRENT_TIME
**Last Save:** $CURRENT_TIME
**Branch:** $CURRENT_BRANCH
**Uncommitted Changes:** $UNCOMMITTED_COUNT file(s)

---

## 💾 Auto-Save Information

**Last Auto-Save:** $CURRENT_TIME
**Save Method:** Manual (via session_handoff.sh)
**Save Frequency:** On-demand or every 10 minutes (auto mode)

**How to Update This File:**
\`\`\`bash
# Save current state
./scripts/session_handoff.sh save "Brief description of current work"

# Load saved state
./scripts/session_handoff.sh load
\`\`\`

---

## 🔍 Quick Status Check

**System Health:** ✅ (Verify with: ./.claude/verify_context.sh)
**Git Status:** $([ "$UNCOMMITTED_COUNT" -eq "0" ] && echo "✅ Clean" || echo "⚠️ $UNCOMMITTED_COUNT uncommitted file(s)")
**Context Available:** ✅
**Ready to Resume:** ✅

---

**END OF SESSION STATE**

*This file is automatically updated by session_handoff.sh. Always check this file at session start for continuity.*
EOF

    echo -e "${GREEN}✅ Session state saved successfully${NC}"
    echo ""
    echo "Saved to: $SESSION_STATE"
    echo "Backup location: $BACKUP_DIR/"
    echo ""
    echo -e "${YELLOW}📝 Tip:${NC} Review and edit $SESSION_STATE to add more details"
}

load_session() {
    echo -e "${BLUE}📋 Loading Session State...${NC}"
    echo "================================="
    echo ""

    if [ ! -f "$SESSION_STATE" ]; then
        echo -e "${RED}❌ No session state found${NC}"
        echo ""
        echo "Create one with:"
        echo "  ./scripts/session_handoff.sh save \"Working on task X\""
        exit 1
    fi

    # Extract key information
    LAST_UPDATED=$(grep "Last Updated:" "$SESSION_STATE" | head -1 | cut -d':' -f2- | xargs)
    WORKING_ON=$(grep "Working On:" "$SESSION_STATE" | head -1 | cut -d':' -f2- | xargs)
    CURRENT_BRANCH=$(grep "Current Branch:" "$SESSION_STATE" | head -1 | cut -d':' -f2- | xargs)

    # Calculate time since last update
    if [ -n "$LAST_UPDATED" ]; then
        LAST_TIMESTAMP=$(date -j -f "%Y-%m-%d %H:%M:%S" "$LAST_UPDATED" +%s 2>/dev/null || echo "0")
        CURRENT_TIMESTAMP=$(date +%s)
        SECONDS_DIFF=$((CURRENT_TIMESTAMP - LAST_TIMESTAMP))
        HOURS_AGO=$((SECONDS_DIFF / 3600))

        if [ "$HOURS_AGO" -lt 1 ]; then
            MINUTES_AGO=$((SECONDS_DIFF / 60))
            TIME_AGO="${MINUTES_AGO} minute(s) ago"
        else
            TIME_AGO="${HOURS_AGO} hour(s) ago"
        fi
    else
        TIME_AGO="Unknown"
    fi

    # Display summary
    echo -e "${GREEN}Last Session:${NC} $LAST_UPDATED ($TIME_AGO)"
    echo ""
    echo -e "${GREEN}Task:${NC} $WORKING_ON"
    echo -e "${GREEN}Branch:${NC} $CURRENT_BRANCH"
    echo ""
    echo "─────────────────────────────────"
    echo ""

    # Show pending questions if any
    if grep -q "For Khaleel:" "$SESSION_STATE"; then
        echo -e "${YELLOW}Pending Questions:${NC}"
        grep -A 2 "For Khaleel:" "$SESSION_STATE" | tail -2
        echo ""
    fi

    # Show next steps
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Review full session state: cat .claude/SESSION_STATE.md"
    echo "2. Check recent work: ./scripts/session_context.sh"
    echo "3. Verify context: ./.claude/verify_context.sh"
    echo "4. Ask Khaleel what to work on next"
    echo ""

    echo -e "${GREEN}✅ Session state loaded${NC}"
    echo ""
    echo -e "${YELLOW}Press Enter to view full session state...${NC}"
    read -r
    cat "$SESSION_STATE"
}

auto_save_mode() {
    echo -e "${BLUE}🔄 Auto-Save Mode (Ctrl+C to stop)${NC}"
    echo "Saving session state every 10 minutes..."
    echo ""

    while true; do
        TIMESTAMP=$(date '+%H:%M:%S')
        echo "[$TIMESTAMP] Auto-saving session state..."

        # Auto-save with timestamp description
        DESCRIPTION="Auto-save at $TIMESTAMP"
        save_session "$DESCRIPTION" > /dev/null 2>&1

        echo "[$TIMESTAMP] ✓ Saved"
        echo "[$TIMESTAMP] Next save in 10 minutes..."
        echo ""

        sleep 600  # 10 minutes
    done
}

# Main script logic
case "${1:-}" in
    save)
        save_session "${2:-Session work in progress}"
        ;;
    load)
        load_session
        ;;
    auto)
        auto_save_mode
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
