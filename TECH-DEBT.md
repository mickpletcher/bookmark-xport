# Technical Debt

> Technical debt: the implementation currently works, but some aspect of it should
> eventually be improved because the current approach creates future cost,
> complexity, fragility, or risk.

2 open entries. Resolved debt moves to [docs/archive/RESOLVED-DEBT.md](docs/archive/RESOLVED-DEBT.md) with its resolution date and the change that resolved it.

### TD-001 — UI behavior is covered only by a construction smoke test

**Status:** Open
**Severity:** Low
**Area:** ui/main_window.py
**Introduced/Discovered:** 2026-08-28
**Standing waiver:** No

**Related files**
src/bookmark_exporter/ui/main_window.py, tests/test_ui.py

**Description**
Tests cover the Qt tree model and that `MainWindow` constructs. The interactive paths, browser switching, profile switching, selection, and the export dialog flow, are not exercised.

**Why it exists**
The Chrome-to-export path was proven end-to-end through the service layer instead, which was cheaper than driving widgets and covers the logic that can actually be wrong.

**Impact**
A regression in signal wiring or in the busy-state handling would not be caught by the suite. The threading fix in this release was found by observing stderr during a test run, not by a test.

**Recommended resolution**
Add `pytest-qt` and cover browser selection, profile switching, and the enable and disable transitions of the export button.

**Fix trigger**
The first defect found in UI wiring, or any change to the threading model.

**Estimated effort:** Small

---

### TD-002 — No linter or static analysis configured

**Status:** Open
**Severity:** Low
**Area:** Repository tooling
**Introduced/Discovered:** 2026-08-28
**Standing waiver:** Yes

**Related files**
pyproject.toml, .github/workflows/tests.yml

**Description**
There is no ruff, flake8, or mypy configuration, so the lint line in the assessment reads `Not assessed`.

**Why it exists**
The initial release prioritized working software and a real test suite over tooling.

**Impact**
Type annotation errors and unused imports are caught only by review. The code is fully annotated, so a type checker would likely pay for itself.

**Recommended resolution**
Add ruff and mypy to the dev extra and a lint job to the workflow.

**Fix trigger**
Before the first release tag, or when a second contributor joins.

**Estimated effort:** Small

---

## Classification

1. Does it not work as intended? → Defect, see [ISSUES.md](ISSUES.md)
2. Does the work reduce cost, risk, or fragility in something already shipped? → Debt, here
3. Does the work add capability that does not exist yet? → Upgrade, see [FUTURE-UPGRADES.md](FUTURE-UPGRADES.md)
4. Both 2 and 3? → File as debt, cross-reference the FU

## Entry Template

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
