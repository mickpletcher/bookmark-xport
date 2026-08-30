# Repository Assessment

**Last full assessment:** 2026-08-29
**Assessed repository state:** `main` at commit `c35f307`, including the release-readiness changes described here
**Basis:** 94 automated tests with branch coverage; Ruff; strict mypy; live count-only Chrome, Edge, and Firefox integration with source hashes compared; Windows PyInstaller build and bundle smoke test; green Windows, macOS, and Ubuntu CI; green Windows and macOS packaging; green CodeQL; documentation compliance; GitHub configuration inspection
**Assessed by:** Agent

## Executive Summary

The core application works end to end for Chrome, Edge, and Firefox on Windows 11 and reads each source file without changing its SHA-256 hash. The automated suite covers parsing, discovery, export, privacy controls, preferences, and the interactive Qt paths. It passes with 84.83 percent branch coverage. Ruff and strict mypy pass. CI is green on Windows, macOS, and Ubuntu. Windows and macOS PyInstaller bundles build and remain running during offscreen smoke tests.

The release remains blocked by the manual browser import check and live Safari execution. No release tag exists.

## Agent Handoff

Read on every Class 2+ task.

- Browser data access is read-only in all cases. This is a hard rule in [AGENTS.md](AGENTS.md), not a preference. Firefox proves it with a hash comparison in `tests/test_firefox.py`.
- Nothing below `src/bookmark_exporter/ui/` may import Qt. See ADR-003. Breaking this makes the suite unrunnable without a display and kills FU-002.
- `BookmarkFolder.children` is the source-ordered mixed sequence. Do not rebuild separate mutable folder and bookmark lists. See ADR-004.
- The Qt background-task code has a lifetime trap: `MainWindow` must retain every in-flight `_Task` until its signal is delivered. See `src/bookmark_exporter/ui/main_window.py`.
- Safari parsing is synthetic-fixture tested and macOS CI can execute those tests, but no real Safari bookmark file or Full Disk Access denial has been exercised. Do not report live Safari support as verified.
- Test fixtures are synthetic. No real bookmark exports, profile paths, personal URLs, or machine names enter the repository.
- Qt tests require `QT_QPA_PLATFORM=offscreen` when no display is available.
- The build brief in `prompts/` is not agreed scope. There is no contractual authority at this tier.

## Living Documentation Compliance

`pwsh ./scripts/docs-check.ps1 -Markdown -FailOnGap` is the authoritative freshness check. It must pass in the quality job. Targeted semantic checks also reject obsolete Greenfield claims, claims that no executable code exists, stale build-prompt authority, tracked machine-name conflict copies, and Qt imports below the UI.

## Current Health

- Build: PASS, editable install from `pyproject.toml` and locked dependencies
- Tests: PASS, 94 passed, 0 failed, 0 skipped
- Coverage: PASS, 84.83 percent branch coverage against an 80 percent floor
- Integration: PASS on Windows 11 for Chrome, Edge, and Firefox; 907 bookmarks across three profiles; all source hashes unchanged
- Lint: PASS, Ruff check and format check
- Types: PASS, strict mypy over 37 source, test, and build files
- Dependencies: PASS, `pip check`; one runtime dependency and a committed development lock
- Packaging: PASS locally on Windows and in CI on Windows and macOS with PyInstaller build, offscreen smoke, and uploaded artifacts
- CI: PASS at commit `c35f307`; six platform and Python test jobs, quality, two packaging jobs, and CodeQL completed successfully
- Security: Dependabot alerts and security updates, secret scanning, push protection, private vulnerability reporting, and read-only workflow permissions are enabled; CodeQL passed; open CodeQL, Dependabot, and secret-scanning alert counts are zero
- Branch protection: Enabled on `main` with strict required checks, pull requests, linear history, conversation resolution, and force-push and deletion prevention
- Standing waivers: 2

## Standing Waivers

- **Live Safari access is unverified.** No macOS Safari profile with Full Disk Access is available. Risk: real plist or TCC behavior may differ from synthetic tests. Follow-up: run on a real Mac before claiming Safari verification.
- **Browser import compatibility is unverified.** Importing the generated HTML requires a human browser workflow. Risk: structurally valid output may still expose browser-specific import behavior. Follow-up: import one export into Chrome, Edge, and Firefox before release.

## Current Capabilities

Verified locally on Windows 11:

- Discovers and loads Chrome, Edge, and Firefox profiles without modifying source files.
- Loads 293 Chrome, 320 Edge, and 294 Firefox bookmarks in count-only integration validation.
- Preserves nested hierarchy and mixed bookmark and folder ordering.
- Exports one selected folder and descendants through an atomic UTF-8 write.
- Excludes bookmark content and URL credentials from logs and preferences.
- Builds and starts a Windows PyInstaller bundle.

Implemented and CI-verified with synthetic fixtures:

- Safari parsing, unsupported-platform handling, and Full Disk Access guidance.
- Windows, macOS, and Linux unit test matrix.
- Windows and macOS package build and bundle smoke jobs.

## Known Issues and Risks

- Safari remains a live-platform validation gap.
- Browser import compatibility remains a manual release gate.
- Chromium's bookmark JSON and Firefox's SQLite schema are browser-owned formats and may change. Parsers fail visibly or skip malformed records rather than modifying data.
- The complete bookmark tree is held in memory. This is proven at observed sizes around 300 bookmarks per profile, not at very large profiles.

No open defects. See [ISSUES.md](ISSUES.md).

## Technical Debt Summary

No open technical debt. TD-001 and TD-002 were resolved and moved to [docs/archive/RESOLVED-DEBT.md](docs/archive/RESOLVED-DEBT.md).

## Current Priorities

1. Complete the Chrome, Edge, and Firefox manual import check.
2. Execute live Safari validation on a real Mac with and without Full Disk Access.
3. Tag `v0.1.0` only after the release gates above are complete.

## Repository Limitations

- Primary development and live integration validation run on Windows 11 with Python 3.13.
- Python 3.12 and 3.13 are exercised in CI.
- Linux and macOS automated tests do not prove access to real user browser profiles.
- macOS code signing, Windows signing, installers, and automatic updates remain explicitly deferred.
