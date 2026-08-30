# Changelog

This repository does not cut releases yet. Sections are date-stamped. Changes accumulate as fragments in `changelog.d/` on feature branches and are concatenated here on merge to main or on a monthly cadence.

## 2026-08 (unreleased)

### Added

- Normalized bookmark model (`Bookmark`, `BookmarkFolder`, `BrowserProfile`) with recursive counts.
- `BrowserProvider` interface and a seven-member `BrowserError` hierarchy carrying user-facing messages.
- Chrome and Edge support through a shared Chromium JSON parser, including multi-profile discovery and profile display names read from Chromium's own preferences.
- Firefox support reading `places.sqlite` read-only, with a temporary-copy fallback when the database is locked. Hierarchy and ordering are reconstructed from `moz_bookmarks`; tag folders, separators, and saved queries are excluded.
- Safari support parsing `Bookmarks.plist`, with Full Disk Access denial detected and reported. Implemented but never executed on macOS.
- Browser discovery service reporting available, no data, unsupported OS, permission denied, or error per browser, with provider failures contained.
- Netscape bookmark HTML exporter with deterministic output and full escaping of folder names, titles, and URLs.
- Export service with filename sanitization, path-traversal protection, writability checks, and UTF-8 output.
- PySide6 window: browser and profile selectors, folder tree, recursive selection summary, native save dialog, status area, accessible names, and keyboard mnemonics. Browser reads run off the GUI thread.
- Rotating per-user file logging with URL redaction, and a preferences file storing only the last export directory.
- pytest suite of 72 tests over synthetic fixtures covering Chromium, Firefox, Safari, the exporter, the export service, discovery, and the Qt model.
- PyInstaller build script and a GitHub Actions workflow for Windows and macOS on Python 3.12 and 3.13.
- Packaging metadata: `pyproject.toml`, `requirements.txt`, MIT `LICENSE`.

### Documentation

- Applied the Software Project Living Documentation Standard 2.2 at Tier 1, Greenfield mode. Created PROJECT-STANDARD.md with the Authority Mapping, AGENTS.md, ASSESSMENT.md, ARCHITECTURE.md, CHANGELOG.md, ISSUES.md, TECH-DEBT.md, FUTURE-UPGRADES.md, VALIDATION.md, `docs/decisions/`, `docs/archive/`, `.docs-authority.json`, and `scripts/docs-check.ps1`.
- Recorded ADR-001 (Firefox read-only access), ADR-002 (Safari access method), and ADR-003 (no Qt below the UI layer).
- Replaced the architecture and validation placeholders with evidence-backed content.
- Expanded README.md into the project overview authority.
- Opened TD-001 (UI covered only by a smoke test) and TD-002 (no linter configured).
