---
name: paired-pr-review
description: Use when the user is leading a code or PR review by articulating each comment themselves — pasting code blocks with their own critique, pointing at a review doc with a per-comment structure, asking "what do you think of this?" about specific snippets, or maintaining a comment list they want validated before submitting.
---

# Paired PR Review

## Overview

The user owns the observation stream; Claude owns the rigor. Each comment the user raises gets verified against current code, given an explicit verdict, sharpened into committable language, and presented for approval **before** anything lands in the running review document.

This is the inverse of the standard `code-review` skill — there, Claude initiates issues. Here the user initiates and Claude evaluates. The strategies for filtering false positives, citing code, and avoiding pedantic nitpicks (from `code-review`) still apply; what changes is who drives the comment list.

## When to use

- User pastes a code block and articulates a critique of it
- User points at a review document with a per-comment structure (e.g., "Reader comment / Evaluation / Recommendation") and wants to add to it
- User says "what do you think of this?" about a specific snippet
- User maintains a running list of comments they want sharpened before submitting

## When NOT to use

- User asks for an autonomous review of a PR (use `code-review` instead — Claude initiates)
- User asks Claude to write code or fix the issue (skill ends at "comment committed to doc")
- User just wants a quick yes/no on whether code is OK without producing a review artifact

## The cycle

```
user comment → verify → verdict → sharpen → present for approval
                                                  ↓
                                         user approves/edits
                                                  ↓
                                         append to review doc
```

Run this loop **once per comment**. Don't batch — the user wants a back-and-forth.

## Step 1: Verify against current code, every time

The user's mental model of the code may be stale. Comments based on memory, an older branch, or a quick scan can be wrong about what's actually there.

**Always:**
- Read the file the comment names
- Find the actual symbol / line / structure being critiqued
- Note any drift between the user's framing and current code

A comment whose premise is already addressed in the code is **not** a sharpening exercise — it's a "verified, no-op" entry that goes into the doc as such (so the reader knows it was considered).

| Rationalization | Reality |
|---|---|
| "User obviously knows the code, no need to verify" | They might be working from a stale snapshot. Verify. |
| "The comment cites a file path, that's enough" | Symbols rename, code moves. Read the file as it stands today. |
| "Skipping verification saves a turn" | Committing a stale comment to the doc costs more turns to fix later. |

## Step 2: Take an explicit verdict

Pick one. Don't hedge.

- **Accepted** — premise verified, recommendation stands.
- **Accepted, with note** — premise correct, but there's nuance the user didn't surface (boundary, exception, related concern).
- **Partially accepted** — observation is right but prescription is wrong, or only half the story.
- **Verified, already implemented** — the concern was real but the working tree already addresses it. Useful when reviewing against a stale doc.
- **Rejected** — premise doesn't hold against current code; explain why.

The verdict goes at the top of the Evaluation section so a reader scanning the doc sees the disposition immediately.

## Step 3: Sharpen

Convert the raw observation into committable language:

- Replace pronouns ("this", "that code") with named symbols, file paths, line ranges
- Quote the actual code being critiqued (short snippet, not pages)
- Separate observation ("the chat handler owns error taxonomy for five distinct categories") from prescription ("extract a `chatErrorSpec` mapper")
- Cite project conventions by number/name when relevant ("violates coding-conventions §3 — composition root vs. component")
- Trim to the smallest comment that conveys the concern. The doc accumulates; bloat compounds.

## Step 4: Surface options when paths diverge

If the recommendation has multiple legitimate shapes (small fix vs. architectural change; named default vs. config knob; rename vs. struct introduction), present them as a spectrum with trade-offs. Recommend one. Let the user decide. Don't pre-collapse the choice.

Same for **coupling** — if accepting comment N implies also resolving comments N+1 and N+2, name the linkage in the Evaluation. The doc reader needs to see the dependency chain.

## Step 5: Present, wait, commit

Show the user the proposed entry **before** writing to the doc. Format:

```
### Proposed entry for [doc path]

**Verdict:** [one of the five]

**Reader comment**
[user's comment, lightly cleaned for grammar — preserve their framing]

**Evaluation**
[premise verification + verdict reasoning + cited code]

**Recommendation**
[concrete next action(s); options if applicable]
```

Wait for explicit approval. Edit on request. **Only after approval**, append the entry to the running review document, matching the doc's existing section style (numbering, heading depth, code-fence style).

If multiple comments accumulated approval before any were committed, batch the appends in one Edit call — but only with the user's say-so.

## Output structure

Match the host doc's existing per-comment shape. Common shape (this session's `code-walkthrough-current-part1.md` is an example):

```markdown
## N. [Short title]

**Reader comment**
> [the user's comment as a blockquote, or a code snippet]

**Evaluation**
[Verdict.] [Reasoning, with file:line citations and short code quotes.]

**Recommendation**
[Concrete next action. Options + trade-offs if multi-path.]
```

If the doc uses a different shape (numbered list, table, GitHub PR comment thread), follow it. Don't impose a new structure on an existing artifact.

## Common mistakes

| Mistake | Why it's wrong |
|---|---|
| Paraphrasing the user's comment back without verifying | Skips the entire value of pairing |
| Committing to the doc without explicit approval | The user is the gatekeeper; respect the checkpoint |
| Hedging the verdict ("could possibly be a small concern") | Verdicts are decisions; commit |
| Inflating one-line observations into multi-page essays | Doc bloat compounds; trim ruthlessly |
| Skipping options when paths diverge, just picking one | Forces a premature decision the user might not want |
| Missing cross-comment coupling | Reader of the doc loses the dependency map |
| Renumbering / restructuring the doc to fit a new entry | Existing IDs may be referenced elsewhere; preserve them |
| Suggesting code fixes that go beyond the comment | Scope creep; the comment is the deliverable |

## Worked example

User says:

> The `Config.AWSRegion` is just a string — typos like `eu-wset-1` won't fail validation, just blow up later in the SDK. Should be an enum.

**Step 1 — verify.** Open `internal/config/config.go`. Confirm `AWSRegion string`, confirm `validate()` only checks non-empty. Confirm bootstrap passes the string into `llm.BedrockConfig.Region`.

**Step 2 — verdict.** Accepted.

**Step 3 — sharpen.**

**Step 4 — options.** One reasonable shape (typed enum + parser, reject unknown values). Recommend it. No spectrum needed unless the user wants to debate strict-vs-permissive parsing — surface that as an open decision.

**Step 5 — present.**

```
### Proposed entry for docs/code-walkthrough-current-part1.md

**Verdict:** Accepted

**Reader comment**
> Config.AWSRegion is a string. Incorrect values could lead to obscure
> errors downstream. I think an enum is warranted.

**Evaluation**
Accepted. Current code (internal/config/config.go:81) trims `AWS_REGION` and
only validates non-empty (config.go:94). The string flows into
`llm.BedrockConfig.Region` (bootstrap.go:57), which means `eu-wset-1`
passes validation and fails later as an SDK endpoint or credential error.

**Recommendation**
Add `AWSRegion` as a typed string enum in internal/config with a parser
that rejects unknown values at Load(). Keep the env-var name `AWS_REGION`
(SDK convention); the enum is the internal typed representation post-load.
Open decision: should the seed list start with `eu-west-1` only (strict)
or include all known Sophos Central regions (lenient)?
```

User approves; append to the doc, preserve numbering, match the doc's existing heading style.

## Bottom line

User initiates. Claude verifies, decides, sharpens, presents. User approves. Claude commits. **One comment per cycle. No commits without approval.** The doc is a permanent artifact — its quality compounds over weeks; bad entries cost more to remove than to write carefully the first time.
