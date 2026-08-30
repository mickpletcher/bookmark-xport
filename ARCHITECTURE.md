# Architecture

**Last reviewed:** 2026-08-29

Material claims carry inline evidence. Anything not evidenced is marked as such.

## System Overview

A single-process PySide6 desktop application. It reads bookmark data from local browser files, normalizes it into a browser-independent model, shows the folder hierarchy, and writes one selected folder to a Netscape-format HTML file.

Layering is one-directional. The UI depends on services and models. Services depend on providers, models, and exporters. Providers depend only on models and utilities. Nothing below the UI imports Qt.

```text
ui/main_window.py, ui/models.py
        |
services/browser_discovery.py, services/export_service.py
        |
browsers/ (chrome, edge, firefox, safari)  ->  exporters/html_exporter.py
        |
models/bookmarks.py
```

Evidence: no Qt import exists outside `src/bookmark_exporter/ui/` and `src/bookmark_exporter/app.py:22`.

## Major Components

**Normalized model.** `Bookmark`, `BookmarkFolder`, `BrowserProfile`, and `assign_source_ids`. Each folder stores one ordered `children` sequence so interleaved bookmarks and subfolders retain their source order. Filtered folder and bookmark views and recursive counts are computed from that sequence.
Evidence: src/bookmark_exporter/models/bookmarks.py:14-88

**Provider interface.** `BrowserProvider` declares `is_supported_platform`, `detect_profiles`, and `load_bookmarks`. Every recoverable failure is one of seven `BrowserError` subclasses carrying a user-facing message.
Evidence: src/bookmark_exporter/browsers/base.py:1-39

**Chromium parser.** Shared by Chrome and Edge. Chrome and Edge each supply only their user-data directories.
Evidence: src/bookmark_exporter/browsers/chromium.py:97-162, src/bookmark_exporter/browsers/chrome.py:1-19, src/bookmark_exporter/browsers/edge.py:1-16

**Firefox provider.** Reads `places.sqlite` and reconstructs the hierarchy from `moz_bookmarks` ordered by parent then position.
Evidence: src/bookmark_exporter/browsers/firefox.py:63-71, 104-171

**Safari provider.** Parses `Bookmarks.plist` with `plistlib`. macOS only.
Evidence: src/bookmark_exporter/browsers/safari.py:60-115

**Discovery service.** Classifies every provider as available, no data, unsupported OS, permission denied, or error, and never lets one provider's failure affect another.
Evidence: src/bookmark_exporter/services/browser_discovery.py:60-97

**HTML exporter.** Pure function from `BookmarkFolder` to a string. No file I/O.
Evidence: src/bookmark_exporter/exporters/html_exporter.py:1-59

**Export service.** Adds the `.html` suffix and writes UTF-8 with LF newlines to a same-directory temporary file before atomically replacing the destination. A failed replacement leaves an existing destination unchanged. Contains no Qt import.
Evidence: src/bookmark_exporter/services/export_service.py:37-88

## Application Entry Points

`python -m bookmark_exporter` and the `bookmark-xport` GUI script both call `app.run`, which configures logging before importing Qt so a missing PySide6 produces an actionable message rather than a traceback.
Evidence: src/bookmark_exporter/__main__.py:1-8, src/bookmark_exporter/app.py:13-27, pyproject.toml gui-scripts entry

## Data Flow

1. `MainWindow` runs `discover()` on a `QThreadPool` worker.
2. Selecting a browser populates the profile list from the already-discovered profiles.
3. Selecting a profile runs `provider.load_bookmarks(profile)` on a worker and returns a `BookmarkFolder`.
4. The Qt model is built on the GUI thread, because `QStandardItemModel` is not thread-safe.
5. Selecting a folder in the tree stores it and enables export.
6. Export renders HTML and writes it to the path chosen in a native save dialog.

Evidence: src/bookmark_exporter/ui/main_window.py:118-140, 176-201, 227-247

## Data Storage

The application reads browser data and writes a rotating log file, a preferences file holding the last export directory, and an explicit HTML export. The export uses a short-lived same-directory temporary file for atomic replacement. Logs and preferences do not contain bookmark titles, folder names, URL paths, URL credentials, or browser content.
Evidence: src/bookmark_exporter/services/export_service.py:51-82, src/bookmark_exporter/utils/logging_setup.py:28-48, src/bookmark_exporter/utils/preferences.py:17-55

Browser data locations read, all read-only:

| Browser | Windows | macOS | Linux |
|---|---|---|---|
| Chrome | `%LOCALAPPDATA%\Google\Chrome\User Data\<profile>\Bookmarks` | `~/Library/Application Support/Google/Chrome` | `~/.config/google-chrome` |
| Edge | `%LOCALAPPDATA%\Microsoft\Edge\User Data\<profile>\Bookmarks` | `~/Library/Application Support/Microsoft Edge` | `~/.config/microsoft-edge` |
| Firefox | `%APPDATA%\Mozilla\Firefox\profiles.ini` | `~/Library/Application Support/Firefox` | `~/.mozilla/firefox` |
| Safari | not applicable | `~/Library/Safari/Bookmarks.plist` | not applicable |

