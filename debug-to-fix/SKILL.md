---
name: debug-to-fix
description: When debugging frustration appears ("why isn't this working?", "it should work", "I don't understand"), orchestrate the full debug cycle - clarify, investigate, fix, verify. Prevents jumping to fixes before understanding the problem. Use when the user is stuck on a bug or expressing debugging frustration.
---

# Debug to Fix

## Purpose

An elixir for debugging. The #1 debugging mistake: jumping to fixes before
understanding the problem. This chains clarification, investigation, fix, and
verification, with gates that prevent skipping steps. Uses rubber-duck to clarify,
built-in investigation phase, and prove-it to verify.

## Prerequisites

This skill works best with these skills installed:

| Skill | Purpose | If Missing |
|-------|---------|------------|
| rubber-duck | Structured problem clarification | Falls back to built-in questions |
| prove-it | Verification enforcement | Falls back to built-in verification |
| retrospective | Document learnings | Skipped (optional phase) |

The skill degrades gracefully - it will use built-in fallbacks for missing skills.

## When To Activate

- "Why isn't this working?"
- "It should work but..."
- "I don't understand why..."
- "This doesn't make sense"
- User expresses debugging frustration
- Bug that persists after initial fix attempts
- User has been stuck on same issue for multiple messages

## Instructions

### Phase 1: Clarify

**If rubber-duck skill installed:** Invoke it now.

**If not installed, ask:**

Before we debug, let me understand the problem:

1. **Expected:** What should happen?
2. **Actual:** What actually happens?
3. **Tried:** What have you already attempted?
4. **Changed:** What changed before this broke?

**GATE:** Do not proceed until you can state the problem in one sentence:
"When I [action], I expect [expected], but instead [actual]."

Write this sentence before continuing.

### Phase 2: Investigate

**Objective:** Find the root cause, not just symptoms.

**Investigation checklist:**

1. **Reproduce:** Can you trigger the bug reliably?
   - [ ] Yes, every time
   - [ ] Sometimes (note conditions)
   - [ ] Haven't tried yet - Try now

2. **Isolate:** Where does the bug live?
   - [ ] Identified the file(s)
   - [ ] Identified the function(s)
   - [ ] Narrowed to specific lines

3. **Understand:** Why does it fail?
   - [ ] Read the actual error (not just the message)
   - [ ] Checked the data/state at failure point
   - [ ] Understood the expected flow vs actual flow

**Investigation techniques (try in order):**

```
1. Read the error message completely - what does it actually say?
2. Add logging/print at the failure point - what are the actual values?
3. Trace backwards - where do the bad values come from?
4. Check recent changes - git diff, git log
5. Rubber duck the code flow aloud
```

**GATE:** Do not proceed until you can answer:
- "The bug happens because [specific cause]"
- "I know this because [evidence]"

Write both sentences before continuing.

### Phase 3: Fix

**Now** implement the fix.

Before writing code, state:
1. **What** you're changing
2. **Why** this fixes the root cause (not just symptoms)
3. **Risk** of this change breaking something else

Implement the minimal fix. Resist the urge to refactor nearby code.

### Phase 4: Verify

**If prove-it skill installed:** Invoke it now.

**If not installed:**

Verification checklist:
- [ ] Original bug no longer reproduces
- [ ] Tested the exact scenario from Phase 1
- [ ] Checked for regressions in related functionality
- [ ] Tests pass (if applicable)

**GATE:** Do not declare victory until verification complete.

Show the evidence:
```
VERIFIED:
- [What you tested]
- [What you observed]
- [Why this confirms the fix]
```

### Phase 5: Document (Optional)

**If retrospective skill installed:** Invoke it for significant bugs.

**If not installed or bug was minor:** Skip this phase.

For significant debugging sessions (>15 min), capture:
- What the bug was
- Why it was hard to find
- What you'd do differently

## Output Format

```markdown
## Debug Session: [Brief description]

### Problem Statement
When I [action], I expect [expected], but instead [actual].

### Root Cause
The bug happens because [cause].
Evidence: [how you know]

### Fix
[What you changed and why]

### Verification
- [x] Original bug fixed
- [x] [Other checks performed]

### Learnings (if significant)
[What you'd do differently]
```

## NEVER

- Jump to fixes before completing Phase 1 (clarify)
- Guess at root cause without evidence (Phase 2)
- Declare "fixed" without verification (Phase 4)
- Skip gates because "I already know the answer"
- Refactor unrelated code while fixing a bug

## ALWAYS

- Write the problem statement sentence before investigating
- State root cause with evidence before fixing
- Verify the exact original scenario after fixing
- Keep fixes minimal and focused

## Example

**User:** "The login is broken, I don't know why"

**Phase 1 - Clarify:**
> Before we debug, help me understand:
> 1. What should happen when you log in?
> 2. What actually happens?
> 3. What have you tried?
> 4. Did anything change recently?
>
> *[User answers]*
>
> Problem statement: "When I submit the login form, I expect to be redirected to /dashboard, but instead I see a blank page with no errors."

**Phase 2 - Investigate:**
> Let me investigate...
> - Checked network tab: POST /api/login returns 200
> - Checked console: No errors
> - Checked redirect logic: `router.push('/dashboard')` is called
> - Added logging: redirect fires but page doesn't change
> - Checked recent commits: Found change to middleware yesterday
>
> Root cause: "The bug happens because new auth middleware redirects /dashboard back to /login for users without 'verified' flag, creating a loop that results in blank page."
> Evidence: "Middleware logs show redirect loop, user object missing 'verified' field."

**Phase 3 - Fix:**
> Fixing: Add 'verified: true' to user object after successful login
> Why: Root cause is missing field, not redirect logic
> Risk: Low - only affects login success path

**Phase 4 - Verify:**
> VERIFIED:
> - Logged in with test user, redirected to /dashboard
> - No redirect loop in network tab
> - Middleware logs show single redirect
> - Existing tests pass
