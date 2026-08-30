# Architecture Decisions

Write the ADR before implementing, not after. Class 4 changes presume an ADR.

An `Accepted` ADR is immutable except for its status line and cross-reference fields. A changed decision requires a new ADR that supersedes it. Supersession is reciprocal: update both ADRs and this index together.

| ID | Title | Status | Date | Supersedes | Superseded by |
|---|---|---|---|---|---|
| [ADR-001](ADR-001-firefox-read-only-access.md) | Read Firefox places.sqlite read-only, with a temporary copy as fallback | Accepted | 2026-08-28 | — | — |
| [ADR-002](ADR-002-safari-access-method.md) | Read Safari bookmarks from Bookmarks.plist and report Full Disk Access denial | Accepted | 2026-08-28 | — | — |
| [ADR-003](ADR-003-no-qt-below-the-ui.md) | Keep Qt out of everything below the UI layer | Accepted | 2026-08-28 | — | — |
| [ADR-004](ADR-004-preserve-mixed-bookmark-order.md) | Preserve mixed bookmark and folder order in the normalized model | Accepted | 2026-08-29 | — | — |

## Template

```markdown
# ADR-001 — Decision Title

**Status:** Proposed | Accepted | Superseded | Rejected
**Date:** YYYY-MM-DD
**Supersedes:** ADR-###
**Superseded by:** ADR-###

## Context
## Decision
## Rationale
## Alternatives Considered
## Consequences
## Related
```
