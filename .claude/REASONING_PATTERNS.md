# Reasoning Patterns - How Claude Code Thinks

**Purpose:** Teach systematic thinking patterns for the TSH ERP Ecosystem - not just what to do, but HOW to think through problems.

**Last Updated:** 2025-11-12

---

## 🎯 Core Principle

**Don't just execute tasks. THINK like a senior software engineer who understands:**
- Business impact (500+ clients, $35K USD weekly)
- Technical constraints (FastAPI + Flutter + PostgreSQL)
- Scale considerations (2,218+ products, 30+ daily orders)
- Strategic goals (Zoho migration, system independence)

---

## 🧠 Reasoning Pattern 1: Root-Cause Analysis

### When to Use
- Bug reports or unexpected behavior
- Performance degradation
- Sync failures between systems
- User complaints or errors

### Systematic Approach

#### Step 1: Observe Symptoms
```yaml
Questions to Ask:
□ What is the EXACT error or unexpected behavior?
□ When did it start happening? (specific time/date)
□ How frequently? (always, intermittent, specific conditions)
□ Which users/roles are affected? (all, specific role, specific client)
□ Which component? (backend, frontend, mobile, TDS Core)
```

#### Step 2: Gather Evidence
```yaml
Data Sources to Check:
□ Error logs (backend logs, TDS Core logs)
□ Database state (query recent changes)
□ Recent commits (git log --since="3 days ago")
□ Recent deployments (GitHub Actions history)
□ User actions (what did they do before error?)
□ System load (is VPS overloaded?)
```

#### Step 3: Form Hypotheses
```yaml
Common Root Causes in TSH ERP:
□ Database connection issue (connection pool exhausted?)
□ Zoho API rate limit (exceeded 150 req/min?)
□ TDS Core sync failure (credentials expired?)
□ Missing data validation (invalid input accepted?)
□ N+1 query problem (performance degradation?)
□ Missing index (slow query on 2,218+ products?)
□ Authentication/RBAC issue (wrong permissions?)
□ Arabic encoding issue (UTF-8 handling?)
□ Deployment incomplete (missing component?)
□ Recent code change (introduced bug?)
```

#### Step 4: Test Hypotheses
```yaml
Verification Methods:
□ Reproduce the error in staging
□ Check specific log entries
□ Run SQL query to verify data state
□ Test with different user roles
□ Compare with previous working version
□ Isolate the component (backend vs. frontend)
```

#### Step 5: Trace to Root Cause
```yaml
Keep asking "WHY?" (5 Whys Method):
Example:
1. Why did order creation fail?
   → Database constraint violation

2. Why did constraint violation occur?
   → Missing product_id in order_items

3. Why was product_id missing?
   → Frontend didn't send it

4. Why didn't frontend send it?
   → Product selection dropdown returned null

5. Why did dropdown return null?
   → Zoho sync didn't update products table

ROOT CAUSE: TDS Core sync job failed silently
```

#### Step 6: Validate Fix
```yaml
Before Marking Complete:
□ Fix addresses root cause (not just symptom)
□ Tested in staging environment
□ Cannot recur under same conditions
□ Added safeguard to prevent future occurrence
□ Updated monitoring to detect early
```

### TSH-Specific Root-Cause Patterns

**Pattern: "Orders Not Creating"**
```
Symptoms → Database errors
Evidence → Foreign key constraint violation
Hypothesis → Missing client_id or product_id
Test → Check if Zoho sync is current
Root Cause → TDS Core sync delayed by 30+ minutes
Fix → Optimize sync frequency + add real-time validation
```

**Pattern: "Slow Performance"**
```
Symptoms → Page load > 5 seconds
Evidence → Database query taking 3+ seconds
Hypothesis → Missing pagination or index
Test → EXPLAIN ANALYZE on slow query
Root Cause → Querying all 2,218 products without pagination
Fix → Add pagination (max 100) + index on filtered column
```

---

## ⚖️ Reasoning Pattern 2: Trade-Off Decision Framework

### When to Use
- Multiple valid implementation approaches
- Conflicting requirements (speed vs. accuracy)
- Resource constraints (time, performance, complexity)
- Strategic technology choices

