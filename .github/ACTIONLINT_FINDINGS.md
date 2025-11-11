# Action Lint Findings - ROOT CAUSE IDENTIFIED

**Date:** 2025-11-11
**Tool:** rhysd/actionlint (GitHub Actions workflow linter)

##  CRITICAL ISSUE FOUND

### The Real Problem: Secrets Context in Step-Level `if` Conditions

**Error:** `context "secrets" is not allowed here`

**Explanation:**
GitHub Actions restricts where the `secrets` context can be used. It is **NOT** available in step-level `if` conditions.

### Where `secrets` CAN be used:
- ✅ Job-level `env` blocks
- ✅ Step-level `env` blocks
- ✅ Job-level `if` conditions
- ✅ Workflow inputs
- ✅ Inside `run` scripts (via environment variables)

### Where `secrets` CANNOT be used:
- ❌ Step-level `if` conditions
- ❌ Direct step conditionals like: `if: secrets.TOKEN != ''`

## Affected Workflows

Total: **11 workflows** with this issue

| Workflow | Lines with Error | Priority |
|----------|------------------|----------|
| ci.yml | 433 (2 instances) | HIGH ✅ FIXED |
| cleanup-ghcr.yml | 167 (2), 177 | HIGH |
| validate-secrets.yml | 340 (2) | HIGH |
| notify.yml | 59 (2), 163 | HIGH |
| dependabot-auto-merge.yml | 151 (2) | MEDIUM |
| deploy-production.yml | 135, 414 (2) | MEDIUM |
| e2e-tests.yml | 462 (2) | MEDIUM |
| flutter-ci.yml | 406 (2) | LOW |
| nextjs-ci.yml | 456 (2) | LOW |
| performance-test.yml | 440 (2) | LOW |
| schema-drift-check.yml | 342 (2) | LOW |
| security-scan.yml | 415 (2) | LOW |

## The Fix Pattern

### Before (WRONG - causes immediate workflow failure):
```yaml
- name: Send notification
  if: secrets.TELEGRAM_BOT_TOKEN != '' && secrets.TELEGRAM_CHAT_ID != ''
  run: |
    curl -s -X POST "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
      -d chat_id="${{ secrets.TELEGRAM_CHAT_ID }}" \
      -d text="Message"
```

### After (CORRECT - works properly):
```yaml
- name: Send notification
  if: always()  # or other non-secret condition
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
  run: |
    # Check secrets in bash instead
    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
      echo "Telegram credentials not configured, skipping"
      exit 0
    fi

    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="${TELEGRAM_CHAT_ID}" \
      -d text="Message"
```

## Why This Wasn't Caught Earlier

1. **Standard YAML validators don't check GitHub Actions semantics**
   - `yaml.safe_load()` only validates YAML syntax
   - Doesn't understand GitHub Actions context restrictions

2. **GitHub's error messages were unhelpful**
   - "workflow file issue" - very vague
   - 0s runtime - no logs available
   - No specific line numbers or error details

3. **Required specialized tool**
   - `actionlint` specifically validates GitHub Actions workflows
   - Understands context availability rules
   - Provides actionable error messages

## Impact

### Why ALL workflows were failing:
1. Most workflows use Telegram notifications
2. All notification steps used `if: secrets.TELEGRAM_BOT_TOKEN != ''` pattern
3. This pattern is **invalid** GitHub Actions syntax
4. Workflows fail at parse time (before any jobs run)
5. Result: 0 second failures with no logs

### Why `ci-test-simple.yml` worked:
```yaml
- name: Send Telegram notification
  env:
    BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}  # ✅ Correct - env block
    CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
  run: |
    # No secrets in if condition - works!
    curl -s "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" ...
```

## Repair Plan

### Phase 1: Critical Workflows (PRIORITY)
1. ✅ ci.yml - FIXED
2. ⏳ cleanup-ghcr.yml
3. ⏳ validate-secrets.yml
4. ⏳ notify.yml

### Phase 2: Medium Priority
5. ⏳ dependabot-auto-merge.yml
6. ⏳ deploy-production.yml
7. ⏳ e2e-tests.yml

### Phase 3: Low Priority
8. ⏳ flutter-ci.yml
9. ⏳ nextjs-ci.yml
10. ⏳ performance-test.yml
11. ⏳ schema-drift-check.yml
12. ⏳ security-scan.yml

## Testing Strategy

### After each fix:
1. Run actionlint to verify no errors
2. Commit and push
3. Monitor workflow run (should not fail at 0s)
4. Verify jobs actually execute

### Success Criteria:
- Workflow runs longer than 0s
- Jobs appear in GitHub Actions UI
- Steps execute (even if they fail for other reasons)
- Logs are available

## Lessons Learned

1. **Always use specialized linters**
   - Generic YAML validators insufficient for GitHub Actions
   - Use `actionlint` for all workflow development

2. **Test incrementally**
   - One working example (ci-test-simple) was key
   - Compare working vs failing to identify patterns

3. **Documentation gaps**
   - GitHub's error messages need improvement
   - Better documentation of context restrictions needed

4. **Validation in CI**
   - Should run actionlint as part of CI/CD
   - Catch issues before merge

## Next Steps

1. Fix all 11 workflows systematically
2. Add actionlint to CI pipeline
3. Document best practices
4. Update all Telegram notification patterns
5. Test each workflow after fixes
6. Re-enable weekly-devops-report.yml

---
**Status:** 🟢 ROOT CAUSE IDENTIFIED & FIX IN PROGRESS
**Progress:** 1/11 workflows fixed (ci.yml)
**Tool:** actionlint successfully diagnosed issue after hours of debugging
