# Technical Debt

No open technical debt.

Resolved entries are retained in [docs/archive/RESOLVED-DEBT.md](docs/archive/RESOLVED-DEBT.md).

## Classification

1. Does it not work as intended? Defect, see [ISSUES.md](ISSUES.md).
2. Does the work reduce cost, risk, or fragility in something already shipped? Debt, here.
3. Does the work add capability that does not exist yet? Upgrade, see [FUTURE-UPGRADES.md](FUTURE-UPGRADES.md).
4. Both 2 and 3? File as debt and cross-reference the upgrade.

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
