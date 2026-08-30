# Validation

**Last reviewed:** 2026-08-29

> The authoritative runbook for proving a change works. It is not a run log.
> Execution evidence travels in the completion report and CI run.

## Validation Levels

### Basic

Automated tests with branch coverage plus Ruff and strict mypy. Bookmark fixtures are synthetic. Qt interaction tests run offscreen.

### Integration

Basic validation plus provider discovery and loading against real local browser profiles. Output is count-only. Hash every source file before and after loading and require equality.

### Full

Integration validation plus PyInstaller build and bundle smoke test on affected platforms, then manual import of an exported HTML file into Chrome, Edge, and Firefox when export behavior changes.

## Environment Requirements

- Python 3.12 or 3.13.
- PowerShell 7 for the documentation check.
- Windows 11 for local Chrome, Edge, and Firefox integration validation.
- A real macOS Safari profile for live Safari validation.

## Setup

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --requirement requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps --editable .
```

On macOS and Linux use `python3 -m venv .venv` and `.venv/bin/python`.

Regenerate the lock after an intentional dependency change:

```powershell
.\.venv\Scripts\python.exe -m piptools compile --extra dev --allow-unsafe --output-file requirements-dev.lock --strip-extras pyproject.toml
```

## Commands

| Purpose | Command | Expected exit code |
|---|---|---|
| Tests and coverage | `python -m pytest --cov=bookmark_exporter --cov-report=term-missing --cov-fail-under=80` | 0 |
| Ruff lint | `python -m ruff check src tests scripts` | 0 |
| Ruff format | `python -m ruff format src tests scripts --check` | 0 |
| Strict typing | `python -m mypy src tests scripts` | 0 |
| Dependency consistency | `python -m pip check` | 0 |
| Installed package | `python -c "import bookmark_exporter"` | 0 |
| Documentation | `pwsh ./scripts/docs-check.ps1 -Markdown -FailOnGap` | 0 |
| Package build | `python scripts/build.py` | 0 |
| Bundle smoke | `python scripts/smoke_bundle.py` | 0 |

Set `QT_QPA_PLATFORM=offscreen` before tests and bundle smoke validation where no display is available.

## Local Integration Check

The check may read real local profiles but must print counts only. It must hash each `profile.data_path` before and after `load_bookmarks` and fail if any digest changes. Do not print profile paths, titles, URLs, or machine identifiers.

Expected providers on the primary Windows machine are Chrome, Edge, and Firefox. Safari must report unsupported on Windows.

## Manual Import Check

Required for exporter, normalized-ordering, and packaging changes:

1. Export a synthetic or deliberately non-sensitive folder containing interleaved bookmarks, nested folders, Unicode, and an empty folder.
2. Import the file through Chrome bookmark import and verify hierarchy, order, titles, URLs, and counts.
3. Repeat with Edge and Firefox.
4. Delete the imported test folder after verification.

Browser UI automation is prohibited. This is a human validation step.

## Packaging Check

`scripts/build.py` must run through the active Python interpreter and place output under `dist/`. `scripts/smoke_bundle.py` starts the platform executable with the offscreen Qt platform, waits five seconds, and passes only when the process remains running. CI uploads Windows and macOS bundles as run artifacts.

## Known Validation Limitations

- **Live Safari access is not validated.** Synthetic plist parsing, unsupported-platform behavior, and permission guidance are automated. Real `Bookmarks.plist` structures and TCC behavior still require a real Mac and user-granted Full Disk Access. Risk: Safari may fail despite green macOS fixture tests.
- **Browser import compatibility is manual and incomplete.** No automated test can prove that Chrome, Edge, and Firefox accept the generated file. Risk: a browser-specific import issue can survive structural HTML tests.

These are standing waivers and are counted in [ASSESSMENT.md](ASSESSMENT.md).

## CI Coverage

- Tests and coverage: Windows, macOS, and Ubuntu on Python 3.12 and 3.13.
- Quality: Ruff, strict mypy, and living documentation on Ubuntu and Python 3.13.
- Packaging: Windows and macOS on Python 3.13 with bundle smoke tests and uploaded artifacts.
- Security: CodeQL Python analysis on push, pull request, and weekly schedule.
- Dependency updates: weekly pip and GitHub Actions Dependabot checks.

## Validation Matrix

| Change type | Class | Tests | Quality | Integration | Package | Manual import |
|---|---|---|---|---|---|---|
| Documentation only | 1 | No | Docs only | No | No | No |
| Internal refactor | 2 | Yes | Yes | As needed | No | No |
| Test-only change | 2 | Yes | Yes | No | No | No |
| Bug fix | 3 | Yes | Yes | As needed | If affected | If exporter affected |
| New feature or provider | 3 | Yes | Yes | Yes | Yes | If exporter affected |
| Interface or dependency change | 3 | Yes | Yes | Yes | Yes | No |
| Architecture change | 4 | Yes | Yes | Yes | Yes | Yes |
| Security or file-access change | 4 | Yes | Yes | Yes | Yes | If exporter affected |
| Packaging or build change | 4 | Yes | Yes | Yes | Yes | Yes |

**Hard rule.** Validation is never claimed from inspection. Record the command, exit code, passed, failed, and skipped counts. A required check that cannot run needs a waiver with reason, risk, and follow-up.
