---
name: jira-ticket-creator
description: >-
  Create JIRA tickets using a template ticket for project, components, and required
  field values. Supports bulk creation, file attachments, and linking. Use when the
  user asks to "create JIRA tickets", "create stories", "file tickets", or mentions
  acli/JIRA ticket creation.
---

# JIRA Ticket Creator

Create JIRA tickets that inherit project configuration, components, and required
custom fields from a template ticket.

## When To Activate

- User asks to create one or more JIRA tickets/stories/tasks
- User mentions a template ticket to base new tickets on
- User wants to bulk-create tickets from a plan or work breakdown

## Prerequisites

- `acli` installed and authenticated (`acli jira workitem view <KEY>` should work)
- macOS (scripts read OAuth token from keychain)
- PyYAML installed (`pip install pyyaml`)

## Workflow

### Phase 1: Gather Inputs

The user will provide ticket content in whatever form is natural — a markdown
document, bullet points, verbal description, or pointer to existing files.
Your job is to extract the structured data from their input.

**Required from the user:**

1. **Template ticket key** — ask explicitly if not provided (e.g., `CPLAT-65215`)
2. **Ticket content** — provided in one of these forms:

| User provides | What you do |
|---------------|-------------|
| A work breakdown / plan document | Read it, extract summaries + scope + AC per ticket |
| A list of summaries | Use summaries as-is, write descriptions from context |
| Detailed implementation plans (separate files) | Read each, extract summary/description/AC |
| Verbal description ("create 3 tickets for X, Y, Z") | Draft summaries + descriptions, confirm with user |

**Optional (ask if not mentioned, default in parens):**

3. **Assignee** — (unassigned)
4. **Link target** — should new tickets link to the template or another ticket? (link to template)
5. **Attachments** — files to attach to each ticket? (none)

**Do NOT ask the user to write JSON.** You build `tickets.json` from their input.

### Phase 2: Extract Template Fields

Run the extraction script to read the template ticket's project, components,
issue type, epic link, and all custom field values:

```bash
python scripts/extract-template.py CPLAT-65215
```

Output: `template.json` with all field configuration. Review the output to
confirm the project, components, and required custom fields look correct.

**Why this step exists**: `acli jira workitem create` and `clone` both fail on
projects with required custom fields (e.g., "Components is required"). The REST
API is the only reliable way to set these fields, and this script extracts the
field IDs and values automatically.

### Phase 3: Build Ticket Definitions

**You build this file** from whatever the user provided. Do not ask them to
create or edit JSON.

Write a `tickets.json` file with this structure:

```json
[
  {
    "summary": "Ticket title",
    "description": "Description text or ADF object",
    "acceptance_criteria": "AC text or ADF object"
  }
]
```

**Field formats:**
- `summary` — required, plain string
- `description` — plain string (auto-converted to ADF) or ADF document object
- `acceptance_criteria` — plain string or ADF object, mapped to the template's
  Acceptance Criteria custom field
- `labels` — optional array of strings

For an example of well-structured input, see
[examples/work-breakdown.md](examples/work-breakdown.md).

#### Mapping user content to ticket fields

**From a work breakdown doc:**
- `summary` = the ticket title/heading
- `description` = the scope/description section, including sub-bullets
- `acceptance_criteria` = the acceptance criteria checklist

**From implementation plan files:**
- `summary` = the top-level heading (e.g., "Ticket 1: Node.js Build...")
- `description` = the full plan content, summarized for the JIRA description
  (scope, key decisions, dependencies, estimate)
- `acceptance_criteria` = extracted from the AC section of the plan
- The original file gets *attached* in Phase 5 (not pasted into the description)

**From a verbal list:**
- `summary` = each item the user listed
- `description` = expand from context, or ask the user to elaborate
- `acceptance_criteria` = draft from the description, confirm with user

#### Plain text vs ADF

Use **plain text** when the description is simple paragraphs. The script
auto-converts to ADF.

Use **ADF objects** when you need rich formatting (headings, bullet lists,
code blocks). Build ADF using the helpers in `create-tickets.py` (`adf_doc`,
`paragraph`, `text_node`, `heading`, `bullet_list`, `code_text`) or construct
manually. See the
[ADF reference](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/).

**Prefer ADF** for descriptions with structure (scope sections, bullet lists).
JIRA renders plain text as a single block with no formatting.

### Phase 4: Create Tickets

```bash
python scripts/create-tickets.py template.json tickets.json
```

Output: `created-tickets.json` with ticket keys and URLs.

**What it does:**
- Reads template configuration (project, components, custom fields)
- Builds payloads with all required fields pre-populated from the template
- Creates each ticket via the Jira REST API
- Select-type custom fields (e.g., Update Instructions: "No") are copied as-is
- ADF fields can be overridden per-ticket or omitted

### Phase 5: Post-Creation Tasks

Run post-creation tasks as needed:

```bash
# Remove assignees and link to parent ticket
python scripts/post-create.py template.json created-tickets.json \
    --unassign --link-to CPLAT-65215

# Attach files by index (1-based, matching ticket order)
python scripts/post-create.py template.json created-tickets.json \
    --attach-idx 1:docs/ticket-1-plan.md \
    --attach-idx 2:docs/ticket-2-plan.md

# Attach files by ticket key
python scripts/post-create.py template.json created-tickets.json \
    --attach docs/plan.md:CPLAT-67326
```

**Available options:**

| Flag | Purpose |
|------|---------|
| `--unassign` | Remove assignee from all created tickets |
| `--link-to KEY` | Link all tickets to KEY |
| `--link-type TYPE` | Link type (default: `Relates`) |
| `--attach FILE:KEY` | Attach FILE to ticket KEY |
| `--attach-idx N:FILE` | Attach FILE to Nth created ticket (1-based) |

### Phase 6: Report Results

Present a summary table to the user:

```markdown
| # | Key | Summary | URL |
|---|-----|---------|-----|
| 1 | CPLAT-67326 | Node.js Build | https://sophos.atlassian.net/browse/CPLAT-67326 |
```

## Script Reference

| Script | Input | Output | Purpose |
|--------|-------|--------|---------|
| `extract-template.py` | Issue key | `template.json` | Read template ticket fields via REST API |
| `create-tickets.py` | `template.json` + `tickets.json` | `created-tickets.json` | Create tickets with all required fields |
| `post-create.py` | `template.json` + `created-tickets.json` | — | Unassign, link, attach files |

All scripts read the OAuth token fresh from the keychain on each run.

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| 401 Unauthorized | OAuth token expired | Run any `acli jira` command to refresh, then re-run |
| "Components is required" | Template extraction missed a field | Re-run `extract-template.py` and check `template.json` |
| `yaml` import error | PyYAML not installed | `pip install pyyaml` |
| Keychain access denied | Sandbox restriction | Use `required_permissions: ["all"]` |
| Empty `created-tickets.json` | All creations failed | Check stderr for API error messages |

## Important Notes

- **Always use `required_permissions: ["all"]`** for all script invocations
  (keychain access + network)
- **Field IDs vary by Jira instance** — always extract from the template,
  never hardcode
- **Clean up intermediate files** after use (`template.json`, `tickets.json`,
  `created-tickets.json`)
- **Token lifetime** is ~1 hour — if a long batch fails partway, refresh and
  retry from where it stopped
