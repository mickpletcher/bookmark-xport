# ADR-003 — Keep Qt out of everything below the UI layer

**Status:** Accepted
**Date:** 2026-08-28

## Context

The obvious way to build a small Qt application is to let widgets call browser code directly and hold browser-shaped data. That makes the parsing and export logic untestable without a display server, and it makes a future command-line mode (FU-002) a rewrite rather than an addition.

## Decision

No module outside `src/bookmark_exporter/ui/` imports Qt, with the single exception of `app.py`, which imports `QApplication` lazily inside `run()`. Providers, services, exporters, models, and utilities are plain Python. The UI converts the normalized model into `QStandardItemModel` items on the GUI thread.

## Rationale

- Parsing and export tests run with no Qt installed and no display. Only `tests/test_ui.py` requires PySide6, and it skips when PySide6 is absent.
- A missing PySide6 produces an actionable message instead of an import traceback, because the import happens after logging is configured.
- The export service can be called by anything, which is what makes FU-002 small.

## Alternatives Considered

- Qt models all the way down. Rejected: it couples data access to a GUI toolkit and makes headless testing impossible.
- A separate core package. Rejected as premature for a repository this size.

## Consequences

- One conversion step from `BookmarkFolder` to `QStandardItemModel`, which must happen on the GUI thread.
- Background work uses `QThreadPool`, so the UI owns the threading and the services stay synchronous and simple.
- Evidence: src/bookmark_exporter/app.py:22-27, src/bookmark_exporter/ui/models.py:1-33, tests/test_ui.py:15

## Related

FU-002 in [FUTURE-UPGRADES.md](../../FUTURE-UPGRADES.md).
