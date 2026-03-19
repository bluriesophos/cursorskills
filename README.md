# Cursor Skills & Rules

**Reusable skills and rules for Cursor that actually work.**

Skills teach the agent *how* to do things — multi-step workflows that trigger based on what you're working on. Rules provide persistent context — conventions and standards injected into every relevant conversation.

Just markdown files. No magic required.

---

## Quickstart

### Skills

```bash
# Personal (available across all your projects)
cp -r skill-name/ ~/.cursor/skills/skill-name/

# Per-project (shared with anyone using the repository)
cp -r skill-name/ .cursor/skills/skill-name/
```

Pick the skills you want, copy them to the appropriate location, and they'll activate based on their description triggers.

### Rules

```bash
# Personal (available across all your projects)
cp rules/your-rule.mdc ~/.cursor/rules/

# Per-project (shared with anyone using the repository)
cp rules/your-rule.mdc .cursor/rules/
```

Rules are `.mdc` files with YAML frontmatter. Cursor loads them automatically — either always, or when files matching their glob pattern are open.

---

## Skills vs Rules

| | **Skills** | **Rules** |
|---|---|---|
| Format | `SKILL.md` in a named directory | `.mdc` file |
| Loaded | On-demand when trigger matches | Automatically by Cursor |
| Best for | Multi-step workflows, procedures | Short conventions, standards |
| Length | Any length (read when needed) | Keep under 50 lines |
| Example | "Run a 5-phase planning ritual" | "Always use camelCase in TS files" |

**Rule of thumb**: If it has phases/steps and structured output, it's a skill. If it's a short guideline the agent should always know, it's a rule.

---

## Skills

### Planning & Risk

- [battle-plan](battle-plan) - Complete planning ritual before significant tasks. Orchestrates scope clarification, risk assessment, estimation, and confirmation. No coding until the plan is approved.

- [pre-mortem](pre-mortem) - Before starting significant tasks, imagines failure scenarios, assesses risks, and reorders the implementation plan to address high-risk items first. Based on Gary Klein's prospective hindsight research.

- [split-decision](split-decision) - Before committing to architectural or technology choices, presents 2-4 viable options as a comparison table with trade-offs. States a lean with reasoning, requires explicit confirmation.

- [you-sure](you-sure) - Before destructive or irreversible actions (rm -rf, DROP TABLE, force push), pauses with a clear checklist of impact and requires explicit confirmation.

### Code Review

- [code-review](code-review) - Structured code review workflow for comparing branches. Fetches diffs, evaluates against 14 quality criteria (design, security, performance, testing, etc.), and produces prioritised issues grouped by severity. Trigger with "Review 'branch1' against 'branch2'".

### Data & Context Management

- [dont-be-greedy](dont-be-greedy) - Prevents context overflow by estimating file sizes, chunking large data, and summarizing before loading. Never loads raw files without checking first.

- [breadcrumbs](breadcrumbs) - Leaves notes for future sessions in `.cursor/breadcrumbs.md`. Records what was tried, what worked, what failed. Session-to-session memory without manual updates.

### Debugging & Problem Solving

- [rubber-duck](rubber-duck) - When users describe problems vaguely, forces structured articulation through targeted questions before proposing solutions. Catches XY problems and handles frustrated users.

- [debug-to-fix](debug-to-fix) - Full debug cycle: clarify, investigate, fix, verify. Chains rubber-duck and prove-it with built-in investigation. Prevents jumping to fixes before understanding the problem.

- [zero-in](zero-in) - Before searching, forces you to zero in: what exactly are you looking for, what would it look like, where would it live, what else might it be called.

### Quality & Verification

- [prove-it](prove-it) - Before declaring tasks complete, actually verify the outcome. Run the code. Test the fix. No victory laps without proof.

- [loose-ends](loose-ends) - Before declaring work done, sweeps for: unused imports, TODO comments created, missing tests, console.logs left in, stale references.

