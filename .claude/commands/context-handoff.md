# Context Handoff (Compaction Mode)

Emergency session handoff for context compaction scenarios - when conversation gets too long.

---

## What This Command Does

This is an **enhanced version of `/end-work`** optimized for context compaction scenarios.

Creates a comprehensive, self-contained handoff document that the next Claude instance can use to continue seamlessly **without asking you to repeat anything**.

**Key Difference from `/end-work`:**
- `/end-work` = Normal session end (focuses on git state, tasks)
- `/context-handoff` = Compaction scenario (focuses on conversation context, decisions, reasoning)

---

## When Context Compaction Happens

Context compaction occurs when:
- Conversation becomes very long (15+ exchanges)
- Token limits approaching
- You see "conversation compacted" or similar warning
- Claude suggests creating a handoff

**Problem:** Next Claude instance won't have our conversation history

**Solution:** Create comprehensive handoff capturing everything discussed

---

## Execution Steps

### Step 1: Acknowledge Compaction Mode

Display:
```
⚠️  Context compaction mode activated
💾 Creating comprehensive handoff for next Claude instance...

This will capture:
✓ Full git state
✓ Conversation highlights
✓ Decisions we made together
✓ Exact continuation point
✓ What NOT to ask you again
```

### Step 2: Run Full State Capture

Execute all steps from `/end-work` command:
- Gather git status
- Ask for work summary (or auto-infer)
- Check uncommitted changes
- Document deployment status

### Step 3: Capture Conversation Context

**Additionally ask user:**
```
📝 CONVERSATION CONTEXT CAPTURE

To ensure the next Claude instance continues seamlessly, please help me capture:

1️⃣  What have we been discussing this session?
    (Main topics, features being worked on, problems being solved)

2️⃣  What decisions did we make together?
    (Architectural choices, approach agreements, implementation strategies)

3️⃣  Any preferences or constraints you mentioned?
    (Things like "don't use library X", "prefer approach Y", "must support Z")

4️⃣  What was I about to do next?
    (The exact task I was working on or about to start)

💡 I'll also review our recent conversation to capture key points.
```

### Step 4: Create Enhanced Session Backup

Generate filename:
```bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE=".claude/session_backups/SESSION_STATE_${TIMESTAMP}_COMPACTION.md"
```

**Note:** Filename includes `_COMPACTION` to indicate this is an enhanced handoff.

Write enhanced session backup with this format:

