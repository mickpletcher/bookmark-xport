# GitHub Copilot Build Prompt — Cross-Browser Bookmark Folder Exporter

## Mission
Act as the lead software engineer for this repository. Build a production-quality, cross-platform desktop application that lets a user export a **specific bookmark folder** from a supported browser into a portable HTML bookmark file for sharing and importing elsewhere.

Build working software, not placeholder scaffolding. Start with an end-to-end proof of concept, then harden it with tests, documentation, error handling, and packaging.

## Product Goal
Most browsers can export all bookmarks but do not make it convenient to export one folder. The application must:

1. Detect installed supported browsers.
2. Discover browser profiles where applicable.
3. Read bookmark hierarchies from local browser data.
4. Display folders in a navigable tree.
5. Let the user select exactly one folder.
6. Preview bookmark/subfolder counts.
7. Export that folder recursively to standards-compatible HTML.
8. Save to a user-selected location.
9. Produce a file suitable for sharing and browser import.

## Initial Browser Support
- Google Chrome
- Microsoft Edge
- Mozilla Firefox
- Apple Safari on macOS

Use a provider/adapter architecture so Brave, Chromium, Vivaldi, Opera, Arc, and others can be added later.

## Technology Stack
- Python 3.12+
- PySide6 / Qt
- `json` for Chromium bookmark stores
- `sqlite3` for Firefox where appropriate
- `plistlib` and safe macOS-specific mechanisms for Safari where appropriate
- `pathlib`
- Python `logging`
- `pytest`
- PyInstaller

Prefer the standard library and avoid unnecessary dependencies.

## Critical Engineering Rule
Do **not** automate browser user interfaces to obtain bookmarks. Read local bookmark/profile data directly using safe, well-understood formats. Browser-specific behavior must be isolated from the GUI and common model.

## Architecture
```text
GUI / Application Layer
        |
Browser Discovery / Service
        |
        +-- Chrome Provider
        +-- Edge Provider
        +-- Firefox Provider
        +-- Safari Provider
        |
Normalized Bookmark Model
        |
Export Service
        |
Netscape Bookmark HTML
```

Do not tightly couple UI components to browser storage formats.

## Suggested Repository Structure
```text
.
├── README.md
├── CHANGELOG.md
├── ASSESSMENT.md
├── FUTURE-UPGRADES.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── src/
│   └── bookmark_exporter/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── models/
│       │   └── bookmarks.py
│       ├── browsers/
│       │   ├── base.py
│       │   ├── chromium.py
│       │   ├── chrome.py
│       │   ├── edge.py
│       │   ├── firefox.py
│       │   └── safari.py
│       ├── services/
│       │   ├── browser_discovery.py
│       │   └── export_service.py
│       ├── exporters/
│       │   └── html_exporter.py
│       ├── ui/
│       │   ├── main_window.py
│       │   └── models.py
│       └── utils/
│           └── paths.py
├── tests/
│   ├── fixtures/
│   ├── test_chromium.py
│   ├── test_firefox.py
│   ├── test_safari.py
│   └── test_html_exporter.py
├── scripts/
│   └── build.py
└── .github/workflows/tests.yml
```
Adjust when justified, but preserve separation of concerns.

## Normalized Models
Create browser-independent models for at least:

### Bookmark
- title
- URL
- optional creation timestamp
- optional extensible metadata

### BookmarkFolder
- folder name
- child folders
- bookmarks
- optional source identifier/path

Preserve hierarchy, titles, URLs, nesting, and order whenever possible. All UI/export logic must use normalized models rather than browser-specific structures.

## Browser Provider Interface
Define a common abstract interface conceptually similar to:

```python
class BrowserProvider(ABC):
    @abstractmethod
    def detect_profiles(self) -> list[BrowserProfile]: ...

    @abstractmethod
    def load_bookmarks(self, profile: BrowserProfile) -> BookmarkFolder: ...
```

Expose browser name/ID, profile display name/path, and OS support.

## Chrome and Edge
Chromium browsers commonly store bookmarks in a JSON `Bookmarks` file. Support multiple profiles such as `Default`, `Profile 1`, `Profile 2`, etc. Parse bookmark bar, other bookmarks, and other valid roots when present.

Implement reusable Chromium parsing. Chrome and Edge should provide browser-specific path/profile discovery without duplicating the parser. Handle missing/optional JSON keys safely.