### Systematic Approach

#### Step 1: Identify Trade-Off Dimensions

**Common Trade-Offs in TSH ERP:**
```yaml
Speed vs. Accuracy:
- Quick approximation OR precise calculation?
- Real-time sync OR batch processing?

Performance vs. Features:
- Simple fast solution OR feature-rich slower solution?
- Eager loading OR lazy loading?

Complexity vs. Maintainability:
- Advanced optimization OR readable code?
- Generic reusable component OR specific simple code?

Now vs. Later:
- Quick fix for immediate need OR proper solution taking longer?
- Technical debt OR proper architecture?

Cost vs. Benefit:
- Optimization effort vs. actual performance gain?
- Feature complexity vs. actual usage?
```

#### Step 2: Evaluate Business Impact

**Impact Matrix:**
```yaml
HIGH Impact (Do It Right):
- Affects all 500+ clients
- Handles financial transactions ($35K USD weekly)
- Core business workflow (order processing, inventory)
- Data integrity (Zoho sync, stock levels)

MEDIUM Impact (Balance Quality and Speed):
- Affects specific user group (travel salespeople, managers)
- Reporting and analytics features
- UI/UX improvements
- Performance optimizations

LOW Impact (Speed Acceptable):
- Internal admin tools
- Rarely used features
- Cosmetic improvements
- Nice-to-have enhancements
```

#### Step 3: Apply Decision Framework

**Framework Questions:**
```yaml
Business Priority:
□ Is this blocking critical operations? (HIGH priority)
□ Does this affect revenue or customer trust? (HIGH priority)
□ Is this a competitive advantage? (MEDIUM priority)
□ Is this internal convenience? (LOW priority)

Technical Feasibility:
□ Can we do it properly within timeline?
□ Do we have all required information?
□ Are there technical blockers?
□ What's the risk level?

Scale Considerations:
□ How does this perform with 500+ clients?
□ How does this perform with 2,218+ products?
□ How does this perform with 30+ daily orders?
□ Will this scale to 10x growth?

Maintenance Burden:
□ How complex is this to maintain?
□ Will future developers understand this?
□ Does this create technical debt?
□ Can this be easily modified later?
```

#### Step 4: Make Informed Decision

**Decision Template:**
```markdown
**Trade-Off Decision: [Feature/Choice Name]**

Option A: [Approach 1]
Pros: [List]
Cons: [List]
Impact: [HIGH/MEDIUM/LOW]
Effort: [Days/Hours]
Risk: [HIGH/MEDIUM/LOW]

Option B: [Approach 2]
Pros: [List]
Cons: [List]
Impact: [HIGH/MEDIUM/LOW]
Effort: [Days/Hours]
Risk: [HIGH/MEDIUM/LOW]

**Recommendation**: [Option X]
**Reasoning**: [Connect to business goals, scale, maintainability]
**Khaleel's Decision**: [If approval needed, ask; if clear, proceed]
```

### TSH-Specific Trade-Off Examples

**Example 1: Real-Time Zoho Sync vs. Batch Sync**
```yaml
Context: Product stock levels need to be current

Option A: Real-Time Sync (every product update triggers sync)
Pros: Always current, instant updates
Cons: 150+ API calls/min risk, higher Zoho API cost, more failures
Impact: HIGH (affects order accuracy)
Effort: 2 days
Risk: HIGH (rate limits)

Option B: Batch Sync (every 15 minutes)
Pros: Fewer API calls, more reliable, better error handling
Cons: Up to 15-min delay, not real-time
Impact: HIGH (acceptable delay for most cases)
Effort: 1 day
Risk: LOW

DECISION: Option B (Batch Sync)
REASONING: For 30 daily orders, 15-min delay is acceptable. Rate limits
           are more critical risk. We can add manual "force sync" button
           for urgent cases. Phase 1 is read-only anyway.
```