```markdown
# TSH ERP - Session State (CONTEXT COMPACTION HANDOFF)

**Purpose:** Comprehensive handoff after context compaction - next Claude should continue seamlessly.

**Last Updated:** [ISO 8601 timestamp]
**Session ID:** session-[YYYYMMDD-HHMM]
**Handoff Type:** CONTEXT_COMPACTION
**Next Session Action:** Continue from exact point below - DO NOT ask user to repeat context

---

## ⚠️  CONTEXT COMPACTION NOTICE

**This session ended due to conversation length.**

The next Claude Code instance should:
1. Run `/start-work` immediately (which will load this file)
2. Read this entire handoff document
3. Continue from exact point specified below
4. **NOT** ask user to re-explain anything documented here

---

## 🎯 Current Task & Status

**Working On:** [Detailed description of current task]

**Status:** [In Progress / Blocked / About to Start]

**Progress:** [Detailed progress description]

**Exact Next Action:** [Specific next step - be very explicit]

**Files Modified:**
```
[git status --short output]
```

**Blockers:** [Any blockers or "None"]

---

## 💬 CONVERSATION HIGHLIGHTS

**Main Topics Discussed:**
[Bullet list of main topics covered in conversation]

**Problems We Solved:**
[List of issues resolved during session]

**Questions User Asked:**
[Key questions and the answers/decisions made]

**My Recommendations Given:**
[Any technical recommendations or suggestions I provided]

---

## 🎨 DECISIONS MADE (Not Yet in Code)

**These decisions were made during our conversation but may not be reflected in commits yet:**

1. **[Decision 1]**
   - Rationale: [Why we decided this]
   - Implications: [What this means]
   - Action Required: [What needs to be done]

2. **[Decision 2]**
   - Rationale: [Why]
   - Implications: [Impact]
   - Action Required: [Next steps]

[Continue for all major decisions]

**Important:** Next Claude should honor these decisions without re-questioning them.

---

## 🎯 USER PREFERENCES & CONSTRAINTS

**User Explicitly Stated:**
[Things user said they want/don't want]
- "Prefer X over Y"
- "Don't use Z"
- "Must support A"

**Technical Constraints:**
[From conversation]
- Must use [technology/approach]
- Cannot change [system component]
- Required to [specific requirement]

**Business Constraints:**
[From conversation]
- Timeline: [if mentioned]
- Budget: [if mentioned]
- Stakeholders: [if mentioned]

---

## 🧠 IN-FLIGHT REASONING

**Problem We Were Solving:**
[Describe the problem in detail]

**Approach We Agreed On:**
[The implementation strategy decided]

**Why This Approach:**
[Reasoning behind the decision]

**Alternatives Considered:**
[What we ruled out and why]

**Current Thinking:**
[Where we are in the problem-solving process]

---

## 📝 Session Accomplishments

[User-provided or auto-generated summary of work done]

**Commits This Session:**
```
[git log with timestamps and messages]
```

**Key Changes:**
[Detailed list of changes made]

---

## 🌿 Git State

**Current Branch:** [branch]
**Status:** [clean / N uncommitted file(s)]
**Staged Changes:** [list or "None"]
**Unstaged Changes:** [list or "None"]

**Last Commit:** [hash] [message] ([time ago])

**Recent Commits:**
```
[git log --oneline -5]
```

**Uncommitted Files:**
[Detailed list with status]

---

## 🎯 EXACT CONTINUATION POINT

**User's Last Request:**
"[Exact quote of user's last message or question]"

**My Last Response/Action:**
"[What I was doing, saying, or about to do]"

**Next Claude Should:**
1. [First immediate action - be very specific]
2. [Then this]
3. [Then this]

**DO NOT:**
❌ Ask user to re-explain what we discussed
❌ Re-ask questions we already answered
❌ Suggest approaches we already ruled out
❌ Question decisions we already made
❌ Start from scratch on current task

**DO:**
✅ Continue from exact point where we left off
✅ Honor decisions made in conversation
✅ Remember user's preferences
✅ Reference this handoff if clarification needed
✅ Build on work already done

---

## 📌 Next Session Immediate Actions

**Critical Next Steps:**
1. [Most urgent action]
2. [Second priority]
3. [Third priority]

**Before Implementing:**
- [ ] Verify understanding of decisions made
- [ ] Review uncommitted changes
- [ ] Check current branch
- [ ] Load relevant @docs/ if needed

**Context Required:**
- `.claude/CLAUDE.md` (auto-loaded)
- This handoff document (will be loaded by `/start-work`)
- [Any @docs/ files that were referenced]

---

## 🚨 CRITICAL INFORMATION

**Must Remember:**
[Any absolutely critical context that would be disastrous to forget]

**Security/Production Notes:**
[Any warnings about production, credentials, or security]

**Deployment Status:**
- Current branch: [branch]
- Deploy status: [pending/done/blocked]
- Server: [staging/production]

---

## 📊 Session Metrics

**Session Duration:** [If trackable]
**Conversation Length:** [Why compaction happened]
**Branch:** [current]
**Commits Made:** [count]
**Files Changed:** [count]
**Decisions Made:** [count]

---

## 🔄 HANDOFF VERIFICATION

**Next Claude Instance - Verify You Can Answer These:**

Before starting work, confirm you understand:
- [ ] What task we were working on?
- [ ] What decisions we made and why?
- [ ] What's the exact next step?
- [ ] What approaches did we rule out?
- [ ] What are user's constraints/preferences?
- [ ] What should I NOT ask user about?

If any are unclear, refer to relevant section above.

---

## 💡 THINGS USER SHOULD NOT NEED TO REPEAT

The next Claude instance already knows:
✅ Current task and context
✅ Decisions made during conversation
✅ User's preferences and constraints
✅ Problems we solved
✅ Approaches we ruled out
✅ Current git state
✅ Next steps

**User should only need to say:**
"Continue from previous session" or run `/start-work`

---

## 📚 Context for Next Session

**Phase:** [from .claude/state/current-phase.json]

**Authorization:** RBAC + ABAC + RLS (all 3 layers required)

**Tech Stack:** FastAPI + PostgreSQL + Flutter (immutable)

**Servers:**
- Staging: 167.71.58.65 (develop branch)
- Production: 167.71.39.50 (main branch)

**Current Scale:**
- 500+ wholesale clients
- 2,218+ active products
- 12 travel sales ($35K USD/week)

---

**END OF CONTEXT COMPACTION HANDOFF**

*This enhanced handoff was created by `/context-handoff` command.*
*Next session: Run `/start-work` to load this state automatically.*
*The next Claude instance has everything needed to continue seamlessly.*
```

### Step 5: Update State Files (if major decisions)

If major architectural decisions were made, offer to update:
```
.claude/state/recent-decisions.json
```

