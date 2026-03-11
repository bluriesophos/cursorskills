# Rules

Cursor rules (`.mdc` files) provide persistent context that gets injected into conversations automatically.

Unlike skills (which are read on-demand when a situation matches), rules are loaded by Cursor whenever they're relevant — either always, or when files matching their glob pattern are open.

## When to use a rule vs a skill

| Use a **rule** when… | Use a **skill** when… |
|---|---|
| Short guidance (<50 lines) | Multi-step workflow or procedure |
| Always or frequently relevant | Situationally triggered |
| Conventions, standards, preferences | Complex procedures with phases |
| "Always do X when editing Y files" | "When Z happens, follow this process" |

## Adding rules

Place `.mdc` files in this directory. Each rule has YAML frontmatter:

```markdown
---
description: Brief description of what this rule enforces
globs: **/*.ts           # Optional: only apply when matching files are open
alwaysApply: false       # true = inject into every conversation
---

Your rule content here.
```

## Installation

```bash
# Global (all projects)
cp rules/your-rule.mdc ~/.cursor/rules/

# Per-project
cp rules/your-rule.mdc .cursor/rules/
```
