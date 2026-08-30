# Project Standard

**Standard version:** 2.2
**Project tier:** 1
**Tier rationale:** Multiple modules (GUI, browser providers, services, exporters) intended for reuse by other people, with limited integrations. No deployment, no operational consequence on failure, and no client or agreed scope, so Tier 2 and Tier 2C are not defensible.
**Promotion trigger:** Promote to Tier 2 if the tool gains a deployment or update mechanism, runs unattended, or acquires operational consequences on failure. Promote to Tier 2C only if a client or stakeholder with agreed scope and sign-off appears.
**Lifecycle mode:** Greenfield — implementation has not begun.
**Adopted:** 2026-08-28

This repository follows the Software Project Living Documentation Standard 2.2, reproduced at [prompts/Scaffolding.md](prompts/Scaffolding.md).

---

## Authority Mapping

Exactly one authority per responsibility. Resolve every responsibility through this table before reading or writing documentation. The machine-readable form is [.docs-authority.json](.docs-authority.json); the two must agree.

| Responsibility | Authority | Notes |
|---|---|---|
| Project overview | README.md | |
| Current assessment | ASSESSMENT.md | |
| Architecture | ARCHITECTURE.md | Optional at Tier 1; adopted because the provider/adapter design is the core of the tool |
| Change history | CHANGELOG.md | Fragments accumulate in `changelog.d/` |
| Defect tracking | ISSUES.md | Optional at Tier 1; adopted, no external tracker in use |
| Technical debt | TECH-DEBT.md | |
| Deferred improvements | FUTURE-UPGRADES.md | |
| Validation | VALIDATION.md | |
| Operations | Not required at this tier | Desktop application, no deployed runtime |
| Requirement traceability | Not required at this tier | Tier 2C only |
| Agreed scope | Not required at this tier | Tier 2C only; no client or counterparty |
| Agreed design | Not required at this tier | Tier 2C only |
| Scope amendments | Not required at this tier | Tier 2C only |
| Decision history | docs/decisions/ | Optional at Tier 1; adopted |
| Resolved history | docs/archive/ | Optional at Tier 1; adopted |
| Development rules | PROJECT-STANDARD.md | This file |
| Agent rules | AGENTS.md | |

### Note on the build prompt

[prompts/COPILOT-BUILD-PROMPT.md](prompts/COPILOT-BUILD-PROMPT.md) is an implementation brief, not a contractual authority. It has no client, no baseline, and no approval, so it does not satisfy the agreed scope responsibility and is not subject to the contractual rules. It is input to implementation and to the architecture authority. Where the built system diverges from it, the built system governs and the brief is simply superseded.

---

## Change Classes

| Class | Name | Examples |
|---|---|---|
| 0 | Trivial | Formatting, whitespace, typos, local renames, ignore-list additions |
| 1 | Documentation | Human-facing documentation only |
| 2 | Internal implementation | Refactors, internal behavior, test additions, no interface change |
| 3 | Functional | Features, bug fixes, dependency changes, configuration changes, interface changes |
| 4 | Architectural / Security | Architecture, data model, trust boundary, file-system access patterns, packaging, major dependency, security control changes |

Class 0 changes skip the documentation lifecycle entirely. Everything Class 1 and above is meaningful.

## Process Weight by Class

| | Class 0 | Class 1 | Class 2 | Class 3 | Class 4 |
|---|---|---|---|---|---|
| Read routed authorities | No | Target only | Yes | Yes | Yes |
| Read agent handoff | No | No | Yes | Yes | Yes |
| Validation | None | None | Basic | Per matrix | Full per matrix |
| Changelog fragment | No | If meaningful | Yes | Yes | Yes |
| ADR required | No | No | No | If a decision is made | Presumed yes |
| Assessment refresh on merge | No | No | Yes | Yes | Yes |

## Change Type Routing

Read lists name responsibilities and resolve through the Authority Mapping above.

| Change type | Class | Read | Review after |
|---|---|---|---|
| Formatting, typo, ignore-list | 0 | Nothing | Nothing |
| Documentation only | 1 | Target document | Target document |
| Internal refactor | 2 | Architecture, technical debt, validation | Change history, technical debt, assessment |
| Test-only change | 2 | Validation | Change history, validation |
| Bug fix | 3 | Assessment (handoff), validation, defect tracking | Change history, defect tracking, assessment |
| New feature or new browser provider | 3 | Overview, architecture, validation, deferred improvements | Overview, change history, architecture, assessment |
| Interface change | 3 | Overview, architecture, validation | Overview, change history, architecture, validation, assessment |
| Dependency change | 3 | Architecture, technical debt, validation | Change history, architecture, technical debt, assessment |
| Architecture change | 4 | Architecture, decision history, validation | Change history, architecture, decision history, assessment |
| Security or file-access change | 4 | Architecture, validation | Change history, architecture, validation, assessment |
| Packaging or build change | 4 | Architecture, validation | Change history, architecture, validation, assessment |

---

## Source-of-Truth Hierarchy

For "what does the system do?":

```text
Executable repository state → configuration and schemas → tests → architecture and validation docs → assessment → README
```

Repository state governs. Stale documentation is corrected.

At Tier 1 there is no agreed scope authority, so there is no second hierarchy and no scope-finding mechanism. If a client or stakeholder ever appears, promote to Tier 2C before implementing anything they asked for.

---

## Evidence Rule

Every factual claim in living documentation must be derived from repository evidence, explicitly marked unverified, or absent. `Not assessed` is a correct and useful value. Material architecture claims carry inline evidence references. Never carry a prior health conclusion forward under a new date.

## Waivers

A requirement that cannot be met is waived on the record with reason, risk, and follow-up. Grounds are environmental only: missing tooling, unsafe execution, permissions, unavailable dependency. Not time pressure or inconvenience.

Transient waivers live in the completion report. A transient waiver recorded three times is a standing waiver and is promoted to the Known Validation Limitations section of VALIDATION.md or an `Accepted` entry in TECH-DEBT.md, and is counted in ASSESSMENT.md.

## Branching and Merge Policy

- CHANGELOG.md is never edited on a feature branch. Add a fragment to `changelog.d/`.
- ASSESSMENT.md is updated on the main branch only.
- Documentation updates travel in the same commit as the change that made them necessary.

## Compliance

Run `pwsh ./scripts/docs-check.ps1 -Markdown` and paste the output into the Living Documentation Compliance section of ASSESSMENT.md. Compliance is derived, never asserted.

## Standard Evolution

Materially changing this file increments the version marker, updates AGENTS.md if agent behavior changes, and records the methodology change in CHANGELOG.md.
