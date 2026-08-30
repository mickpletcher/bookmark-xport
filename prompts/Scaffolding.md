<!-- markdownlint-disable MD025 MD028 MD060 -->

# Software Project Living Documentation Standard

```text
Living Documentation Standard: 2.2
```

## Purpose

This document defines a reusable, repository-local standard for initializing and maintaining software projects with continuously reviewed, AI-friendly documentation.

The objective is to let a developer, reviewer, maintainer, or AI coding agent quickly understand what the project is, what it was agreed to do, what condition it is in, how it is built, what changed, what is known to be wrong or compromised, what is deferred, and how correctness is proven.

The standard depends on no CI platform, no repository administration permissions, and no specific source-control host. Everything it requires lives inside the repository.

---

## Version History

### 2.2 — Operational precision

| Addition | Reason |
|---|---|
| Responsibility model with canonical default filenames | Resolves the contradiction between required filenames and Adoption Mode's rule against duplicate authorities |
| Authority Mapping table, one authority per responsibility | Makes the mapping explicit and single-valued so nothing is half-covered by three documents |
| Change Classes 0 through 4 | Removes subjective judgment about how much process a change requires |
| Source-of-Truth Hierarchy, scoped by question | Defines what wins when documents disagree, without letting code override agreed scope |
| Waivers, split into transient and standing | A blocked requirement is recorded rather than silently skipped or failing the whole task |
| Evidence citations extended to ARCHITECTURE | The document most prone to confident invention now carries its sources |
| ADR immutability rule and reciprocal supersession fields | Preserves decision history cleanly |
| Compliance status derived from docs-check, not asserted | A self-reported compliance table is checkbox theater within two months |
| `Tests skipped` and `Reason skipped` in the completion report | Distinguishes what was not run from what did not apply |

### 2.1 — Contractual document class

| Addition | Reason |
|---|---|
| Document Classes: Living, Contractual, Derived | Requirements follow inverted update rules and cannot share the living ruleset |
| REQUIREMENTS, DESCRIPTOR, AMENDMENTS responsibilities | Scaffolded placeholders act as a standing obligation, not an optional extra |
| Traceability as a living responsibility | The bridge between agreed scope and shipped code |
| Tier 2C — Client Project | Contractual documents apply only where a client and agreed scope exist |
| Requirement review step | Detects silent scope drift on every meaningful change |
| Requirement coverage in assessment; acceptance criteria in validation | Status reporting and sign-off derived from the repository |
| Frozen documents excluded from drift detection | Contractual documents should not generate staleness warnings |

### 2.0 — Scaling and verifiability

| Problem in 1.0 | Fix in 2.0 |
|---|---|
| One fixed weight for all projects | Project Tiers |
| Health claims with no basis become fiction | Evidence Rule; `Not assessed` is a valid value |
| Resolved items grow files without bound | Archive with mandatory archival |
| Assessment and changelog are merge-conflict magnets | Changelog fragments; assessment is main-branch only |
| Nowhere for bugs | Defect tracking responsibility |
| Agents read every document before trivial changes | Routed reads keyed to change type |
| Same information duplicated across four documents | Secondary sections replaced with links |
| "Meaningful change" defined so broadly it filters nothing | Explicit non-meaningful examples |
| No way to detect staleness | `docs-check` freshness gate |
| Completion reports unverifiable | Commands and exit codes required |
| Nothing covers operating the software | Operations responsibility |
| Secrets rule with no mechanism | Ignore rules, placeholder rule, scan step |
| Version marker optional | Version marker mandatory |
| Two competing bootstrap instructions | Single canonical bootstrap |

---

## Core Principle

> A software change is not complete until the repository's documentation has been reviewed against the resulting repository state, and every document made stale by the change has been corrected.

Four corollaries carry equal weight:

> Documentation must never be modified merely to produce a diff.

> A documented claim that cannot be traced to evidence must be stated as unverified or omitted.

> Agreed scope is never quietly rewritten to match what was built. Divergence is a finding, not an error to be corrected in the document.

> A requirement that cannot be met is waived on the record, not skipped in silence.

---

# Part I — Structure

## Documentation Responsibilities

**This standard requires responsibilities, not filenames.** A repository must have exactly one authoritative source for each responsibility its tier requires. The filenames below are canonical defaults, used when nothing already serves the purpose.

| Responsibility | Question answered | Canonical default | Class |
|---|---|---|---|
| Project overview | What is this project? | `README.md` | Living |
| Current assessment | What condition is it in? | `ASSESSMENT.md` | Living |
| Architecture | How is it actually built? | `ARCHITECTURE.md` | Living |
| Change history | What changed? | `CHANGELOG.md` | Living |
| Defect tracking | What is currently broken? | `ISSUES.md` | Living |
| Technical debt | What compromises should be improved? | `TECH-DEBT.md` | Living |
| Deferred improvements | What might be worth doing later? | `FUTURE-UPGRADES.md` | Living |
| Validation | How do we prove it works? | `VALIDATION.md` | Living |
| Operations | How do we run and recover it? | `OPERATIONS.md` | Living |
| Requirement traceability | Where does each requirement live? | `TRACEABILITY.md` | Living |
| Agreed scope | What did we agree to build? | `REQUIREMENTS.md` | Contractual |
| Agreed design | What did we agree it would look like? | `DESCRIPTOR.md` | Contractual |
| Scope amendments | What did we agree to change? | `AMENDMENTS.md` | Contractual |
| Decision history | Why were major decisions made? | `docs/decisions/` | Derived |
| Resolved history | What was fixed, resolved, delivered? | `docs/archive/` | Derived |
| Development rules | What rules govern this repository? | `PROJECT-STANDARD.md` | Governance |
| Agent rules | What must AI agents do? | `AGENTS.md` | Governance |

### The Authority Rule

**Exactly one authority per responsibility. Mandatory, single-valued, and declared.**

An existing document may satisfy a responsibility when explicitly mapped. If `docs/system-design.md` already serves the architecture responsibility, keep it and map it. Do not create `ARCHITECTURE.md` alongside it.

What is not permitted is leaving a responsibility partially covered by several documents. Responsibility-based mapping without single-valued authority produces fourteen scattered files each answering part of a question, which is worse than a rigid filename rule.

### Authority Mapping

Declared in PROJECT-STANDARD.md, maintained alongside `.docs-authority.json` (see Compliance). This table is the resolution layer: **everything else in the standard, including the routing table and the agent rules, refers to responsibilities and resolves them through this table.**

```markdown
## Authority Mapping

| Responsibility | Authority | Notes |
|---|---|---|
| Project overview | README.md | |
| Current assessment | ASSESSMENT.md | |
| Architecture | docs/system-design.md | Pre-existing; adopted 2026-04-02 |
| Change history | CHANGELOG.md | |
| Validation | docs/testing-guide.md | Pre-existing; adopted 2026-04-02 |
| Defect tracking | External tracker | Out of repository scope; see note |
| Technical debt | TECH-DEBT.md | |
| Deferred improvements | FUTURE-UPGRADES.md | |
| Operations | Not required at this tier | |
```