**Example 2: Pagination Limit (50 vs. 100 vs. 200)**
```yaml
Context: API endpoint returning products list

Option A: 50 items per page
Pros: Faster response, less memory
Cons: More API calls, more clicks for users
Performance: ~200ms per request

Option B: 100 items per page
Pros: Balance between speed and UX
Cons: Moderate response time
Performance: ~350ms per request

Option C: 200 items per page
Pros: Fewer API calls, less pagination
Cons: Slower response, more memory
Performance: ~700ms per request

DECISION: Option B (100 items per page)
REASONING:
- 2,218 products ÷ 100 = ~23 pages (acceptable)
- 350ms response time is fast enough
- Most users search/filter instead of browsing all
- 100 is industry standard
- Can adjust later if needed
```

---

## 🚀 Reasoning Pattern 3: Performance Analysis

### When to Use
- Endpoint taking > 2 seconds
- Database query taking > 1 second
- Page load feeling slow
- Background job timing out
- Scale concerns (will this work at 10x?)

### Systematic Approach

#### Step 1: Measure Current Performance
```yaml
What to Measure:
□ Endpoint response time (total)
□ Database query time (use EXPLAIN ANALYZE)
□ Network latency (API calls, Zoho)
□ Memory usage (large datasets)
□ CPU usage (complex calculations)

Measurement Tools:
- FastAPI: Add logging middleware
- PostgreSQL: EXPLAIN ANALYZE
- Python: time.time() or cProfile
- Browser: DevTools Network tab
- TDS Dashboard: Sync job duration
```

#### Step 2: Identify Bottlenecks

**Performance Bottleneck Matrix:**
```yaml
Database (Most Common):
□ N+1 queries (multiple small queries instead of one join)
□ Missing indexes (table scans on 2,218+ products)
□ No pagination (loading all records)
□ Inefficient joins (unnecessary data loading)
□ Transaction locks (blocking operations)

Application Logic:
□ Synchronous I/O in async functions (blocking)
□ Heavy computation in request handler (should be background)
□ Inefficient algorithms (O(n²) instead of O(n))
□ Unnecessary data processing (filtering after loading all)

External Services:
□ Zoho API latency (150ms+ per call)
□ Multiple sequential API calls (should be parallel)
□ No caching (repeated identical requests)
□ Network timeouts (slow connections)

Frontend:
□ Large payload (should paginate)
□ Unoptimized images (should compress)
□ Too many re-renders (React optimization)
□ Blocking JavaScript (should defer)
```

#### Step 3: Calculate Impact

**Impact Assessment:**
```yaml
User Experience Impact:
- < 200ms: Instant (feels immediate)
- 200-500ms: Fast (acceptable for most operations)
- 500ms-2s: Noticeable (acceptable for complex operations)
- 2-5s: Slow (users will complain)
- > 5s: Unacceptable (users abandon operation)

Scale Impact (Current: 500 clients, 2,218 products):
- Will this work with 1,000 clients?
- Will this work with 5,000 products?
- Will this work with 100 daily orders?
- What happens at 10x scale?

Business Impact:
- Does this block critical workflow? (order creation, payment)
- Does this affect user trust? (slow checkout, errors)
- Does this cost money? (API calls, compute time)
```

#### Step 4: Optimize Strategically

**Optimization Priority:**
```yaml
Priority 1 - Fix Immediately:
□ Queries on 2,218+ products without pagination
□ N+1 queries loading related data
□ Missing indexes on foreign keys
□ Blocking I/O in async functions

Priority 2 - Fix Soon:
□ Inefficient algorithms (can improve 10x+)
□ Unnecessary API calls
□ Heavy computation in request handlers
□ Large payloads without compression

Priority 3 - Optimize If Time Permits:
□ Micro-optimizations (5-10% improvement)
□ Caching rarely-changing data
□ Image/asset optimization
□ Code minification
```

#### Step 5: Validate Improvement

**Before and After:**
```yaml
Benchmark:
□ Measure before optimization (baseline)
□ Apply optimization
□ Measure after optimization (result)
□ Calculate improvement percentage
□ Verify no regression in other areas

Success Criteria:
□ Response time reduced by 50%+ (significant)
□ Scales to 10x current load
□ No new bugs introduced
□ Maintainability preserved or improved
```

### TSH-Specific Performance Patterns

