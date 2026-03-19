---
name: pegasus-release-analysis
description: Analyze Pegasus software release branches to extract tickets, pull requests, feature flags, and API changes. Use when examining release notes, comparing branches, or analyzing new features and dependencies for a release.
---

# Pegasus Release Analysis

Analyzes Pegasus release branches compared to main to provide comprehensive release documentation including tickets, PRs, new flags, and API changes.

## Quick Start

When analyzing a release branch, perform these steps in order:

### 1. Fetch and List Tickets
```bash
git fetch origin
git log --oneline origin/main...origin/<branch-name>
```

Extract unique ticket numbers and group commits by ticket.

### 2. Find Pull Requests
```bash
git log --oneline origin/main...origin/<branch-name> | grep -oE "CPLAT-[0-9]+" | sort -u
```

For each ticket, construct PR URLs: `https://github.com/sophos-internal/cld.csvc.taegis-sync/pull/<PR_NUMBER>`

### 3. Check for New Feature Flags
```bash
git diff origin/main...origin/<branch-name> -- '**/FeatureFlagService*.java' | grep -E "boolean should|PROVISION|FLAG"
```

Look for:
- New method declarations in `FeatureFlagService` interface
- New constants in `FeatureFlagServiceImpl`
- Implementation with `isFlagSet()` call

### 4. Analyze API Changes
```bash
git diff origin/main...origin/<branch-name> -- gradle.properties | grep apiClients
```

Check for:
- New API clients added
- API branch references changed
- New API versions

### 5. Find GraphQL Additions
```bash
git diff origin/main...origin/<branch-name> -- '**/*.java' | grep -E "GRAPH_QL.*=|query|mutation" | head -30
```

Look for:
- New GraphQL query/mutation constants
- New Taegis GraphQL operations
- GET/UPDATE operations beyond CREATE

### 6. Identify New Model Fields
```bash
git diff origin/main...origin/<branch-name> -- '**/*.java' | grep -E "new.*Request\(\)|\.xdrProvider|\.hydrateTo|isPartner|isOrganization"
```

Check for new fields in API request/response models.

## Output Format

Create a comprehensive release summary with these sections:

### Tickets Table
```markdown
| Ticket | Description | Pull Request |
|--------|-------------|--------------|
| [CPLAT-XXXXX](https://sophos.atlassian.net/browse/CPLAT-XXXXX) | Brief description | [PR #XXX](https://github.com/sophos-internal/cld.csvc.taegis-sync/pull/XXX) |
```

### New Feature Flags Table
```markdown
| Flag | Description |
|------|-------------|
| `central.taegis-sync.<flag-name>.enabled` | What this flag controls and behavior when enabled/disabled |
```

### API Changes Section
Document:
- **New API Clients**: None / List any added with their package names
- **API Branch Updates**: From `old-branch` to `new-branch`
- **New Model Fields**: List with purpose and related ticket
- **GraphQL Operations**: List new queries and mutations

## Key Considerations

### When Comparing Against Main
- Only analyze commits in range `origin/main...origin/<branch-name>`
- Exclude merge commits representing PR merges
- Focus on commits with ticket numbers in messages

### Distinguishing New vs Existing
- Check if method/field exists on main branch before marking "new"
- Verify API client isn't already in gradle.properties
- Confirm flag wasn't already implemented previously

### Feature Flag Analysis
Flags are new when they have:
1. New method declaration in `FeatureFlagService` interface
2. New constant string in `FeatureFlagServiceImpl`
3. New implementation calling `isFlagSet()`

Note: Some flags may already exist; only report truly new ones.

### API Model Field Analysis
Look for:
- New `.fieldName()` calls on request builders
- New `@JsonProperty` annotations on response models
- Comments explaining purpose of new fields

## Common Issues

**No flags found**: Some releases only have infrastructure/security fixes with no new feature flags

**Flags in multiple commits**: Track which ticket introduced each flag; consolidate if same flag repeated

**API changes without new usage**: api-store branch updates may not add new API calls; verify actual code usage

**Pre-existing features**: Always verify a feature doesn't already exist on main before reporting as new

## Pegasus-Specific Notes

- Tickets use CPLAT prefix (e.g., CPLAT-66706)
- GitHub repo: sophos-internal/cld.csvc.taegis-sync
- Taegis integration is primary downstream dependency
- Parent account provisioning is an emerging feature (check related tickets)