Three legitimate values for an authority: a path in this repository, an explicit external system, or `Not required at this tier`. Anything else is a compliance gap.

---

## Document Classes

The most consequential distinction in this standard. Applying living rules to a contractual document destroys the only mechanism available for detecting scope drift.

| Class | Nature | Review question | Action on mismatch |
|---|---|---|---|
| **Living** | Current truth | Is this still accurate? | Update the document |
| **Contractual** | Agreement at a point in time | Did we drift from this? | Amend, descope, or fix the code |
| **Derived** | Historical record | Is a new record required? | Append; never edit existing entries |
| **Governance** | Rules of the repository | Did the method change? | Update and version |

Contractual documents are read constantly during implementation and written rarely. That is the opposite of the living set, and it is why they need their own rules rather than an exemption from someone else's.

---

## Source-of-Truth Hierarchy

When sources disagree, this resolves it. **The hierarchy is scoped by the question being asked.** A single flat hierarchy would let code silently override agreed scope, which inverts the entire purpose of the contractual class.

### For "what does the system do?"

```text
Executable repository state
        ↓
Configuration and schemas
        ↓
Tests
        ↓
Architecture and validation documentation
        ↓
Current assessment
        ↓
README summaries
```

**Rule.** When documentation conflicts with verifiable repository behavior, the repository governs and the stale documentation is corrected.

### For "what should the system do?"

```text
Requirements and amendments
        ↓
Descriptor
        ↓
Architecture and validation documentation
        ↓
Everything else
```

**Rule.** When implementation conflicts with agreed scope, agreed scope governs the question of intent. The code does not become correct by existing.

### When the two hierarchies conflict

This is the important case, and it has its own rule:

> A conflict between what the system does and what it was agreed to do is **not a documentation error**. It is a scope finding. It is recorded in the traceability authority, surfaced in the assessment authority, and escalated for a decision. It is never resolved by editing either side to match the other.

Three legitimate resolutions: amend the agreement, change the code, or accept the divergence on the record. Silently reconciling the documents is not one of them.

---

## Project Tiers

The most common failure of a documentation standard is applying full ceremony to a project that cannot justify it. Tier is a deliberate promotion decision, not a default.

| Responsibility | Tier 0 | Tier 1 | Tier 2 | Tier 2C |
|---|---|---|---|---|
| Project overview | Required | Required | Required | Required |
| Change history | Required | Required | Required | Required |
| Agent rules | If agents used | Required | Required | Required |
| Development rules | — | Required | Required | Required |
| Current assessment | — | Required | Required | Required |
| Technical debt | — | Required | Required | Required |
| Deferred improvements | — | Required | Required | Required |
| Validation | — | Required | Required | Required |
| Architecture | — | Optional | Required | Required |
| Defect tracking | — | Optional | Required | Required |
| Operations | — | — | Required | Required |
| Decision history | — | Optional | Required | Required |
| Resolved history | — | Optional | Required | Required |
| Agreed scope | — | — | — | Required |
| Agreed design | — | — | — | Required |
| Scope amendments | — | — | — | Required |
| Requirement traceability | — | — | — | Required |

- **Tier 0 — Utility.** Single script or a few files, one maintainer, no integrations, no deployment.
- **Tier 1 — Tool.** Multiple modules, reused by others, limited integrations.
- **Tier 2 — System.** Deployed, integrated, multiple contributors, operational consequences on failure.
- **Tier 2C — Client Project.** Tier 2 plus a client or stakeholder with agreed scope and delivery sign-off.

An internal automation repository with no client and no agreed scope does not use Tier 2C. Forcing contractual documents onto a repository with no counterparty is exactly the over-application the tier system exists to prevent.

### Tier Declaration

```markdown
**Standard version:** 2.2
**Project tier:** 2C
**Tier rationale:** Client engagement with agreed scope, deployed integration, delivery sign-off required.
**Promotion trigger:** N/A — highest tier.
```

Promotion is additive. Demotion requires archiving, not deleting, the documents no longer maintained, with a header noting the date maintenance stopped.

---

## Anti-Duplication Rule

The following must be a link, not content:

- Project overview "Known Limitations" links to defect tracking and technical debt.
- Project overview "Current Status" carries status, version, and tier only. Health belongs to the assessment.
- Assessment "Recently Changed" links to change history.
- Assessment "Recommended Improvements" references TD and FU identifiers only.
- Assessment "Requirement Coverage" summarizes counts and links to traceability.
- Architecture "Planned Evolution" references FU identifiers only.
- Anything appearing verbatim in two documents is a defect in one of them.

### Agreed design vs. architecture

The single most likely duplication failure in a client project. Two competing architecture documents are worse than either alone.

The descriptor is the agreed pre-build design. It seeds the architecture authority on the first day of implementation and is then frozen forever. From that point the architecture authority is current truth and the descriptor is the agreement. When they diverge, that is a scope finding, not a correctable error.

---

# Part II — Process

## Change Classes

Classes determine **how much process** a change requires. Change types determine **which specific validation** applies. Both are needed; neither replaces the other.

| Class | Name | Examples |
|---|---|---|
| **0** | Trivial | Formatting, whitespace, typo fixes, local variable renames, ignore-list additions, generated-output refresh with no input change, version bumps with no behavior change |
| **1** | Documentation | Human-facing documentation changes only, no code touched |
| **2** | Internal implementation | Refactors, internal behavior changes, test additions, no interface change |
| **3** | Functional | Features, bug fixes, dependency changes, configuration changes, interface and API changes |
| **4** | Architectural / Security | Architecture, authentication, authorization, data model, trust boundary, deployment, major dependency, security control changes |

### Process Weight by Class

| | Class 0 | Class 1 | Class 2 | Class 3 | Class 4 |
|---|---|---|---|---|---|
| Read routed documents | No | Target only | Yes | Yes | Yes |
| Read agent handoff | No | No | Yes | Yes | Yes |
| Identify governing requirement (2C) | No | No | If applicable | Yes | Yes |
| Validation | None | None | Basic | Per matrix | Full per matrix |
| Changelog fragment | No | If meaningful | Yes | Yes | Yes |
| Update traceability (2C) | No | No | If mapping changed | Yes | Yes |
| ADR required | No | No | No | If a decision is made | Presumed yes |
| Assessment refresh on merge | No | No | Yes | Yes | Yes |
| Second reviewer | No | No | No | Recommended | Required where practical |

Class 4 presumes an ADR. Not writing one is a decision that should be stated, not a default.

### Change Type to Class