## Firefox
Discover Firefox profiles and extract actual bookmarks from `places.sqlite`/related profile data.

Requirements:
- Never modify the database.
- Use read-only access where possible.
- Remain resilient when Firefox is running.
- If locking prevents safe access, use a safe temporary-copy strategy where appropriate.
- Reconstruct hierarchy and ordering correctly.
- Never confuse browsing history with bookmarks.

## Safari
Support Safari on macOS only. Determine the safest reliable method for the current macOS version.

Requirements:
- Never modify Safari data.
- Respect macOS privacy/security controls.
- Gracefully detect permission restrictions such as Full Disk Access requirements.
- Provide actionable permission messages rather than crashing.
- Never bypass OS security controls.
- Keep all Safari-specific logic isolated.

## Browser Detection
At startup distinguish between:
- available browser/profile data
- installed browser with unavailable data
- unsupported browser on current OS
- permission denied

An unavailable browser must not crash the application.

## Desktop UI
Build a clean utility-style interface containing:
- Browser selector
- Profile selector when applicable
- Bookmark folder tree
- Selected-folder summary
- Export button
- Status/error area

Concept:
```text
+----------------------------------------------------------+
| Bookmark Folder Exporter                                 |
+----------------------------------------------------------+
| Browser: [ Chrome v ]   Profile: [ Default v ]           |
+----------------------------------------------------------+
| > Bookmarks Bar                                          |
|     > Development                                        |
|     > Travel                                             |
|     > Research                                           |
| > Other Bookmarks                                        |
+----------------------------------------------------------+
| Selected: Development                                    |
| 42 bookmarks | 6 subfolders                              |
|                                      [ Export Folder ]    |
+----------------------------------------------------------+
```

Use native save dialogs. Keep the UI responsive during loading. Technical paths/database details belong in diagnostics/logs, not normal UX.

## HTML Export
Generate Netscape Bookmark File Format HTML compatible with mainstream browsers, for example:

```html
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3>Development</H3>
    <DL><p>
        <DT><A HREF="https://example.com">Example</A>
    </DL><p>
</DL><p>
```

Properly HTML-escape folder names, titles, URLs, and special characters. Preserve nested folders recursively.

## Export Semantics
Export only the selected folder plus all descendants. Do not include siblings or unrelated parent content. Suggest a sanitized filename such as `Development-Bookmarks.html`, valid on Windows and macOS.

## Read-Only Safety
The initial release is an exporter only. It must never add, delete, rename, reorganize, or otherwise write browser bookmarks/profile data.

## Privacy
Bookmark data may be sensitive:
- Process locally.
- No external transmission.
- No analytics/telemetry by default.
- Do not log full URLs at normal logging levels.
- Do not include bookmark contents in crash reports.
- Document this behavior in README.md.

## Error Handling
Handle and explain:
- browser not installed
- profile not found
- malformed/corrupt bookmark data
- inaccessible files
- locked database
- permission denied
- unsupported Safari environment
- unwritable export destination

Show concise actionable errors to users and technical details in logs.

## Testing
Use sanitized fixtures, not the developer's live profile, for automated tests.

Cover:
- Chromium single/nested/empty folders
- multiple profiles
- malformed JSON
- Unicode
- Firefox hierarchy/order/multiple profiles/read-only behavior
- Safari fixture parsing where practical
- Safari unsupported-OS and permission behavior
- HTML nesting, escaping, Unicode, unusual URLs, empty folders, deterministic output where practical

## Platform Targets
Primary:
- Windows 11
- current supported macOS versions

Keep Linux compatibility possible for Chromium/Firefox where low-cost, but Linux packaging is not required initially. Never hard-code usernames or home directories.

## Packaging
Prepare PyInstaller builds for Windows and macOS while keeping the project runnable directly from source. Keep packaging logic separate from application logic.

## Code Quality
Use type hints, focused functions/classes, clear exceptions, useful docstrings, separation of concerns, and testable design. Avoid duplicated Chromium logic, unexplained magic constants, unnecessary abstractions, and premature complexity.

## Security
Treat browser data as untrusted input. Defend against malformed structures, unexpected types, malicious HTML characters, unsafe filenames/path traversal, and malformed URLs. Never execute bookmark content or automatically navigate to bookmark URLs.