**Pattern: "Product List Endpoint Slow"**
```yaml
Symptoms: /api/products endpoint taking 3 seconds

Step 1 - Measure:
- Query time: 2.8 seconds
- Network: 200ms
- Processing: minimal

Step 2 - Identify Bottleneck:
EXPLAIN ANALYZE shows:
- Seq Scan on products (table scan)
- Loading all 2,218 products
- No pagination

Step 3 - Calculate Impact:
- Every user loading product list affected
- 3 seconds = "Slow" category
- At 10x scale (22,000 products): 30+ seconds

Step 4 - Optimize:
Solution 1: Add pagination (max 100 per page)
Result: 2.8s → 350ms (8x faster)

Solution 2: Add index on is_active column
Result: 350ms → 180ms (2x faster)

Combined: 2.8s → 180ms (15x faster!)

Step 5 - Validate:
✓ Tested with 2,218 products: 180ms
✓ Tested with 5,000 products (simulated): 250ms
✓ Scales to 10x: ✓
✓ No bugs introduced: ✓
```

---

## 🎯 Reasoning Pattern 4: Strategic Technical-Business Alignment

### When to Use
- Making architectural decisions
- Prioritizing features
- Evaluating new technologies
- Planning refactoring
- Assessing technical debt

### Systematic Approach

#### Step 1: Understand Business Context

**Ask Business Questions:**
```yaml
Strategic Goals:
□ What is Khaleel trying to achieve? (independence from Zoho)
□ What's the current phase? (Migration Phase 1)
□ What's the timeline? (what's urgent vs. important)
□ What's the risk tolerance? (can we experiment or must be stable)

User Needs:
□ Who are the users? (500+ clients, 100+ salesmen, managers)
□ What do they need most? (order speed, stock accuracy, reports)
□ What are pain points? (current system problems)
□ What language do they speak? (Arabic primary)

Business Constraints:
□ Budget limitations? (self-funded, minimize costs)
□ Time constraints? (deploy anytime in dev, careful in prod)
□ Team size? (Khaleel + Claude Code, no other developers)
□ Technical debt acceptable? (if strategic value)
```

#### Step 2: Map Technical Options to Business Value

**Value Mapping Matrix:**
```yaml
HIGH Business Value + LOW Technical Effort = DO FIRST
Example:
- Add pagination to product list (immediate user benefit, 2 hours)
- Add missing indexes (performance boost, 1 hour)
- Fix authentication bug (security critical, 1 day)

HIGH Business Value + HIGH Technical Effort = STRATEGIC INVESTMENT
Example:
- Complete Zoho Migration Phase 1 (independence goal, 2 weeks)
- Refactor TDS Core (scalability, 1 week)
- Build comprehensive mobile apps (field user productivity, ongoing)

LOW Business Value + LOW Technical Effort = DO IF TIME PERMITS
Example:
- Code refactoring (cleaner but same functionality, 1 day)
- UI polish (nice-to-have, 1 day)
- Additional logging (helpful for debugging, 2 hours)

LOW Business Value + HIGH Technical Effort = SKIP
Example:
- Migrate to GraphQL (no business benefit, 2 weeks)
- Rewrite frontend in new framework (no user benefit, 4 weeks)
- Over-engineering for unrealistic scale (1M clients, 3 months)
```

#### Step 3: Connect to Strategic Goals

**TSH ERP Strategic Goals:**
```yaml
Goal 1: Zoho Independence (PRIMARY)
Technical Implications:
□ Never bypass TDS Core (centralizes Zoho logic)
□ Build robust sync mechanisms
□ Data validation must be in TSH ERP (not rely on Zoho)
□ Complete Phase 1 before Phase 2

Goal 2: Scale for Growth (SECONDARY)
Technical Implications:
□ Pagination on all lists
□ Database indexes on common queries
□ Efficient sync algorithms
□ Consider 10x scale in design

Goal 3: User Productivity (PRIMARY)
Technical Implications:
□ Mobile-first design (field users)
□ Arabic language support (mandatory)
□ Fast response times (< 500ms)
□ Offline capability (mobile apps)

Goal 4: Cost Efficiency (SECONDARY)
Technical Implications:
□ Minimize Zoho API calls (batch operations)
□ Optimize server resources (VPS costs)
□ AWS S3 for backups (cheap storage)
□ No expensive third-party services
```