| Change type | Class | Read (by responsibility) | Review after |
|---|---|---|---|
| Formatting, typo, ignore-list | 0 | Nothing | Nothing |
| Documentation only | 1 | Target document | Target document |
| Internal refactor | 2 | Architecture, technical debt, validation | Change history, technical debt, assessment |
| Test-only change | 2 | Validation | Change history, validation |
| Bug fix | 3 | Assessment (handoff), validation, defect tracking | Change history, defect tracking, traceability, assessment |
| New feature | 3 | Agreed scope, overview, architecture, validation, deferred improvements | Overview, change history, architecture, traceability, assessment |
| Requirement implementation | 3 | Agreed scope, agreed design, amendments, architecture, validation | Change history, traceability, architecture, validation, assessment |
| Interface / API change | 3 | Agreed scope, overview, architecture, validation | Overview, change history, architecture, traceability, validation, assessment |
| Dependency change | 3 | Architecture, technical debt, validation | Change history, architecture, technical debt, assessment |
| Configuration change | 3 | Operations, architecture, validation | Change history, operations, assessment |
| Architecture change | 4 | Agreed design, architecture, decision history, validation | Change history, architecture, decision history, traceability, assessment |
| Security change | 4 | Agreed scope, architecture, validation, operations | Change history, architecture, validation, operations, assessment |
| Deployment change | 4 | Operations, architecture, validation | Change history, operations, architecture, assessment |
| Scope change | 4 | Agreed scope, amendments, agreed design | Amendments, traceability, deferred improvements, assessment, change history |

Read lists name **responsibilities**, resolved through the Authority Mapping. An agent reads the authority, whatever its filename.

---

## Meaningful Change

Class 0 changes are not meaningful and skip the lifecycle entirely. Everything Class 1 and above is meaningful.

If you find yourself arguing that a change is technically Class 2 rather than Class 0, it is Class 2. If you find yourself arguing that it is technically Class 0, ship it and move on.

---

## The Evidence Rule

Every factual claim in living documentation must be one of:

1. **Derived** — traceable to a file, command output, or configuration in the repository.
2. **Stated as unverified** — explicitly marked.
3. **Absent.**

`Not assessed` is a correct and useful value. An agent that cannot run a security scan writes `Security: Not assessed (no scanning tooling available in this environment)`. It does not write a security judgment.

### Inline Evidence Citation

Material claims carry their source inline. This applies to the assessment health lines and, from 2.2, to the architecture authority, which is the document most prone to confident invention.

```markdown
## Authentication and Authorization

Authentication: OAuth 2.0 client credentials flow
Evidence: src/auth/oauth.py:14-88, config/auth.yaml

Authorization: role claims evaluated at the API boundary
Evidence: src/api/middleware/authz.py, tests/Authz.Tests.ps1
```

Never carry a prior conclusion forward under a new date:

```markdown
- Tests: PASS as of 2026-08-14 (commit a1b2c3d) — not re-run since
```

This rule overrides every template in this document. A template heading with no evidence behind it is deleted, not filled.

---

## Validation: Procedure vs. Evidence

Two different things that must not share a home.

| | Where it lives | Nature |
|---|---|---|
| **Validation procedure** | Validation authority | Living. How to prove correctness |
| **Validation evidence** | Commit, PR, or agent completion report | Per-change. What was actually executed |

The validation authority is never a log of runs. Execution evidence travels with the change, which keeps it verifiable and prevents an ever-growing results file nobody reads.

Required evidence fields per change:

```text
Command:
Result:            PASS | FAIL | BLOCKED | SKIPPED
Exit code:
Tests passed:
Tests failed:
Tests skipped:
Reason skipped:
```

`Tests skipped` and `Reason skipped` are mandatory when nonzero. A suite reporting 40 passed and 7 skipped is not a passing suite until someone knows why the 7 were skipped.

---

## Waivers

Real projects cannot always follow the rule. The alternative to a waiver mechanism is an agent that either fails an entire task over an unavailable linter or silently ignores the requirement. Both are worse than recording it.

### Grounds

A requirement may be waived when required tooling is unavailable, validation cannot execute safely, repository permissions prevent an action, an external dependency is unavailable, or the environment cannot reproduce the conditions the check requires.

Not grounds: time pressure, inconvenience, or a judgment that the check is unnecessary.

### Transient vs. Standing

**Transient waiver** — this change, this environment. Recorded in the completion report and nowhere else.

```text
WAIVED  Integration suite
  Requirement: Class 3 requires integration validation
  Reason:      Tenant credentials not present in this environment
  Risk:        Integration regressions would not be caught by this change
  Follow-up:   Run before merge to main
```

**Standing waiver** — the condition will not resolve on its own. A transient waiver recorded three times is a standing waiver that nobody promoted.

Standing waivers live in one of two places and must be visible in the assessment:

- The validation authority's "Known Validation Limitations" section, when the gap is procedural
- An `Accepted` technical debt entry with a fix trigger, when the gap is a real reduction in assurance

**Rule.** A standing waiver is a permanent reduction in assurance. It belongs in the assessment's health section, not buried in a commit message from March. The assessment names the count of standing waivers and links to each.

---

## Mandatory Development Lifecycle

```text
START TASK
    │
    ▼
Read agent rules; classify the change (Class 0-4)
    │
    ├── Class 0 ──► Implement. Done.
    │
    ▼
Resolve routed responsibilities through the Authority Mapping
    │
    ▼
Read only those authorities, plus the assessment's Agent Handoff
    │
    ▼
[Tier 2C] Identify the governing requirement, or state that none exists
    │
    ▼
Inspect relevant repository content; understand existing behavior
    │
    ▼
Class 4, or a significant decision? ──► Write ADR (Proposed) BEFORE implementing
    │
    ▼
Would this contradict agreed scope? ──► STOP. Raise it. Amend or redesign.
    │
    ▼
Implement smallest coherent change
    │
    ▼
Run validation per class and matrix
    │
    ├── Cannot run? ──► Record a waiver. Do not skip silently.
    │
    ▼
Review documentation impact for routed authorities only
    │
    ▼
Update stale authorities; update traceability; add changelog fragment
    │
    ▼
Final consistency check against the Source-of-Truth Hierarchy
    │
    ▼
TASK COMPLETE
```

ADRs move to `Accepted` when the change merges.

### The Requirement Review Step

At Tier 2C, every Class 2 and above change answers three questions before it is complete:

1. **Does this implement a requirement?** Update traceability with the files and validation that now satisfy it.
2. **Does this contradict a requirement?** Stop. Do not proceed on the assumption that the requirement was wrong. Raise it.
3. **Did agreed scope actually change?** Record an amendment. Never adjust the agreed scope authority in place.

This is the step that catches silent scope drift. It costs a minute per change and is effectively impossible to reconstruct at delivery.

---

## Branching and Merge Policy

Documentation on a single shared file becomes a merge-conflict generator the moment two branches are open. This standard removes that friction structurally.

**The change history authority is never edited on a feature branch.** Each change adds a fragment:

```text
changelog.d/2026-08-27-fix-token-refresh.md
```

```markdown
### Fixed
- Token refresh no longer retries indefinitely when the identity endpoint returns 401. (REQ-014)
```

Fragments are concatenated into the changelog at release, or on a monthly cadence for repositories that never release, and then deleted.