Evidence: src/bookmark_exporter/browsers/chrome.py:13-25, src/bookmark_exporter/browsers/edge.py:13-23, src/bookmark_exporter/browsers/firefox.py:173-182, src/bookmark_exporter/browsers/safari.py:49-51

No path contains a hard-coded username or home directory; all are derived from environment variables or `Path.home()`.
Evidence: src/bookmark_exporter/utils/paths.py:19-30

## Concurrency

Browser reads run on `QThreadPool` through a `_Task` runnable that reports results by signal. Two things this design has to get right, both handled explicitly:

- Python signal objects are not owned by Qt, so `MainWindow` holds a reference to each in-flight task until it reports back.
- A window closed mid-load would otherwise emit into a deleted receiver, so emission is guarded and `closeEvent` drains the pool.

Evidence: src/bookmark_exporter/ui/main_window.py:44-74, 231-238, 251-253

## Significant Dependencies

PySide6 (>= 6.6) is the only runtime dependency. Development tooling includes pytest, pytest-qt, coverage, Ruff, mypy, pip-tools, and PyInstaller. `requirements-dev.lock` pins the resolved development and packaging toolchain used by CI.
Evidence: pyproject.toml, requirements-dev.lock

## Security Architecture

Browser data is treated as untrusted input.

- **Read-only access is structural.** No browser file is ever opened for writing. Firefox uses a `mode=ro` SQLite URI and falls back to a temporary copy when the database is locked; the original is never touched.
  Evidence: src/bookmark_exporter/browsers/firefox.py:82-103
- **Recursion is bounded.** Chromium and Safari parsing stop at depth 100, so a malformed or hostile file cannot exhaust the stack.
  Evidence: src/bookmark_exporter/browsers/chromium.py:36, src/bookmark_exporter/browsers/safari.py:33
- **Malformed records are skipped, not fatal.** Wrong types, missing keys, and unknown node types are dropped individually.
  Evidence: src/bookmark_exporter/browsers/chromium.py:56-88
- **Output is escaped.** Folder names, titles, and URLs pass through `html.escape(quote=True)`, so bookmark content cannot break out of an attribute or inject markup.
  Evidence: src/bookmark_exporter/exporters/html_exporter.py:29-30
- **Filenames cannot traverse.** Separators, control characters, Windows reserved names, and leading dots are stripped from the suggested filename.
  Evidence: src/bookmark_exporter/utils/paths.py:12-18, 40-58
- **URLs are never fetched or executed.** The application performs no network I/O of any kind.
- **Logs exclude bookmark content and URL credentials.** Successful exports log counts only. `redact_url` reconstructs an authority from hostname and optional port, excluding user information, path, query, and fragment.
  Evidence: src/bookmark_exporter/services/export_service.py:78-82, src/bookmark_exporter/utils/logging_setup.py:28-48
- **Exports are atomic.** Content is flushed to a same-directory temporary file and committed with `os.replace`, so an interrupted write does not truncate an existing destination.
  Evidence: src/bookmark_exporter/services/export_service.py:51-76
- **OS controls are not bypassed.** A macOS Full Disk Access denial is reported with instructions.
  Evidence: src/bookmark_exporter/browsers/safari.py:42-46

## Error Handling

Providers raise `BrowserError` subclasses with user-facing text. The discovery service converts them into a status per browser. The UI worker catches `BrowserError` for the message and everything else for a generic message plus a logged traceback.
Evidence: src/bookmark_exporter/ui/main_window.py:52-66, src/bookmark_exporter/services/browser_discovery.py:70-92

## Logging and Observability

Rotating file log per user, warnings and above also to the console. Failure to create the log directory downgrades to console logging rather than preventing startup.
Evidence: src/bookmark_exporter/utils/logging_setup.py:48-72

## Deployment Architecture

Runs from source, or as a PyInstaller windowed bundle produced by `scripts/build.py`. The wrapper invokes PyInstaller through the active Python interpreter. `scripts/smoke_bundle.py` starts the packaged executable offscreen and fails if it exits early. CI builds and smoke tests Windows and macOS bundles.
Evidence: scripts/build.py:1-50, scripts/smoke_bundle.py:1-49, .github/workflows/tests.yml

## Architectural Constraints

- No Qt import below the UI layer, which is what keeps a future CLI (FU-002) cheap.
- Browser-specific branching lives inside a provider. Nothing else may test which browser is in use.
- Providers are read-only. This is a correctness constraint, not a convention.

## Architectural Decisions

See [docs/decisions/README.md](docs/decisions/README.md). ADR-001 through ADR-003 are recorded.

## Known Architectural Limitations

- Safari code paths have never been executed. See [VALIDATION.md](VALIDATION.md).
- The whole bookmark tree is loaded into memory and rebuilt into a `QStandardItemModel`. Fine at observed sizes (about 300 bookmarks); not assessed at very large ones.

## Planned Evolution

See [FUTURE-UPGRADES.md](FUTURE-UPGRADES.md). FU-001, FU-002.