#### Step 4: Make Strategic Decisions

**Decision Framework:**
```yaml
For Every Technical Choice, Ask:
1. Does this align with strategic goals? (Zoho independence, scale, productivity)
2. What's the business value? (quantify if possible)
3. What's the opportunity cost? (what else could we build)
4. Is this the right time? (Phase 1 vs. Phase 2 vs. later)
5. Can this decision be reversed? (low risk vs. high risk)

Example Decision:
Choice: Should we add real-time notifications via WebSockets?

Business Value Analysis:
- Users would see order updates instantly (nice-to-have)
- Current polling every 30 seconds is acceptable
- Affects ~30 orders per day
- No user complaints about current system

Strategic Alignment:
- Doesn't advance Zoho independence
- Adds complexity (WebSocket infrastructure)
- Diverts from Phase 1 completion

Technical Effort:
- 1 week implementation
- Ongoing maintenance overhead
- New infrastructure component

DECISION: DEFER
REASONING: Business value is LOW (nice-to-have), effort is HIGH,
           and it doesn't align with current strategic goal
           (Zoho Phase 1 completion). Revisit after Phase 2.
```

### TSH-Specific Strategic Reasoning

**Example: Should we cache Zoho data in Redis?**

```yaml
Business Context:
- Current: PostgreSQL stores all synced data
- Users experience fast queries (< 500ms)
- Zoho sync every 15 minutes is acceptable
- 2,218 products, 500+ clients

Technical Context:
- Redis would reduce query time 200ms → 50ms
- Requires new infrastructure (Redis server)
- Adds complexity (cache invalidation)
- Cost: ~$10-20/month for Redis server

Strategic Analysis:
Goal Alignment:
- Zoho Independence: Neutral (doesn't help or hurt)
- Scale for Growth: Minor improvement (4x faster queries)
- User Productivity: Minimal impact (already fast enough)
- Cost Efficiency: Negative (adds monthly cost)

Business Value:
- Saves 150ms per query
- For 30 daily orders = 4.5 seconds saved per day
- Users won't notice difference (200ms is already fast)

Opportunity Cost:
- 1 week implementation time
- Could build actual features instead
- Ongoing maintenance burden

DECISION: NO - Not now
REASONING:
1. Current performance is acceptable (< 500ms)
2. Doesn't align with strategic goals
3. Adds cost and complexity
4. Optimization without clear need
5. REVISIT: When we have 10x scale or user complaints

BETTER INVESTMENT: Complete Zoho Phase 1, add missing features
```

---

## 🔄 Reasoning Pattern 5: Change Impact Analysis

### When to Use
- Before making any code change
- Before database schema changes
- Before architectural decisions
- Before deployment
- When evaluating risks

### Systematic Approach

#### Step 1: Identify Blast Radius

**What Could This Affect?**
```yaml
Code Dependencies:
□ Which files import this module?
□ Which endpoints use this function?
□ Which services depend on this?
□ Are there mobile apps using this API?

Data Dependencies:
□ Which tables have foreign keys to this?
□ Which queries filter on this column?
□ Is this data synced with Zoho?
□ Do reports depend on this data?

User Impact:
□ Which user roles are affected?
□ Which workflows use this feature?
□ How many users affected? (all 500+ clients or subset)
□ Is this in critical path? (order processing, payment)

System Impact:
□ Does this affect TDS Core sync?
□ Does this affect authentication/RBAC?
□ Does this affect performance?
□ Does this require migration?
```

#### Step 2: Assess Risk Level

**Risk Matrix:**
```yaml
🔴 CRITICAL RISK (Requires Approval + Staging Test):
- Changes to authentication/RBAC logic
- Database schema changes affecting core tables (orders, products, clients)
- TDS Core sync algorithm changes
- Zoho API integration changes
- Payment processing logic
- Data deletion or irreversible operations

🟡 MEDIUM RISK (Staging Test Required):
- API endpoint behavior changes
- Business logic changes
- Database query optimization
- Frontend UI/UX changes
- Reporting logic changes

🟢 LOW RISK (Can Deploy After Testing):
- UI text/styling changes
- New optional features
- Internal refactoring (same behavior)
- Adding new endpoints (not modifying existing)
- Logging improvements
```

