# bookmark-xport

Cross-browser desktop tool for exporting a single bookmark folder from Chrome, Edge, Firefox, or Safari to a portable HTML file.

## Overview

Every major browser can export all bookmarks. None of them make it convenient to export one folder. That is the gap this tool fills: pick a browser, pick a profile, pick one folder, and get a standards-compatible HTML bookmark file you can share or import elsewhere.

## Current Status

- Status: Active
- Version: 0.1.0
- Project tier: 1
- Primary technologies: Python 3.12+, PySide6 / Qt
- Owner: Mick

For current repository health, see [ASSESSMENT.md](ASSESSMENT.md).

## Browser and Platform Support

| Browser | Windows | macOS | Linux | Verified |
|---|---|---|---|---|
| Google Chrome | Yes | Yes | Yes | Windows 11 |
| Microsoft Edge | Yes | Yes | Yes | Windows 11 |
| Mozilla Firefox | Yes | Yes | Yes | Windows 11 |
| Apple Safari | — | Yes | — | Not verified |

Safari support is implemented and unit tested against a synthetic fixture, but it has never been executed on macOS. Treat it as unverified. macOS and Linux are supported by the code but have not been run.

## Key Capabilities

- Detects installed browsers and distinguishes available data, missing data, an unsupported OS, and permission denial.
- Discovers multiple profiles for Chromium browsers and Firefox.
- Browsable folder tree with recursive bookmark and subfolder counts.
- Exports exactly one selected folder plus all descendants, never siblings or parents.
- Preserves the original mixed ordering of bookmarks and subfolders.
- Netscape-format HTML output that imports into mainstream browsers.
- Suggests a sanitized filename such as `Development-Bookmarks.html`.
- Remembers the last export directory. Nothing else is persisted.

## Architecture Summary

Browser-specific parsing is isolated behind a provider interface, feeding a normalized bookmark model that the UI and the HTML exporter both consume. No browser user interface is automated; local bookmark files are read directly, read-only. Nothing below the UI layer imports Qt. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Repository Structure

```text
.
├── src/bookmark_exporter/
│   ├── app.py             Bootstrap and logging
│   ├── browsers/          One module per browser, plus the shared Chromium parser
│   ├── exporters/         Netscape bookmark HTML writer
│   ├── models/            Normalized Bookmark and BookmarkFolder
│   ├── services/          Browser discovery and export
│   ├── ui/                PySide6 window and Qt model adapters
│   └── utils/             Paths, logging, preferences
├── tests/                 pytest suite and synthetic fixtures
├── scripts/
│   ├── build.py           PyInstaller wrapper
│   └── docs-check.ps1     Documentation compliance and drift check
├── docs/
│   ├── archive/           Resolved debt, issues, upgrades
│   └── decisions/         Architecture decision records
├── changelog.d/           Per-change changelog fragments
├── requirements-dev.lock  Reproducible development and packaging dependencies
└── prompts/               Implementation brief and the documentation standard
```

## Getting Started

```powershell
git clone <repository-url>
cd bookmark-xport
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --requirement requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps --editable .
.\.venv\Scripts\python.exe -m bookmark_exporter
```

On macOS or Linux use `python3 -m venv .venv` and `.venv/bin/python`.

Add `--verbose` for debug-level logging.

## Usage

1. Pick a browser. Browsers with no readable data are listed but disabled.
2. Pick a profile if the browser has more than one.
3. Select one folder in the tree. The summary line shows recursive counts.
4. Click Export Folder and choose where to save.
5. Import the file through any browser's bookmark import.

## Packaging

```powershell
.\.venv\Scripts\python.exe scripts/build.py
```

Produces a windowed PyInstaller bundle in `dist/`. Packaging logic lives entirely in that script; the application does not know it is frozen.

Smoke-test the bundle without opening a visible window:

```powershell
.\.venv\Scripts\python.exe scripts/smoke_bundle.py
```

## Privacy

- All processing is local. The application performs no network I/O of any kind.
- No analytics and no telemetry.
- Bookmark titles, folder names, URL paths, query strings, and URL credentials are never written to the log.
- Bookmark titles and URLs are never stored in preferences.
- Export data is written to a same-directory temporary file and atomically replaced into the destination. The temporary file is removed immediately.

## Read-Only Guarantee

This release is an exporter. It never adds, deletes, renames, or reorganizes browser bookmarks. No browser file is opened for writing. Firefox's `places.sqlite` is opened read-only, and when it is locked a temporary copy is read instead. See [ADR-001](docs/decisions/ADR-001-firefox-read-only-access.md).

## Validation

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest --cov=bookmark_exporter --cov-report=term-missing --cov-fail-under=80
.\.venv\Scripts\python.exe -m ruff check src tests scripts
.\.venv\Scripts\python.exe -m ruff format src tests scripts --check
.\.venv\Scripts\python.exe -m mypy src tests scripts
```

See [VALIDATION.md](VALIDATION.md) for levels, the validation matrix, and known limitations.

Documentation compliance:

```powershell
pwsh ./scripts/docs-check.ps1 -Markdown
```

## Contributing

Read [AGENTS.md](AGENTS.md) and [PROJECT-STANDARD.md](PROJECT-STANDARD.md) first. Three rules are absolute: browser data is read-only, no browser UI is automated, and no real bookmark data enters this repository. Test fixtures are synthetic.

Add a fragment to `changelog.d/` rather than editing CHANGELOG.md on a branch.

Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

## Documentation

See the Authority Mapping in [PROJECT-STANDARD.md](PROJECT-STANDARD.md) for the authoritative source of each documentation responsibility.

## Known Limitations

- Safari is implemented but has never been executed. See [VALIDATION.md](VALIDATION.md).
- Exported HTML has not yet been import-tested in a browser.
- The Windows bundle is locally built and smoke tested. macOS packaging is validated by CI rather than locally.
- Open technical debt is listed in [TECH-DEBT.md](TECH-DEBT.md); known defects in [ISSUES.md](ISSUES.md).

## License

MIT. See [LICENSE](LICENSE).
