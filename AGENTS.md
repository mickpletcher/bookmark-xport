# AI Agent Repository Rules

Standard version: 2.2
Project tier: 1
Lifecycle mode: Greenfield

## Authority Resolution

This file names documentation responsibilities, not filenames. Resolve every responsibility through the Authority Mapping in [PROJECT-STANDARD.md](PROJECT-STANDARD.md) before reading or writing. Never create a document that duplicates an existing authority.

Responsibilities marked `Not required at this tier` are not to be created. Do not add REQUIREMENTS.md, DESCRIPTOR.md, AMENDMENTS.md, TRACEABILITY.md, or OPERATIONS.md to this repository without first promoting the tier in PROJECT-STANDARD.md.

## Document Classes

- **Living** — current truth. Rewrite when reality diverges. All authorities in this repository except the two below.
- **Derived** — `docs/decisions/` and `docs/archive/`. Append-only.
- **Governance** — PROJECT-STANDARD.md and this file. Versioned.

There are no contractual authorities at this tier. [prompts/COPILOT-BUILD-PROMPT.md](prompts/COPILOT-BUILD-PROMPT.md) is an implementation brief, not agreed scope. Do not treat it as frozen and do not report divergence from it as a scope finding.

## Source of Truth

Repository state governs what the system does. Stale documentation is corrected to match it. Documentation never describes intended functionality as existing functionality.

## Startup

1. Read this file.
2. Classify the change (Class 0-4) using PROJECT-STANDARD.md.
3. Class 0: implement and stop. No documentation lifecycle.
4. Class 1+: resolve routed responsibilities through the Authority Mapping.
5. Read only those authorities, plus the Agent Handoff section of ASSESSMENT.md.
6. Inspect the relevant implementation before editing it.

Do not read the full documentation set on every task.

## Evidence Rules

- Never claim a test, lint, build, or scan passed unless the command was executed in this session.
- Report the command, exit code, and counts including tests skipped and why.
- Never weaken or remove a valid test to make a change pass.
- Never carry a prior health conclusion forward under a new date.
- `Not assessed` is a correct answer. Invented assessment is a serious defect.
- Material claims in ARCHITECTURE.md carry inline evidence references to files and line ranges.

## Waiver Rules

- A requirement you cannot meet is waived on the record, never skipped silently.
- Record: requirement not completed, reason, risk, recommended follow-up.
- Grounds are environmental only: missing tooling, unsafe execution, permissions, unavailable dependency.
- A transient waiver recorded before is a standing waiver. Promote it to the Known Validation Limitations section of VALIDATION.md or an `Accepted` entry in TECH-DEBT.md.

## Documentation Rules

- Never edit documentation solely to produce a diff.
- Never invent capabilities, architecture, dependencies, integrations, tests, or status.
- ASSESSMENT.md is current truth, updated on the main branch only, never a chronological diary.
- CHANGELOG.md is not edited on a feature branch. Add a fragment to `changelog.d/`.
- Resolved debt, fixed issues, and implemented upgrades move to `docs/archive/`. Never deleted, never left in place.
- Accepted ADRs are immutable except for status and cross-reference fields. A changed decision requires a new ADR that supersedes it.
- If information already lives in another authority, link to it.

## Project-Specific Rules

These follow from the nature of this tool and are not optional.

- **Never write to browser data.** All browser bookmark and profile access is read-only. Firefox `places.sqlite` is opened read-only or via a temporary copy. Safari data is never modified.
- **Never automate a browser user interface** to obtain bookmarks. Read local data files directly.
- **Never bypass an OS security control.** macOS Full Disk Access restrictions are detected and reported with an actionable message, not worked around.
- **Never commit real bookmark data.** Test fixtures are synthetic. Real profile paths, usernames, URLs from a personal browser, and machine names do not enter this repository.
- **Browser-specific logic stays in its provider.** GUI, models, and export code must not branch on browser type.
- An unavailable, uninstalled, or permission-denied browser must never crash the application.

## Security Rules

- Never commit secrets, credentials, tokens, or private certificates.
- Configuration and documentation examples use placeholder paths only. No real user profile paths.
- Do not weaken a security control to simplify an implementation.

## Completion Rule

A task is not complete until code, executed validation, waivers, and documentation agree with the resulting repository state. Report using the completion report format in [prompts/Scaffolding.md](prompts/Scaffolding.md).