#### Step 3: Plan Rollback Strategy

**For Every Change:**
```yaml
Rollback Plan:
□ Can this be rolled back? (reversible vs. irreversible)
□ How to rollback? (git revert, database migration down, manual fix)
□ What's the rollback time? (< 5 minutes vs. hours)
□ What data could be lost? (none, recoverable, permanent)

Safe Deployment Patterns:
✅ Feature flags (enable gradually)
✅ Blue-green deployment (instant rollback)
✅ Database migrations (always reversible)
✅ Staged rollout (staging → subset → all users)

Dangerous Patterns:
❌ Direct database edits (no rollback)
❌ Destructive migrations (data loss)
❌ Changing API contracts without versioning
❌ Bypassing tests "just this once"
```

#### Step 4: Test Impact Thoroughly

**Testing Checklist:**
```yaml
Before Marking Complete:
□ Unit tests pass (if applicable)
□ Manual testing in staging (all affected workflows)
□ Test with different user roles (admin, manager, salesperson, client)
□ Test with Arabic language (if UI changes)
□ Test with realistic data volume (not just 3 test records)
□ Test error cases (what if API fails, database down, etc.)
□ Verify no regression (old functionality still works)
□ Check performance (not slower than before)
```

### TSH-Specific Impact Analysis Examples

**Example: Adding a required field to products table**

```yaml
Proposed Change: Add required "minimum_stock_level" column to products table

Step 1 - Blast Radius:
Code Dependencies:
- app/models/product.py (model definition)
- app/schemas/product.py (Pydantic schemas)
- app/routers/products.py (API endpoints)
- TDS Core sync (Zoho → TSH ERP products)
- 8 Flutter mobile apps (product displays)
- React ERP admin (product management)

Data Dependencies:
- 2,218 existing products (need default value)
- order_items table (foreign key to products)
- Zoho Inventory (source of truth)

User Impact:
- Affects: Managers (who set stock levels)
- Doesn't affect: Clients, salespeople (read-only)
- Critical path: No (informational field)

System Impact:
- TDS Core must map from Zoho field
- Database migration required
- API response structure changes

Step 2 - Risk Level: 🟡 MEDIUM RISK
- Database schema change (moderate)
- TDS Core sync change (moderate)
- Not in critical path (lower risk)
- Reversible migration (lower risk)

Step 3 - Rollback Plan:
Rollback Steps:
1. Revert migration (remove column)
2. Revert code changes (git revert)
3. Redeploy previous version
Rollback Time: 10 minutes
Data Loss: None (can add column again)

Step 4 - Testing Plan:
□ Create migration with default value (0 or NULL)
□ Test TDS Core sync with Zoho field
□ Test product API endpoints (GET, POST, PUT)
□ Test mobile apps still display products
□ Test ERP admin product management
□ Test with existing 2,218 products
□ Verify no performance impact
□ Test rollback procedure in staging

Step 5 - Implementation Order:
1. Add migration (nullable first, or with default)
2. Update TDS Core sync
3. Update backend models/schemas
4. Deploy to staging
5. Test thoroughly
6. Update frontend/mobile (if needed)
7. Deploy to production
8. Monitor for issues

APPROVED TO PROCEED: Yes (after staging test)
```

---

## 🧩 Reasoning Pattern 6: Pattern Recognition & Abstraction

### When to Use
- Seeing similar code in multiple places (DRY violation)
- Solving similar problems repeatedly
- Building new features similar to existing ones
- Refactoring opportunities

### Systematic Approach

#### Step 1: Identify Patterns

**Code Patterns:**
```yaml
Repetition Signals:
□ Same logic in 3+ places (extract to function)
□ Similar API endpoints (extract to generic handler)
□ Similar database queries (extract to service method)
□ Similar validation rules (extract to schema/validator)
□ Similar UI components (extract to reusable component)
```