**The assessment authority is updated on the main branch only.** A feature branch does not touch it. This is the single most important change for making the standard survivable in a team, and it means the assessment reflects a real integrated state rather than an in-flight one.

**Traceability is updated on the branch** implementing the requirement, since the mapping is only knowable there. Conflicts are rare because rows are keyed by REQ identifier and do not overlap.

**Contractual authorities are never edited on a feature branch.** Amendments are a deliberate act with their own commit and their own approval.

**Documentation updates travel in the same commit as the change that made them necessary.**

---

## Compliance and Staleness Detection

A discipline-based standard with no detection mechanism decays silently, and a self-reported compliance table becomes checkbox theater within two months. **Compliance status is derived, never asserted.**

### `.docs-authority.json`

The machine-readable form of the Authority Mapping. Maintained alongside PROJECT-STANDARD.md; the two must agree.

```json
{
  "standardVersion": "2.2",
  "tier": "2C",
  "sourcePaths": ["src", "lib", "scripts"],
  "maxDriftDays": 30,
  "responsibilities": {
    "Project overview":         { "authority": "README.md",              "class": "living" },
    "Current assessment":       { "authority": "ASSESSMENT.md",          "class": "living" },
    "Architecture":             { "authority": "docs/system-design.md",  "class": "living" },
    "Change history":           { "authority": "CHANGELOG.md",           "class": "living" },
    "Defect tracking":          { "authority": "ISSUES.md",              "class": "living" },
    "Technical debt":           { "authority": "TECH-DEBT.md",           "class": "living" },
    "Deferred improvements":    { "authority": "FUTURE-UPGRADES.md",     "class": "living" },
    "Validation":               { "authority": "docs/testing-guide.md",  "class": "living" },
    "Operations":               { "authority": "OPERATIONS.md",          "class": "living" },
    "Requirement traceability": { "authority": "TRACEABILITY.md",        "class": "living" },
    "Agreed scope":             { "authority": "REQUIREMENTS.md",        "class": "contractual" },
    "Agreed design":            { "authority": "DESCRIPTOR.md",          "class": "contractual" },
    "Scope amendments":         { "authority": "AMENDMENTS.md",          "class": "contractual" },
    "Agent rules":              { "authority": "AGENTS.md",              "class": "governance" }
  }
}
```

### `scripts/docs-check.ps1`

Verifies that every required responsibility has a resolvable authority, and reports drift for living authorities only. Contractual documents are frozen by design; flagging them as drifted would train everyone to ignore the warnings.

```powershell
#Requires -Version 7.0
[CmdletBinding()]
param(
    [string]$ConfigPath = '.docs-authority.json',
    [switch]$FailOnGap,
    [switch]$Markdown
)

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Authority map not found at $ConfigPath. This repository is not compliant."
    exit 1
}

$config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
$maxDrift = if ($config.maxDriftDays) { [int]$config.maxDriftDays } else { 30 }

function Get-LastCommitDate {
    param([string]$Path)
    $iso = git log -1 --format=%cI -- $Path 2>$null
    if ([string]::IsNullOrWhiteSpace($iso)) { return $null }
    return [datetime]::Parse($iso)
}

$sourceDate = $config.sourcePaths |
    ForEach-Object { Get-LastCommitDate -Path $_ } |
    Where-Object { $_ } |
    Sort-Object -Descending |
    Select-Object -First 1

$rows = foreach ($name in $config.responsibilities.PSObject.Properties.Name) {
    $entry     = $config.responsibilities.$name
    $authority = $entry.authority
    $class     = $entry.class

    if ($authority -in @('Not required at this tier', 'External tracker')) {
        [pscustomobject]@{ Responsibility = $name; Authority = $authority; Status = 'N/A'; LastUpdated = '' }
        continue
    }

    if (-not (Test-Path $authority)) {
        [pscustomobject]@{ Responsibility = $name; Authority = $authority; Status = 'MISSING'; LastUpdated = '' }
        continue
    }

    $docDate = Get-LastCommitDate -Path $authority
    $updated = if ($docDate) { $docDate.ToString('yyyy-MM-dd') } else { 'uncommitted' }

    # Contractual and governance documents are frozen by design; drift is expected.
    if ($class -ne 'living' -or -not $sourceDate -or -not $docDate) {
        [pscustomobject]@{ Responsibility = $name; Authority = $authority; Status = 'Current'; LastUpdated = $updated }
        continue
    }

    $drift  = [int]($sourceDate - $docDate).TotalDays
    $status = if ($drift -gt $maxDrift) { "REVIEW (${drift}d)" } else { 'Current' }

    [pscustomobject]@{ Responsibility = $name; Authority = $authority; Status = $status; LastUpdated = $updated }
}

if ($Markdown) {
    '| Responsibility | Authority | Last updated | Status |'
    '|---|---|---|---|'
    $rows | ForEach-Object { "| $($_.Responsibility) | $($_.Authority) | $($_.LastUpdated) | $($_.Status) |" }
} else {
    $rows | Format-Table -AutoSize
}

$gaps = $rows | Where-Object { $_.Status -eq 'MISSING' -or $_.Status -like 'REVIEW*' }
if ($gaps -and $FailOnGap) { exit 1 }
```

### Compliance Table

Generated by `docs-check -Markdown` and pasted into the assessment authority. It is never hand-written.

```markdown
## Living Documentation Compliance

Generated by scripts/docs-check.ps1 on 2026-08-27.

| Responsibility | Authority | Last updated | Status |
|---|---|---|---|
| Project overview | README.md | 2026-08-20 | Current |
| Architecture | docs/system-design.md | 2026-06-02 | REVIEW (86d) |
| Operations | OPERATIONS.md | — | MISSING |
```

`REVIEW` is a prompt to look, not proof of staleness. A document can be correct and untouched for a year. The script's job is to make that a conscious judgment rather than an oversight.

Wire it into a local pre-push hook or a scheduled review. Do not make it block a merge until the team has lived with its warnings for a while.

---

# Part III — Document Standards

Templates below use canonical filenames for readability. Each applies to whichever authority the mapping names.

## Project Overview — `README.md`

````markdown
# Project Name

One-sentence description of what the project does.

## Overview

What problem it solves and why it exists.

## Current Status

- Status: Active | Maintenance | Deprecated
- Version:
- Project tier:
- Primary technologies:
- Owner:

For current repository health, see [ASSESSMENT.md](ASSESSMENT.md).

## Key Capabilities

## Architecture Summary

Two or three sentences. See the architecture authority.

## Repository Structure

## Getting Started

Installation, configuration, and first successful run.

## Validation

The normal command to prove a change works. See the validation authority.

## Documentation

See the Authority Mapping in [PROJECT-STANDARD.md](PROJECT-STANDARD.md) for the
authoritative source of each documentation responsibility.

## Known Limitations

See the defect tracking and technical debt authorities. Only limitations that
change how a user should approach the project belong here.
````

Update when the change affects purpose, capabilities, installation, setup, usage, commands, configuration, supported platforms, dependencies, deployment, status, or the architecture summary.

---

