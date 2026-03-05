---
name: breadcrumbs
description: Leaves notes for future sessions in .cursor/breadcrumbs.md. Records what was tried, what worked, what failed, and context for next time. On session start, reads breadcrumbs to understand history. Use when starting a new session, completing significant work, or before ending a session.
---

# Breadcrumbs

## Purpose

Sessions are stateless. You close the window, context is gone. Next
session starts fresh with no memory of what was tried, what failed, or why
certain approaches were abandoned. Breadcrumbs fixes this - notes you leave
for future-you (or the future agent) to find.

## When To Activate

**Read breadcrumbs (session start):**
- Beginning of a new session
- User says "what were we working on?"
- User references previous session work
- Before starting work on a familiar codebase

**Write breadcrumbs (during/end of session):**
- After completing significant work
- After hitting a dead end or failed approach
- Before ending a session
- User says "remember this" or "note for next time"
- After discovering something important about the codebase

## Instructions

### File Location

```
.cursor/breadcrumbs.md    # Project-specific (preferred)
```

Create `.cursor/` directory if it doesn't exist.

### Reading Breadcrumbs (Session Start)

At session start, check for breadcrumbs:

```bash
cat .cursor/breadcrumbs.md 2>/dev/null || echo "No breadcrumbs found"
```

If found, summarize key points:

```markdown
## Previous Session Context

**Last worked on:** [topic]
**Status:** [completed/in-progress/blocked]
**Key notes:**
- [important finding 1]
- [important finding 2]

**Warnings from past self:**
- [thing that didn't work]
```

Don't read the whole file aloud - summarize what's relevant.

### Writing Breadcrumbs

Append to breadcrumbs file (don't overwrite):

```markdown
---
## [Date] - [Brief Topic]

**What we worked on:**
[1-2 sentence summary]

**What worked:**
- [approach that succeeded]

**What didn't work:**
- [approach that failed] - [why it failed]

**Left off at:**
[current state, what's next]

**Notes for next time:**
- [important context]
- [gotcha to remember]
- [file locations worth knowing]
```

### Breadcrumb Types

**Discovery breadcrumb** - Found something important:
```markdown
## 2024-01-15 - Discovery: Auth flow

**Found:** Auth doesn't use middleware. It's in route handlers.
**Location:** src/routes/api/*.ts - each route calls `validateSession()` directly
**Why it matters:** Don't look in middleware/ for auth stuff
```

**Dead end breadcrumb** - Tried something that failed:
```markdown
## 2024-01-15 - Dead End: Redis caching

**Tried:** Adding Redis cache for user sessions
**Failed because:** App uses serverless, Redis connections don't persist
**Don't try again:** Any persistent connection solution
**Instead:** Use edge-compatible cache (KV store)
```

**Progress breadcrumb** - Work in progress:
```markdown
## 2024-01-15 - In Progress: API refactor

**Done:**
- [x] Moved routes to /api/v2
- [x] Updated auth middleware

**Not done:**
- [ ] Update client SDK
- [ ] Migration script

**Blocked on:** Waiting for DB schema approval
**Next steps:** Once approved, run migration then update SDK
```

**Context breadcrumb** - Important background:
```markdown
## 2024-01-15 - Context: Why we use X

**Decision:** Using Prisma instead of raw SQL
**Why:** Team preference, type safety, migration tooling
**Trade-off:** Slower queries but faster development
**Don't suggest:** Switching to raw SQL (already discussed)
```

### Breadcrumb Hygiene

**Pruning old breadcrumbs:**
- Keep last 10-15 entries
- Archive old ones to `.cursor/breadcrumbs-archive.md`
- Delete truly obsolete info (completed features, resolved issues)

**When to prune:**
- File exceeds ~200 lines
- User asks to clean up
- Old breadcrumbs reference deleted code

## NEVER

- Overwrite the entire breadcrumbs file (append only)
- Include sensitive data (passwords, keys, secrets)
- Write breadcrumbs for trivial work
- Ignore existing breadcrumbs at session start
- Write vague notes ("worked on stuff")

## ALWAYS

- Check for breadcrumbs at session start
- Record dead ends (future you will thank you)
- Include file paths for important discoveries
- Note the "why" not just the "what"
- Keep entries scannable (bullets, not paragraphs)