- [trace-it](trace-it) - Before modifying shared code (utils, types, configs), traces all callers first. Prevents "fixed one thing, broke three others."

### Code Discipline

- [stay-in-lane](stay-in-lane) - Before making changes, verifies they match what was asked. Catches scope creep before it happens - no "while I'm here" improvements.

- [sanity-check](sanity-check) - Before building on assumptions, validates them. Prevents assumption cascades where one wrong guess leads to a completely wrong solution.

- [keep-it-simple](keep-it-simple) - Before adding abstraction, asks "do we need this now?" Resists over-engineering. Three similar lines are better than a premature abstraction.

- [safe-refactor](safe-refactor) - Refactoring cycle: assess risk, prepare, implement, verify. Chains pre-mortem and prove-it. Prevents "refactor broke production" disasters.

- [careful-delete](careful-delete) - Destruction cycle: assess blast radius, explicit confirmation, document. Chains pre-mortem and you-sure. No `rm -rf` or `DROP TABLE` without ceremony.

### Release & Deployment

- [pegasus-release-analysis](pegasus-release-analysis) - Analyze Pegasus release branches to extract tickets, pull requests, feature flags, API changes, and GraphQL operations. Provides systematic approach to release documentation and impact analysis.

### Productivity & Growth

- [pair-mode](pair-mode) - Transforms the agent into a pair programming partner. Explains reasoning, teaches patterns, adjusts depth to your level. Activate with "let's pair on this."

- [retrospective](retrospective) - After completing significant tasks, documents what worked, what failed, and key learnings. Failed attempts get documented first.

- [learn-from-this](learn-from-this) - When a session contains a significant failure, analyses the root cause and drafts a new skill to prevent it. The skill library grows from real pain, not theory.

### Awareness

- [drip](drip) - Tracks and surfaces estimated water consumption per session (~0.5ml per 1,000 tokens). Makes the physical cost of AI visible. Not guilt - just awareness.

---

## Rules

Rules live in the [`rules/`](rules) directory. See the [rules README](rules/README.md) for format details and installation instructions.

*No rules have been added yet — contributions welcome.*

---

## Writing Your Own

### Skills

Skills are `SKILL.md` files with YAML frontmatter in a named directory:

```
skill-name/
  SKILL.md
  scripts/        # optional helper scripts
```

```markdown
---
name: your-skill-name
description: Brief description including when to use it.
---

# Your Skill Name

## Instructions
Clear, step-by-step guidance for the agent.
```

The `description` field is critical — it's how the agent decides when to apply your skill. Include both WHAT the skill does and WHEN to use it.

Key principles:
1. **Description is the trigger** - Write "Use when [condition]" to help the agent know when to activate
2. **One job, done well** - If it has "and also", make two skills
3. **Code in scripts, not markdown** - Reference `scripts/foo.py`, don't embed code
4. **NEVER/ALWAYS sections** - Clear guardrails for agent behavior

### Rules

Rules are `.mdc` files with YAML frontmatter:

```markdown
---
description: Brief description of what this rule enforces
globs: **/*.ts           # Optional: only apply when matching files are open
alwaysApply: false       # true = inject into every conversation
---

Your rule content here. Keep it concise.
```

Key principles:
1. **Under 50 lines** - Rules are injected into context; keep them lean
2. **One concern per rule** - Split broad guidance into focused pieces
3. **Concrete examples** - Show the right way, not just the wrong way
4. **`alwaysApply` sparingly** - Most rules should be scoped to file patterns

### Storage Locations

| Type | Skills | Rules |
|------|--------|-------|
| Personal | `~/.cursor/skills/skill-name/` | `~/.cursor/rules/rule-name.mdc` |
| Project | `.cursor/skills/skill-name/` | `.cursor/rules/rule-name.mdc` |

---

## Credits

Adapted from [Claude-Skill-Potions](https://github.com/ElliotJLT/Claude-Skill-Potions) by [@elliot](https://github.com/elliotjlt). Original skills designed for Claude Code, converted here for Cursor's skill system.