## Current Assessment — `ASSESSMENT.md`

Current truth about repository health. Carries no history. Governed by the Evidence Rule.

````markdown
# Repository Assessment

**Last full assessment:** 2026-08-27
**Assessed at commit:** a1b2c3d
**Basis:** Invoke-Pester (47 pass / 0 fail), PSScriptAnalyzer (3 warnings), manual review of src/
**Assessed by:** Human | Agent

## Executive Summary

Three to five sentences. What state is this repository in and what should happen next.

## Agent Handoff

The single most important section. Read on every Class 2+ task.

- What a developer or agent must know before touching this repository
- Traps, fragile areas, non-obvious constraints
- What the last significant change did and what it left unfinished

## Living Documentation Compliance

Generated by scripts/docs-check.ps1. Never hand-written.

## Current Health

Each line carries its basis and date, or reads "Not assessed".

- Build: PASS — 2026-08-27, `dotnet build` exit 0
- Tests: PASS — 2026-08-27, 47/47, 0 skipped
- Lint: WARN — 2026-08-27, 3 PSScriptAnalyzer warnings, see TD-004
- Security: Not assessed — no scanning tooling available in this environment
- Dependencies: 2 minor updates available — 2026-08-27
- Standing waivers: 2 (see below)

## Standing Waivers

Permanent reductions in assurance. Each links to its validation limitation or
accepted debt entry.

- Integration suite cannot run locally — no tenant credentials. See VALIDATION.
- No SAST tooling available in this environment. See TD-009 (Accepted).

## Requirement Coverage

Tier 2C only. Counts and exceptions. Detail lives in the traceability authority.

## Scope Divergence

Tier 2C only. Where the built system differs from the agreed design, and whether
each divergence has been agreed.

## Current Capabilities

What the repository actually does today. Not what it is intended to do.

## Known Issues and Risks

Risk narrative only. Individual defects live in the defect tracking authority.

## Technical Debt Summary

Count and severity distribution only.

## Recently Changed

See the change history authority.

## Current Priorities

Ordered. Reference REQ, TD, and FU identifiers rather than restating them.

## Repository Limitations
````

Refresh on the main branch after merge. Rewrite stale sections rather than appending. Never a chronological diary.

---

## Architecture — `ARCHITECTURE.md`

Include only sections that apply; delete the rest. **Material claims carry inline evidence.**

```markdown
# Architecture

## System Overview
## Architecture Diagram
## Major Components
## Application Entry Points
## Data Flow
## External Integrations
## Data Storage
## Configuration
## Authentication and Authorization
## Error Handling
## Logging and Observability
## Background Processing
## Deployment Architecture
## Significant Dependencies
## Security Architecture
## Architectural Constraints
## Architectural Decisions           (index of ADRs)
## Known Architectural Limitations
## Divergence from Agreed Design     (Tier 2C only)
## Planned Evolution                 (FU identifiers only)
```

Diagrams drift faster than prose. Keep them coarse enough to survive ordinary refactoring, or generate them from source.

Configuration examples use placeholder values only. Never a real hostname, tenant identifier, account name, or path revealing internal topology.

Update when components, interfaces, data flow, storage, major dependencies, configuration architecture, authentication, trust boundaries, background processing, deployment, or external integrations change. Not merely because source code changed.

---

## Change History — `CHANGELOG.md`

For repositories that cut releases, use versioned sections. For repositories that never release, use date-stamped sections rather than an `Unreleased` block that never closes.

```markdown
# Changelog

## 2026-08 (unreleased)

### Added
### Changed
### Fixed
### Removed
### Security
```

At Tier 2C, entries reference the governing requirement or amendment where one exists.

---

## Defect Tracking — `ISSUES.md`

Technical debt is not a bug tracker, so bugs need a home. A repository either maintains this authority or maps it to a named external system.

Identifiers are permanent and never reused: `BUG-001`.

```markdown
### BUG-001 — Short Title

**Status:** Open | Investigating | Fixed | Won't Fix
**Severity:** Low | Medium | High | Critical
**Reported:** YYYY-MM-DD
**Area:** Component
**Violates:** REQ-014   (Tier 2C, when the defect breaks an agreed requirement)

**Symptom**
**Reproduction**
**Expected**
**Workaround**
**Resolution**
```

A defect violating an agreed requirement is not an ordinary bug. It is a delivery risk and surfaces in the assessment.

Fixed issues move to the resolved history authority once shipped and verified.

---

## Technical Debt — `TECH-DEBT.md`

> Technical debt: the implementation currently works, but some aspect of it should eventually be improved because the current approach creates future cost, complexity, fragility, or risk.

### Scope vs. Bug vs. Debt vs. Upgrade

In order:

1. Was it never agreed to in the first place? → **Scope** (amendments, then deferred improvements)
2. Does it not work as intended? → **Bug** (defect tracking)
3. Does the work reduce cost, risk, or fragility in something already shipped? → **Debt**
4. Does the work add capability that does not exist yet? → **Upgrade** (deferred improvements)
5. Both 3 and 4? → File as **Debt**, cross-reference the FU.

Missing test coverage for shipped code is debt. A new test framework is an upgrade. Replacing a deprecated library is debt. Replacing a working library with a better one is an upgrade.

```markdown
### TD-001 — Short Title

**Status:** Open | Accepted | Resolved
**Severity:** Low | Medium | High | Critical
**Area:** Component or concern
**Introduced/Discovered:** YYYY-MM-DD
**Standing waiver:** Yes | No

**Related files**
**Description**
**Why it exists**
**Impact**
**Recommended resolution**
**Fix trigger**
**Estimated effort:** Small | Medium | Large
```

`Accepted` is a valid terminal state. Debt the team has consciously decided to live with should say so, rather than sitting Open forever and eroding the file's credibility.

Resolved debt moves to the resolved history authority with its resolution date and the change that resolved it. Never silently deleted, never left in the working file.

---

## Deferred Improvements — `FUTURE-UPGRADES.md`

```markdown
### FU-001 — Short Title

**Status:** Proposed | Planned | In Progress | Rejected
**Priority:** Low | Medium | High
**Area:** Component or concern
**Origin:** Internal | Descoped requirement REQ-030 via AMD-003

**Opportunity**
**Potential benefit**
**Why deferred**
**Trigger**
**Estimated effort:** Small | Medium | Large
**Dependencies**
```

`Implemented` is deliberately absent. Implemented upgrades move to the resolved history authority and are removed from this file.

Descoped requirements arriving here always carry their `Origin`. A deferred contractual obligation is a different thing from an idea someone had.

---

## Validation — `VALIDATION.md`

The authoritative runbook. Not a log of runs. Include only applicable sections; empty headings train readers to skim.

```markdown
# Validation

## Validation Levels

### Basic
### Integration
### Full

## Environment Requirements
## Setup

## Commands

For each: the exact command, expected exit code, expected output shape, typical runtime.

## Acceptance Validation

Tier 2C only. How each requirement's acceptance criteria are demonstrated and what
constitutes client sign-off.

## Known Validation Limitations

Standing waivers of procedural origin. Mandatory; must not be empty without
justification. Each entry states what cannot be validated, why, and the risk.

## Validation Matrix
```