## Accessibility / UX
Where practical, support keyboard navigation, accessible labels, non-mouse workflows, visible progress/status feedback, and remembering the last export directory without storing bookmark contents.

## Living Documentation
Maintain these files throughout development:

### README.md
Include purpose, problem solved, browser/OS support, installation, development setup, running, packaging, usage, privacy, limitations, architecture, screenshots when available, and contribution guidance.

Treat README.md as a living project overview. Review it after every repository change and update it when the change materially affects human-facing understanding, usage, setup, capabilities, architecture summary, status, supported platforms, or limitations.

### CHANGELOG.md
Record meaningful user-facing and engineering changes using a consistent format.

### ASSESSMENT.md
Continuously assess implemented capabilities, architecture quality, test coverage, security posture, defects, technical debt, and release readiness.

### FUTURE-UPGRADES.md
Track valuable ideas that are intentionally outside current scope. Do not implement everything merely because it is identified.

## Future Features — Do Not Delay V1
Track, but do not allow these to derail the initial release:
- import selected folders
- export multiple folders
- search
- duplicate detection
- broken-link checking
- JSON/CSV export
- browser-to-browser comparison/copy
- scheduled backups
- CLI
- portable mode
- more Chromium browsers
- signed installers
- automatic updates

## Implementation Phases

### Phase 1 — Foundation
Create structure, package configuration, normalized models, provider interface, logging, and tests.

### Phase 2 — Chrome End-to-End POC
Deliver the first complete workflow: detect Chrome profiles → load bookmarks → display folder tree → select one folder → export HTML.

### Phase 3 — Edge
Add Edge by reusing generic Chromium parsing.

### Phase 4 — Firefox
Implement safe read-only Firefox extraction.

### Phase 5 — Safari
Implement macOS Safari support and permission handling.

### Phase 6 — UX Hardening
Improve loading states, errors, profile switching, counts, save workflow, preferences, and accessibility.

### Phase 7 — Testing and Packaging
Complete coverage and reproducible Windows/macOS development builds.

## Definition of Done — Initial Release
The release is complete when:
- Chrome, Edge, and Firefox work end-to-end.
- Safari works on supported macOS environments or reports actionable platform/permission limitations.
- Multiple profiles work where applicable.
- Folder trees are browsable.
- Exactly one folder can be selected/exported.
- Nested folders are preserved.
- Exported HTML is validated by importing into Chrome, Edge, and Firefox.
- Browser data is never modified.
- Errors do not crash the app during normal failure scenarios.
- Automated tests pass.
- README, CHANGELOG, ASSESSMENT, and FUTURE-UPGRADES reflect current state.
- The application can be run from source and packaged with PyInstaller.

## Git / Development Workflow
Work in small, reviewable increments. Before considering each phase complete:

1. Inspect the current repository rather than assuming state.
2. Implement the smallest coherent set of changes.
3. Run relevant tests.
4. Run the full test suite when practical.
5. Review the diff for accidental changes or sensitive data.
6. Update living documentation where materially affected.
7. Record meaningful changes in CHANGELOG.md.
8. Update ASSESSMENT.md honestly.
9. Move deferred ideas to FUTURE-UPGRADES.md rather than silently expanding scope.

Never commit real bookmark databases, real browsing data, secrets, personal profile paths, or generated build artifacts that belong in `.gitignore`.

## Copilot Operating Instructions
When this prompt is supplied to GitHub Copilot:

- First inspect the repository and determine what already exists.
- Do not overwrite good existing work merely to match this proposed structure.
- If the repository is empty, begin with Phase 1 and proceed into the Chrome POC.
- If partially implemented, assess gaps and continue from the correct phase.
- Prefer implementing and testing over producing long planning-only responses.
- Do not leave critical behavior as TODOs when it can reasonably be implemented now.
- When blocked by OS-specific behavior, implement the cross-platform interface and tests, document the blocker precisely, and continue with work that is not blocked.
- Keep the application functional at the end of each major phase.
- Never weaken security or privacy controls to make a browser provider work.

## First Execution Request
Begin now by inspecting the repository. Determine its current state against this specification. If it is empty or nearly empty, create the project foundation and implement the **Chrome end-to-end proof of concept** first. Add automated tests and living documentation as part of the implementation. Then report what was implemented, what tests were run and their results, any limitations discovered, and the next recommended phase.
