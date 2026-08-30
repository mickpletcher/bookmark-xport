# Resolved Technical Debt

Append-only. Entries carry a resolution date and the change that resolved them. Moved here from [TECH-DEBT.md](../../TECH-DEBT.md) when resolved.

### TD-001 — UI behavior was covered only by a construction smoke test

**Status:** Resolved
**Severity:** Low
**Resolved:** 2026-08-29
**Area:** UI testing

Added pytest-qt coverage for initial discovery, browser switching, profile switching, provider failures, task cleanup, folder selection, export enablement, and the export dialog flow.

---

### TD-002 — No linter or static analysis configured

**Status:** Resolved
**Severity:** Low
**Resolved:** 2026-08-29
**Area:** Repository tooling

Added Ruff, strict mypy, branch coverage with an 80 percent floor, and CodeQL. Local and CI commands are defined in `pyproject.toml` and `.github/workflows/`.
