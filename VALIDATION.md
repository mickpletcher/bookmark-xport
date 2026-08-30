# Validation

**Last reviewed:** 2026-08-28

> The authoritative runbook for proving a change works. Not a log of runs.
> Execution evidence travels with the change in the commit or completion report.

## Validation Levels

### Basic

Unit tests over the normalized model, the Chromium parser, the Firefox parser, and the HTML exporter, using synthetic fixtures. No real browser data.

### Integration

Provider discovery and bookmark loading against real local browser profiles on the developer machine. Cannot be automated in CI because it depends on installed browsers and user profiles.

### Full

Basic plus integration plus an exported HTML file re-imported into at least one browser to confirm the output is genuinely importable.

## Environment Requirements

- Python 3.12 or later.
- Windows 11 for Chrome, Edge, and Firefox integration validation.
- macOS for any Safari validation. Not available on the primary development machine.

## Setup

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

On macOS and Linux use `python3 -m venv .venv` and `.venv/bin/python`.

The Qt smoke tests need a platform plugin. Set `QT_QPA_PLATFORM=offscreen` when no display is available. `tests/test_ui.py` skips entirely when PySide6 is not installed.

## Commands

| Purpose | Command | Expected exit code | Typical runtime |
|---|---|---|---|
| Full test suite | `python -m pytest -q` | 0 | under 5 seconds |
| One suite | `python -m pytest tests/test_firefox.py -q` | 0 | under 2 seconds |
| Documentation compliance | `pwsh ./scripts/docs-check.ps1 -Markdown` | 0 | under 5 seconds |
| Package build | `python scripts/build.py` | 0 | minutes |

Integration check against real local browsers, printing counts only and never bookmark content:

```powershell
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'src'); from bookmark_exporter.services.browser_discovery import discover; [print(b.browser_name, b.status.value, len(b.profiles)) for b in discover()]"
```

A read-only proof for any provider is to hash the source file before and after `load_bookmarks` and confirm the digests match. `tests/test_firefox.py` does exactly this for Firefox.

## Manual Import Check

Required for exporter and packaging changes. Export a folder, then import the resulting file through Chrome, Edge, and Firefox bookmark import and confirm the folder hierarchy appears intact.

## Known Validation Limitations

Mandatory section. Each entry states what cannot be validated, why, and the risk.

- **Safari provider has never been executed.** The primary development machine runs Windows 11 and Safari exists only on macOS. Parsing is covered by tests using a synthetic plist, and the permission and unsupported-OS paths are covered only through monkeypatching. Risk: real `Bookmarks.plist` structures, real TCC denials, and real profile discovery are unverified. Mitigation: Safari logic is isolated behind the provider interface, discovery contains provider failures, and README states Safari support is unverified.
- **Exported HTML import compatibility is manual.** Confirming that a browser actually accepts the exported file requires a human importing it. Risk: the exporter can produce structurally valid but practically unimportable output. Mitigation: the manual import check above is required for exporter changes.
- **No macOS or Linux execution.** CI is configured for windows-latest and macos-latest but has never run. Risk: platform-specific path and packaging defects are undetected until the first CI run.
- **No linter or static analysis is configured.** Risk: style and simple correctness issues are caught only by review. See TD-002.

Each of these is a standing waiver and is counted in [ASSESSMENT.md](ASSESSMENT.md).

## Validation Matrix

| Change type | Class | Unit | Integration | Smoke | Manual import check |
|---|---|---|---|---|---|
| Documentation only | 1 | No | No | No | No |
| Internal refactor | 2 | Yes | As needed | Yes | No |
| Test-only change | 2 | Yes | No | No | No |
| Bug fix | 3 | Yes | As needed | Yes | If exporter affected |
| New feature or browser provider | 3 | Yes | Yes | Yes | If exporter affected |
| Interface change | 3 | Yes | Yes | Yes | No |
| Dependency change | 3 | Yes | Yes | Yes | No |
| Architecture change | 4 | Yes | Yes | Yes | Yes |
| Security or file-access change | 4 | Yes | Yes | Yes | No |
| Packaging or build change | 4 | Yes | Yes | Yes | Yes |

**Hard rule.** Validation is never claimed on the basis of code inspection. If a command was not executed, it is reported as `BLOCKED` or `WAIVED` with a reason.
