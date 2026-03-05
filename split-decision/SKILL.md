---
name: split-decision
description: When facing architectural decisions, technology choices, or strategic trade-offs, present options as a structured comparison and require explicit trade-off acknowledgment before proceeding. Use when the user asks "should we", "which approach", "what's the best way", or when about to recommend one approach over alternatives.
---

# Split Decision

## Purpose

There's a tendency to present "the best approach" as if there's only one right
answer. In reality, most significant decisions involve trade-offs. This skill
forces multi-option analysis before committing to any architectural, technology,
or strategic choice. No more single-option recommendations dressed up as
obvious conclusions.

## When To Activate

Trigger when you see:

- User asks "should we X or Y"
- User asks "what's the best approach for..."
- User asks "which is better..."
- About to recommend an architectural choice
- About to recommend a technology/library/tool
- Any decision with meaningful trade-offs (not trivial choices)
- Refactoring approaches with multiple valid paths
- Database, framework, or infrastructure decisions

Do NOT trigger for:

- Trivial decisions ("should I use let or const here")
- Bug fixes with clear solutions
- Syntax questions
- When user has already made the decision and just needs implementation

## Instructions

### Step 1: Identify Viable Options

Generate 2-4 genuinely viable options. These must be:

- Actually reasonable choices (not strawmen to make one look better)
- Different enough to have meaningful trade-offs
- Options you'd actually consider recommending

If there's truly only one viable option, state why alternatives don't apply.

### Step 2: Assess Each Option

For each option, evaluate:

| Dimension | What to assess |
|-----------|----------------|
| Pros | Concrete benefits specific to THIS context (not generic marketing points) |
| Cons | Concrete drawbacks specific to THIS context (not theoretical risks) |
| Effort | Relative: Low / Medium / High |
| Risk | What could go wrong, and how bad would it be |
| Reversibility | Easy to change later, or locked in? |

### Step 3: Present Comparison Table

Format as:

```
## Options Analysis: [Decision Topic]

| Option | Pros | Cons | Effort | Risk | Reversible? |
|--------|------|------|--------|------|-------------|
| A: [Name] | [Specific pros] | [Specific cons] | Low/Med/High | Low/Med/High | Yes/No/Partial |
| B: [Name] | [Specific pros] | [Specific cons] | Low/Med/High | Low/Med/High | Yes/No/Partial |
| C: [Name] | [Specific pros] | [Specific cons] | Low/Med/High | Low/Med/High | Yes/No/Partial |
```

### Step 4: State Your Lean

Do NOT be falsely neutral. State which option you'd recommend and WHY:

```
**My lean:** Option B because [specific reason tied to this context, not generic]
```

The reason must be specific to their situation, not generic best practices.

### Step 5: Request Explicit Confirmation

Before implementing, ask user to confirm which trade-offs they accept:

```
**Before I proceed:** Which trade-offs are acceptable?

- [ ] Accept [specific con from leaned option]?
- [ ] Comfortable with [specific risk from leaned option]?
- [ ] Or prefer a different option?
```

Wait for explicit choice before implementing.

## Trade-off Categories

Common trade-off dimensions to consider:

**Speed vs Quality**
- Ship fast with tech debt vs take longer for clean solution
- MVP vs full implementation

**Simplicity vs Flexibility**
- Hardcoded solution vs configurable
- Specific vs generic abstraction

**Build vs Buy**
- Custom implementation vs third-party library/service
- Control vs maintenance burden

**Now vs Later**
- Fix it properly now vs quick patch
- Refactor first vs work around

**Safety vs Convenience**
- Strict validation vs trust inputs
- Explicit vs implicit behaviour

## NEVER

- Present a single option as "the best way" for significant decisions
- Include strawman options just to make your preference look good
- Use generic pros/cons not specific to this context
- Be falsely neutral - have a recommendation
- Proceed without explicit confirmation on significant decisions
- Ignore the user's stated constraints (time, skill level, existing tech)

## ALWAYS

- Present 2-4 genuinely viable options
- Make pros/cons specific to THIS context
- State your lean with specific reasoning
- Include effort and reversibility assessment
- Wait for user to confirm trade-offs before implementing
- Respect the user's final choice even if different from your lean

## Examples

### Example 1: Database Choice

User: "Should we use Postgres or MongoDB for user data?"

```
## Options Analysis: Database for User Data

| Option | Pros | Cons | Effort | Risk | Reversible? |
|--------|------|------|--------|------|-------------|
| A: PostgreSQL | ACID compliance, your team knows SQL, mature tooling, strong for relational data | Rigid schema requires migrations, more upfront design | Medium | Low | No (migration painful) |
| B: MongoDB | Flexible schema, fast iteration, good for evolving data shapes | Eventual consistency trade-offs, less familiar to team, can become messy | Medium | Medium | No (migration painful) |
| C: Start with SQLite | Zero setup, fast for prototyping, easy to migrate later | Not for production scale, single-writer limitation | Low | Low | Yes (designed for migration) |

**My lean:** Option A (PostgreSQL) because user data is inherently relational
(users have roles, permissions, relationships) and your team already knows SQL.
The "rigid schema" con is actually a feature for user data - you want that
consistency.

**Before I proceed:**
- [ ] Accept that schema changes need migrations?
- [ ] Comfortable with more upfront data modelling?
- [ ] Or prefer a different option?
```

### Example 2: Quick Decision (Skill Not Needed)

User: "Should I use single or double quotes for this string?"

```
Use whatever your codebase already uses for consistency. If no convention,
either is fine - this isn't a meaningful trade-off.

[Proceeds without options table]
```

## Why This Skill Exists

"What's the best way to..." questions deserve nuanced answers. Every significant
technical decision involves trade-offs - pretending otherwise does users a
disservice. The goal isn't to avoid having opinions. It's to show your work and
let users make the final call with full information.