Ask user if any decisions should be persisted to state files.

### Step 6: Verify Handoff Completeness

Ask user:
```
🔍 HANDOFF COMPLETENESS CHECK

I've captured our conversation and created a comprehensive handoff.

Before we finish, is there anything critical from our conversation that I should include? Things like:

- Decisions we made that aren't documented
- Approaches we agreed on
- Important context you provided
- Constraints or preferences you mentioned
- Anything else the next Claude MUST know

If not, the handoff is complete and ready!
```

### Step 7: Final Compaction Handoff Summary

Display:
```
✅ CONTEXT COMPACTION HANDOFF COMPLETE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 COMPREHENSIVE BACKUP CREATED:
   .claude/session_backups/SESSION_STATE_[timestamp]_COMPACTION.md

   This handoff includes:
   ✓ Full git state and work status
   ✓ Conversation highlights and context
   ✓ Decisions made together
   ✓ User preferences and constraints
   ✓ In-flight reasoning and approach
   ✓ Exact continuation point
   ✓ What NOT to ask you about again

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 NEXT SESSION STARTUP:

   When you start a new Claude Code session:

   Option 1 (Recommended):
   → Run: /start-work
   → It will automatically load this handoff

   Option 2 (Manual):
   → Tell new Claude: "Continue from previous session"
   → Reference session backup file if needed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 SEAMLESS CONTINUATION:

   The next Claude instance will:
   ✅ Load this comprehensive handoff
   ✅ Understand full context of our conversation
   ✅ Know all decisions we made
   ✅ Remember your preferences
   ✅ Continue from exact point
   ✅ NOT ask you to repeat anything documented

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 YOU WON'T NEED TO RE-EXPLAIN:

   ❌ What we were working on
   ❌ Decisions we made
   ❌ Approaches we discussed
   ❌ Your preferences or constraints
   ❌ Problems we solved
   ❌ Current git state
   ❌ Next steps

   ✅ Just continue naturally from where we left off!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 READY FOR SEAMLESS HANDOFF

The next Claude instance is fully prepared to continue your work.
You should experience zero friction in the transition.

Thank you for the session! See you in the next one.
```

---

## Important Implementation Notes

**Maximum Context Capture:**
- This is MORE comprehensive than `/end-work`
- Focus on conversation nuances, not just git state
- Capture decisions made verbally
- Document reasoning and "why" behind choices
- Include what was ruled out (prevents re-discussion)

**User Experience:**
- Next session should feel seamless
- User shouldn't notice Claude instance changed
- No repetition of context or decisions
- Pick up exactly where conversation left off

**Self-Contained Document:**
- Next Claude shouldn't need conversation history
- Everything needed is in handoff document
- But keep it organized (use sections)
- Make it scannable (next Claude can find info quickly)

**What to Emphasize:**
- Conversation context > Git status
- Decisions made > Code written
- User preferences > Technical details
- Continuation point > Historical context

---

## When to Use This Command

✅ **Use `/context-handoff` when:**
- Conversation becoming very long (15+ exchanges)
- Approaching token limits
- See "conversation will be compacted" warning
- Long, complex discussion session about to end
- Want to ensure zero context loss on next session
- User mentions "we've been talking a while"

❌ **Don't use for:**
- Normal session ends (use `/end-work` instead)
- Short conversations (context still available)
- Quick tasks (no compaction risk)

**Key Distinction:**
- `/end-work` = Normal session end (lightweight)
- `/context-handoff` = Compaction scenario (comprehensive)

---

## Success Criteria

This command succeeds when:
- ✅ Next Claude loads handoff and continues seamlessly
- ✅ User doesn't need to repeat any context
- ✅ Decisions made are honored
- ✅ User doesn't notice Claude instance changed
- ✅ Conversation continues naturally
- ✅ No "what were we doing?" questions from next Claude

**The ultimate test:**
User should be able to say "continue" and next Claude immediately knows what to do.

---

## Special Cases

**If User Wants to Add More Context:**
```
Of course! What additional context should I include in the handoff?

[Add to handoff document under relevant section]
```

**If Conversation Was Problem-Solving:**
Make sure to capture:
- Problem statement
- Solutions considered
- Why we chose approach X
- Why we ruled out approach Y
- Current progress in implementation

**If User Made Important Decisions:**
Emphasize these in handoff:
- List all decisions clearly
- Include rationale for each
- Mark as "Next Claude must honor these"

---

**Related Commands:**
- `/start-work` - Load this handoff and continue (next session)
- `/end-work` - Normal session end (lighter version)
- `/reload-context` - Full context reload
