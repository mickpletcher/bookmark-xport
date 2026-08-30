# Resolved Issues

Append-only. Entries carry a resolution date and the change that resolved them. Moved here from [ISSUES.md](../../ISSUES.md) when fixed and verified.

### BUG-001 — Export success logging disclosed the selected bookmark folder name

**Status:** Fixed
**Severity:** Medium
**Resolved:** 2026-08-29
**Area:** Export logging

Successful exports now log counts only. Regression coverage confirms that folder names, bookmark titles, and URLs do not enter the log.

---

### BUG-002 — URL redaction preserved embedded credentials

**Status:** Fixed
**Severity:** High
**Resolved:** 2026-08-29
**Area:** Logging privacy

URL redaction now reconstructs the authority from hostname and optional port. Username, password, path, query, and fragment are excluded. IPv6 and invalid-port cases are covered.

---

### BUG-003 — Initial browser selection could fail to load profiles

**Status:** Fixed
**Severity:** Medium
**Resolved:** 2026-08-29
**Area:** Qt browser discovery

Discovery now sets the first usable browser while signals are blocked and then invokes the browser-change handler once. A Qt interaction test proves the first usable browser loads automatically.