| Change type | Class | Unit | Integration | Security | Smoke | Acceptance |
|---|---|---|---|---|---|---|
| Documentation only | 1 | No | No | No | No | No |
| Internal refactor | 2 | Yes | As needed | No | Yes | No |
| Bug fix | 3 | Yes | As needed | No | Yes | If REQ-linked |
| Requirement implementation | 3 | Yes | Yes | As needed | Yes | Yes |
| Interface change | 3 | Yes | Yes | As needed | Yes | As needed |
| Dependency change | 3 | Yes | Yes | Yes | Yes | No |
| Architecture change | 4 | Yes | Yes | Yes | Yes | As needed |
| Security change | 4 | Yes | Yes | Yes | Yes | As needed |
| Deployment change | 4 | Yes | Yes | Yes | Yes | As needed |

**Hard rule.** Validation is never claimed on the basis of code inspection. If a command was not executed, it is reported as `BLOCKED` or `WAIVED` with a reason.

---

## Operations — `OPERATIONS.md`

Validation proves the code is correct; operations covers running it in the real world. For scheduled jobs, connectors, and integration workflows, this is usually the document people actually need at 2am.

```markdown
# Operations

## Runtime Environment
## Deployment Procedure
## Rollback Procedure
## Configuration and Secrets Management

Where secrets live and how they are rotated. Never the secrets themselves.

## Scheduling and Triggers
## Monitoring and Alerting
## Log Locations and Retention
## Common Failure Modes

For each: symptom, cause, resolution.

## Recovery Procedures
## Escalation Path
## Maintenance Windows
## Support Handover

Tier 2C only. What the client or support team receives and is responsible for.
```

---

## Agreed Scope — `REQUIREMENTS.md`

Contractual. Frozen at baseline, changed only through amendments. Scaffolded at repository creation even when nothing has been gathered: an empty placeholder is a standing obligation; a missing file reads as "not applicable."

````markdown
# Requirements

**Status:** Not yet gathered | Draft | Baselined | Superseded
**Revision:** 3
**Baselined:** 2026-04-02
**Client / stakeholder:**
**Approved by:**

> Contractual document. Never edited to match what was built. Changes to agreed
> scope are recorded in the amendments authority and increment the revision above.

## Scope Summary

## Out of Scope

Explicit exclusions. This section prevents more disputes than the requirements themselves.

## Assumptions

What the requirements depend on being true. Each is a risk if it fails.

## Constraints

## Functional Requirements

### REQ-001 — Short Title

**Priority:** Must | Should | Could | Won't (this phase)
**Status:** Agreed | Amended | Descoped
**Source:** Client meeting 2026-03-14 | Descriptor section 4.2
**Amended by:** AMD-002   (present only when amended)

**Requirement**
What the system must do. One requirement per identifier. If it contains "and",
consider splitting it.

**Acceptance criteria**
How the client will confirm this is satisfied. Testable statements only.

**Notes**

## Non-Functional Requirements

Performance, availability, security, retention, compliance, supportability. Same
identifier series. These are the requirements most often omitted and most often
disputed at delivery.

## Requirement Index

| ID | Title | Priority | Status |
|---|---|---|---|
````

Identifiers are permanent and never reused. Descoped requirements keep their entry with `Status: Descoped` and a pointer to the amendment. A requirement that vanishes without a trace is the exact thing this document exists to prevent.

**No commercial terms.** Pricing, payment schedules, statement-of-work legal language, and liability clauses do not belong in a code repository.

---

## Agreed Design — `DESCRIPTOR.md`

````markdown
# Project Descriptor

**Status:** Frozen
**Agreed:** 2026-04-02
**Seeded architecture authority:** 2026-04-08

> Frozen. Describes the solution as agreed before implementation. Not updated as
> the system evolves. For current design, see the architecture authority.
> Divergence is expected and is reported in the assessment, not corrected here.

## Solution Overview
## Intended Architecture
## Component Breakdown
## Data Model
## Integration Points
## Interface Contracts
## Security Model
## Deployment Model
## Operational Expectations
## Dependencies and Prerequisites
## Deliverables
## Acceptance Approach
## Explicit Non-Goals
````

The temptation to keep this current is strong and must be resisted. If the design changes materially before implementation begins, reissue with a new agreed date and record it as an amendment.

---

## Scope Amendments — `AMENDMENTS.md`

Append-only.

````markdown
# Scope Amendments

### AMD-001 — Short Title

**Date:** 2026-05-19
**Requested by:** Client | Delivery team
**Approved by:** Name, role
**Affects:** REQ-014, REQ-015
**Type:** Addition | Modification | Descope | Clarification

**Change**
**Reason**
**Impact**

**Resulting requirement state**
- REQ-014: Amended, see revision 3
- REQ-015: Descoped, moved to FU-009
````

Descoped requirements go to amendments first, then to deferred improvements. Never directly to deferred improvements, or the descoping becomes invisible and a deferred obligation looks like an idea someone had.

---

## Requirement Traceability — `TRACEABILITY.md`

Living. The bridge between agreed scope and shipped code.

````markdown
# Requirement Traceability

**Last verified:** 2026-08-27 (commit a1b2c3d)
**Reconstructed:** No | Yes, on YYYY-MM-DD

## Coverage Summary

- Agreed requirements: 42
- Implemented and validated: 31
- Implemented, validation pending: 4
- In progress: 3
- Deferred: 2
- Descoped: 2

## Matrix

| REQ | Status | Implementation | Validation | Evidence |
|---|---|---|---|---|
| REQ-001 | Validated | `src/Auth/TokenClient.ps1` | `tests/Auth.Tests.ps1` | Pester 2026-08-27, pass |
| REQ-014 | Implemented | `src/Sync/Runner.ps1` | Manual, not automated | Standing waiver |
| REQ-030 | Deferred | — | — | AMD-003, FU-009 |

## Unmapped Implementation

Significant functionality mapping to no requirement. Each entry is either an
undocumented amendment or scope creep. Both need a decision.

- `src/Export/CsvWriter.ps1` — added 2026-06-11, no governing REQ
````

The Unmapped Implementation section is the one people leave out and the one that earns its keep. Scope creep is easier to see from the code side than from the requirement side.

Never reconstructed at delivery; the reconstruction is always wrong and always takes longer than the incremental work would have.

---

## Decision History — `docs/decisions/`

Write the ADR before implementing, not after. Class 4 changes presume an ADR.

`docs/decisions/README.md` contains the index and nothing else:

```markdown
# Architecture Decisions

| ID | Title | Status | Date | Drives | Supersedes | Superseded by |
|---|---|---|---|---|---|---|
| ADR-001 | Use SQLite for local state | Accepted | 2026-03-04 | REQ-008 | — | — |
| ADR-002 | Poll instead of webhook | Superseded | 2026-05-11 | REQ-014 | — | ADR-007 |
| ADR-007 | Webhook with polling fallback | Accepted | 2026-07-22 | REQ-014 | ADR-002 | — |
```