**Business Patterns:**
```yaml
Common Workflows:
□ CRUD operations (Create, Read, Update, Delete)
□ Pagination + filtering + sorting (list endpoints)
□ Authentication + RBAC (protected operations)
□ Zoho sync operations (pull data via TDS Core)
□ Arabic bilingual fields (name, description)
□ Audit logging (who changed what when)
```

#### Step 2: Evaluate Abstraction Value

**Should I Abstract This?**
```yaml
✅ Abstract When:
- Used in 3+ places (proven pattern)
- Likely to be reused (future features)
- Complex logic worth centralizing (maintain once)
- Business rule consistency critical (single source)

❌ Don't Abstract When:
- Only used once or twice (premature)
- Still evolving (requirements unclear)
- Simple code (abstraction adds complexity)
- Unique business logic (not truly reusable)
```

#### Step 3: Design Abstraction

**Abstraction Levels:**
```yaml
Level 1: Function
- Extract repeated logic into function
- Single responsibility
- Clear parameters and return value

Level 2: Service Class
- Group related functions
- Encapsulate business logic
- Reusable across routes

Level 3: Base Class / Mixin
- Common functionality across models
- Inheritance hierarchy
- Shared behavior

Level 4: Design Pattern
- Factory, Strategy, Observer, etc.
- Architectural patterns
- Framework-level abstractions
```

### TSH-Specific Pattern Examples

**Pattern: Bilingual Field Handling**
```python
# ❌ BEFORE: Repeated everywhere
product = Product(
    name=data.name,
    name_ar=data.name_ar,
    description=data.description,
    description_ar=data.description_ar
)

client = Client(
    name=data.name,
    name_ar=data.name_ar,
    address=data.address,
    address_ar=data.address_ar
)

# ✅ AFTER: Abstracted pattern
class BilingualMixin:
    name: str
    name_ar: str
    description: str
    description_ar: str

    def get_name(self, lang='en'):
        return self.name_ar if lang == 'ar' else self.name

# Usage:
class Product(BilingualMixin, Base):
    # Automatically gets bilingual fields
    pass
```

---

## 📚 Reasoning Pattern Application Checklist

### Before Starting Any Task

```yaml
□ Which reasoning pattern applies?
  - Bug? → Root-Cause Analysis
  - Multiple options? → Trade-Off Decision
  - Slow performance? → Performance Analysis
  - New feature? → Strategic Alignment
  - Code change? → Change Impact Analysis
  - Repetitive code? → Pattern Recognition

□ Have I thought through the problem systematically?
□ Have I considered business context (500+ clients, 2,218+ products)?
□ Have I considered scale (will this work at 10x)?
□ Have I considered strategic goals (Zoho independence)?
□ Have I considered risk and rollback?
```

### During Implementation

```yaml
□ Am I applying the right pattern?
□ Am I considering edge cases?
□ Am I thinking about maintainability?
□ Am I balancing speed and quality?
□ Am I connecting technical choices to business value?
```

### After Completion

```yaml
□ Did my reasoning lead to a good solution?
□ What did I learn from this pattern?
□ Can this reasoning be reused for similar problems?
□ Should I document this pattern for future reference?
```

---

## 🎯 Success Indicators

**I'm reasoning well when:**
- ✅ I trace problems to root cause (not just symptoms)
- ✅ I make trade-offs based on business value
- ✅ I optimize strategically (high-impact bottlenecks first)
- ✅ I connect technical decisions to business goals
- ✅ I assess change impact before implementing
- ✅ I recognize patterns and abstract appropriately
- ✅ Khaleel doesn't have to explain business context repeatedly
- ✅ My solutions scale and are maintainable

**I need to improve reasoning when:**
- ❌ I fix symptoms without finding root cause
- ❌ I make technical decisions without considering business impact
- ❌ I optimize prematurely or in wrong places
- ❌ I create solutions that don't scale
- ❌ I change code without assessing impact
- ❌ I duplicate code instead of recognizing patterns
- ❌ Khaleel has to correct my thinking process

---

**END OF REASONING_PATTERNS.md**

*Read this file to learn HOW to think, not just WHAT to do. Apply these patterns systematically to every task.*
