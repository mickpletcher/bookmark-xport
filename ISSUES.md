# Issues

Defect tracking authority. Identifiers are permanent and never reused.

Two accessibility defects are fixed locally, with limited macOS verification recorded in [ACCESSIBILITY.md](ACCESSIBILITY.md), and remain pending release. Screen-reader speech and keyboard-only export are not yet verified. Shipped fixes are retained in [docs/archive/RESOLVED-ISSUES.md](docs/archive/RESOLVED-ISSUES.md).

Fixed issues move to [docs/archive/RESOLVED-ISSUES.md](docs/archive/RESOLVED-ISSUES.md) once shipped and verified.

## Entry Template

```markdown
### BUG-001 — Short Title

**Status:** Open | Investigating | Fixed | Won't Fix
**Severity:** Low | Medium | High | Critical
**Reported:** YYYY-MM-DD
**Area:** Component

**Symptom**
**Reproduction**
**Expected**
**Workaround**
**Resolution**
```


### BUG-004 — Dynamic label text hidden by generic accessible names

**Status:** Fixed (pending live assistive-technology verification and release)
**Severity:** Medium
**Reported:** 2026-11-06
**Area:** Qt accessibility

**Symptom:** The selection summary and status expose generic names instead of their current text through Qt's accessibility interface.
**Reproduction:** Query `QAccessible.Text.Name` for either label after a selection or status update.
**Expected:** The current label text is available to assistive technology.
**Resolution:** Removed explicit accessible-name overrides. Regression tests check the initial and changing text. Native macOS accessibility-tree checks also exposed the actual summary and export-complete text. This verifies interface content, not spoken announcements.

### BUG-005 — Selection summary clipped with large text

**Status:** Fixed (pending live platform verification and release)
**Severity:** Medium
**Reported:** 2026-11-06
**Area:** Qt layout

**Symptom:** At 24-point text in a 720-by-560 window, the single-line summary extends beyond its available width.
**Reproduction:** Use 24-point text and select a folder with a long name.
**Expected:** The complete summary remains visible.
**Resolution:** Enabled word wrapping. A regression test measures the wrapped text bounds against its available area at 24 points.