```markdown
# ADR-001 — Decision Title

**Status:** Proposed | Accepted | Superseded | Rejected
**Date:** YYYY-MM-DD
**Driving requirement:** REQ-008   (Tier 2C, where applicable)
**Supersedes:** ADR-###            (when this replaces an earlier decision)
**Superseded by:** ADR-###         (required when status is Superseded)

## Context
## Decision
## Rationale
## Alternatives Considered
## Consequences
## Related
```

**Immutability rule.** An `Accepted` ADR is immutable except for its status line and cross-reference fields. A changed decision requires a new ADR that supersedes it. Never edit the context, decision, or rationale of an accepted ADR; doing so destroys the record of what was actually known and decided at the time.

Supersession is reciprocal. Both ADRs and the index are updated together.

---

## Resolved History — `docs/archive/`

Append-only. Entries carry resolution date and a link to the change that resolved them.

```text
docs/archive/
├── RESOLVED-DEBT.md
├── RESOLVED-ISSUES.md
└── COMPLETED-UPGRADES.md
```

---

## Agent Rules — `AGENTS.md`

### Instruction File Authority

Multiple agent instruction files will diverge, and an agent faithfully following a stale copy is worse than an agent with no instructions. **The agent rules authority is single-valued like every other.** Every other instruction file contains a pointer and nothing else:

```markdown
See AGENTS.md. It is the authoritative agent instruction file for this repository.
```

### Recommended Content

````markdown
# AI Agent Repository Rules

Standard version: 2.2
Project tier: 2C

## Authority Resolution

This file names documentation responsibilities, not filenames. Resolve every
responsibility through the Authority Mapping in PROJECT-STANDARD.md before
reading or writing. Never create a document that duplicates an existing authority.

## Document Classes

Living       — current truth. Rewrite when reality diverges.
Contractual  — agreed scope, agreed design, amendments. Frozen. Never rewritten
               to match what was built. Divergence is a finding. Changes are
               amendments.
Derived      — decision history and archive. Append-only.

## Source of Truth

For what the system does: repository state governs; stale documentation is corrected.
For what the system should do: agreed scope governs; code does not become correct
by existing.
When these conflict: that is a scope finding. Record it, surface it, escalate it.
Never resolve it by editing either side to match the other.

## Startup

1. Read this file.
2. Classify the change (Class 0-4).
3. Class 0: implement and stop. No documentation lifecycle.
4. Class 1+: resolve routed responsibilities through the Authority Mapping.
5. Read only those authorities, plus the assessment's Agent Handoff.
6. Class 2+ at Tier 2C: identify the governing requirement, or state none exists.
7. Inspect the relevant implementation before editing.

Do not read the full documentation set on every task.

## Requirement Rules

- Every Class 2+ change identifies its governing REQ, or states that none exists.
- Unmapped implementation is recorded in traceability and requires a decision.
- If the change would contradict an agreed requirement, stop and raise it.
- Never edit the agreed scope authority in place. Scope changes are amendments.
- Update traceability whenever implementation or validation status changes.

## Evidence Rules

- Never claim a test, lint, build, or scan passed unless the command was executed
  in this session.
- Report the command, exit code, and counts including tests skipped and why.
- Never weaken or remove a valid test to make a change pass.
- Never carry a prior health conclusion forward under a new date.
- "Not assessed" is a correct answer. Invented assessment is a serious defect.
- Material claims in the architecture authority carry inline evidence references.

## Waiver Rules

- A requirement you cannot meet is waived on the record, never skipped silently.
- Record: requirement not completed, reason, risk, recommended follow-up.
- Grounds are environmental only: missing tooling, unsafe execution, permissions,
  unavailable dependency. Never time pressure or inconvenience.
- A transient waiver you have recorded before is a standing waiver. Promote it to
  the validation authority's limitations section or an Accepted debt entry.

## Documentation Rules

- Never edit documentation solely to produce a diff.
- Never invent capabilities, architecture, requirements, dependencies,
  integrations, tests, or status.
- The assessment authority is current truth, updated on the main branch only,
  and is never a chronological diary.
- Resolved debt, fixed issues, and implemented upgrades are archived, not left in
  place and not deleted.
- Accepted ADRs are immutable except for status and cross-references.
- If information already lives in another authority, link to it.

## Security Rules

- Never commit secrets, credentials, tokens, or private certificates.
- Configuration examples use placeholders only.
- Never document real hostnames, tenant identifiers, or account names.
- Never place commercial terms, pricing, or contract language in this repository.
- Do not weaken a security control to simplify an implementation.

## Completion Rule

A task is not complete until code, executed validation, waivers, traceability, and
documentation agree with the resulting repository state.
````

---

# Part IV — Execution

## Agent Completion Report

Verdicts without commands are unverifiable and will be produced regardless of what actually happened.

```text
Classification
- Class 3 (Functional) — bug fix
- Governing requirement: REQ-014

Implementation
- Fixed indefinite retry in token refresh (src/Auth/TokenClient.ps1).

Validation
- PASS    Invoke-Pester ./tests -CI
          exit 0 | passed 47 | failed 0 | skipped 0
- PASS    Invoke-ScriptAnalyzer -Path ./src
          exit 0 | 3 warnings (pre-existing, TD-004)
- WAIVED  Integration suite
          Requirement: Class 3 requires integration validation
          Reason:      Tenant credentials not present in this environment
          Risk:        Integration regressions not caught by this change
          Follow-up:   Run before merge to main
- SKIPPED UI validation — not applicable, no UI in this repository

Scope
- REQ-014: no divergence from agreed requirement.
- No amendment required.
- No unmapped implementation introduced.

Documentation (by responsibility → authority)
- Change history      → changelog.d/2026-08-27-fix-token-refresh.md : Added
- Traceability        → TRACEABILITY.md      : Updated, REQ-014 → Validated
- Defect tracking     → ISSUES.md            : BUG-011 marked Fixed
- Technical debt      → TECH-DEBT.md         : TD-004 severity raised to Medium
- Project overview    → README.md            : Reviewed, no update required
- Architecture        → docs/system-design.md: Reviewed, no update required
- Agreed scope        → REQUIREMENTS.md      : Not edited (contractual)
- Current assessment  → ASSESSMENT.md        : Not updated (feature branch)

Architecture Decisions
- None required (Class 3, no architectural decision made).

Technical Debt
- No new debt introduced.
```

Four distinct outcomes, never conflated:

- **PASS / FAIL** — executed, with result
- **BLOCKED** — attempted, could not complete, with reason
- **WAIVED** — required but not run, with reason, risk, and follow-up
- **SKIPPED** — not applicable to this repository or change

Never `N/A` for something simply not attempted.

---

## Project Lifecycle Modes

### Greenfield Mode

Implementation has not meaningfully begun.

Create the tier-appropriate authorities before development starts, including empty contractual documents at Tier 2C:

```markdown
# Requirements

**Status:** Not yet gathered
**Revision:** 0

> Requirements have not been gathered. This document must be completed and
> baselined with the client before implementation begins. Implementation against
> an empty requirements document is out of process.
```

Distinguish state explicitly: `Proposed | Approved | In Progress | Implemented`. Never describe intended functionality as existing functionality.

Technical debt, defect tracking, and traceability legitimately contain no entries at creation. Do not invent entries to populate them.

**Greenfield sequence for a client project:**

```text
Create repository
      ▼
Apply standard, declare tier, write Authority Mapping, scaffold all authorities
      ▼
Gather requirements with client       → agreed scope
      ▼
Agree detailed solution design        → agreed design
      ▼
Baseline requirements, freeze descriptor
      ▼
Seed architecture authority from descriptor
      ▼
Record initial ADRs
      ▼
Define validation and acceptance strategy
      ▼
Establish agent rules
      ▼
Begin implementation
      ▼
Maintain traceability continuously
```

### Adoption Mode

Applying the standard to an existing repository. The responsibility model makes this straightforward: the work is mapping, not creating.

```text
Inspect repository
      ▼
Determine appropriate tier
      ▼
Inventory existing documentation
      ▼
Map each existing document to a responsibility
      ▼
Write the Authority Mapping and .docs-authority.json
      ▼
Create authorities only for unmapped responsibilities
      ▼
Repair stale living content from repository evidence
      ▼
Run docs-check; record the compliance table
      ▼
Consistency review
```

Rules:

1. A missing canonical filename does not mean the responsibility is unmet. Search and map first.
2. Adapt an authoritative existing document rather than creating a competing one. Renaming is optional; mapping is mandatory.
3. Preserve changelog history verbatim.
4. Merge agent instructions rather than replacing them.
5. Normalize progressively. Do not destroy established conventions to match a template.
6. Do not invent missing architecture, requirements, validation procedures, or implementation detail.
7. Start at the lowest defensible tier. Promotion is cheap; abandoned ceremony is expensive.
8. **Never reconstruct requirements from code.** If the original agreement exists elsewhere, import it as-is. If it does not exist, say so. Inferred requirements are worse than none, because they carry contractual weight they never earned.
9. Traceability built retroactively is legitimate, but must be marked `Reconstructed: Yes` with the date.

### Maintenance Mode

Every Class 1+ change triggers a routed documentation impact review. Living authorities are modified only when the resulting state makes their content stale. Contractual authorities are touched only through amendment.

Quarterly review, five items and nothing else:

1. Run `docs-check`; act on `MISSING` and `REVIEW` rows.
2. Reconcile traceability against the repository; investigate unmapped implementation.
3. Review standing waivers; close any whose blocking condition has resolved.
4. Archive resolved debt, fixed issues, and implemented upgrades.
5. Delete any living documentation not read or needed since the last review.

Item five is the one people skip, and it is the reason documentation standards die. Contractual and derived documents are exempt; they are never deleted.

---

## Canonical Bootstrap Instruction

The single bootstrap for all modes and tiers.

```text
Apply the Software Project Living Documentation Standard 2.2 to this repository.

Step 1 — Determine the project tier.
  Tier 0:  single script or a few files, one maintainer, no integrations, no deployment.
  Tier 1:  multiple modules, reused by others, limited integrations.
  Tier 2:  deployed, integrated, multiple contributors, operational consequences.
  Tier 2C: Tier 2 plus a client or stakeholder with agreed scope and sign-off.
Start at the lowest defensible tier and state your rationale.

Step 2 — Determine the lifecycle mode.
  Greenfield:  implementation has not meaningfully begun.
  Adoption:    partially or substantially implemented, does not yet use this standard.
  Maintenance: already follows this standard.

Step 3 — Inspect the repository well enough to understand its purpose, technologies,
existing documentation, architecture, build process, tests, integrations,
configuration, agreed scope if any, and current state.

Step 4 — Map responsibilities to authorities BEFORE creating anything.

This standard requires documentation RESPONSIBILITIES, not filenames. For each
responsibility your tier requires, identify whether an existing document already
serves it. If one does, map it and keep it. Create a new document only for
responsibilities nothing currently covers. Exactly one authority per
responsibility. Write the Authority Mapping into PROJECT-STANDARD.md and
.docs-authority.json.

Step 5 — Create or adapt only the authorities the tier requires.

Understand the document classes and treat them differently:
  Living       — current truth. Rewrite when reality diverges.
  Contractual  — agreed scope, agreed design, amendments. Frozen. Never rewritten
                 to match what was built. Divergence is reported, not corrected.
  Derived      — decision history and archive. Append-only.
  Governance   — the rules themselves. Versioned.

Apply the Source-of-Truth Hierarchy when sources disagree. For what the system
does, repository state governs. For what it should do, agreed scope governs. A
conflict between the two is a scope finding, not a documentation error, and is
never resolved by editing either side.

In Greenfield Mode, scaffold contractual authorities as explicit placeholders
stating that requirements have not been gathered. Do not leave them out.

In Adoption Mode, map before creating. Preserve changelog history. Never
reconstruct requirements by inferring them from code; if no agreement exists,
say so.

In all modes:
- Derive every claim from repository evidence; cite it inline where material.
- Write "Not assessed" rather than inventing an assessment. This is mandatory.
- Record the assessment basis (commands, date, commit).
- Run every validation command that can safely run here. Report each with its
  exact command, exit code, and counts including tests skipped and why.
- Anything required but not run is WAIVED on the record with reason, risk, and
  follow-up. Never skip silently.
- Include no secrets, real hostnames, tenant identifiers, account names, or
  commercial terms.
- Include only template sections that apply. Delete the rest rather than filling
  them with N/A.
- Link rather than duplicate. Content appearing in two authorities is a defect.

Finish by running docs-check, recording the compliance table in the assessment,
and verifying that the repository, the validation results you actually observed,
the traceability matrix, and the documentation agree.
```

---

## Standard Evolution

When materially changing this standard:

1. Update PROJECT-STANDARD.md and increment the version marker.
2. Update the agent rules authority if agent behavior changes.
3. Review the affected templates.
4. Record the methodology change in the change history authority.
5. Do not force unrelated documentation churn merely because the version changed.

The version marker is mandatory. Adoption Mode cannot reconcile a repository against a standard whose version it cannot identify.

---

## Guiding Principle

The purpose of this structure is not to maximize documentation. It is to minimize rediscovery, and on client work, to make agreed scope and delivered software provably the same thing.

The standard covers authority, evidence, lifecycle, validation, exceptions, compliance, history, and agent execution. What it deliberately does not do is mandate filenames, because a repository that already answers a question well should not be made to answer it twice.

Every living authority must earn its maintenance cost. Every contractual authority must survive untouched long enough to be worth having. When a living document stops being read, delete it. That is a success of the standard, not a failure of it. Contractual documents are never deleted, because the day you need them is the day nobody remembers what was agreed.