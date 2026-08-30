# ADR-002 — Read Safari bookmarks from Bookmarks.plist and report Full Disk Access denial

**Status:** Accepted
**Date:** 2026-08-28

## Context

Safari stores bookmarks in `~/Library/Safari/Bookmarks.plist`. On current macOS versions `~/Library/Safari` is protected by TCC, so an application that has not been granted Full Disk Access receives a permission error when it reads the file. The repository rules forbid both automating a browser UI and bypassing an OS security control.

## Decision

Read `Bookmarks.plist` directly with `plistlib`. When the read raises `PermissionError`, raise `PermissionDeniedError` carrying instructions to grant Full Disk Access in System Settings. Do not attempt any workaround.

## Rationale

`plistlib` is standard library, the format is stable and documented, and parsing is a pure function that can be tested on any platform with a synthetic fixture. Detecting the denial and telling the user how to fix it is the only legitimate response to a TCC restriction.

## Alternatives Considered

- AppleScript or Safari UI automation. Rejected by the project rules and fragile besides.
- Requesting Full Disk Access programmatically. Not possible; TCC grants are user actions in System Settings.
- Shipping without Safari support. Rejected, since parsing is cheap and the platform limitation can be reported honestly.

## Consequences

- Safari support ships unexecuted. No macOS machine was available. This is recorded as a standing validation limitation, not as working functionality.
- Parsing is covered by tests using a synthetic plist; the file access and permission paths are covered by monkeypatched tests only.
- Evidence: src/bookmark_exporter/browsers/safari.py:42-46, 117-141

## Related

ADR-003. Known Validation Limitations in [VALIDATION.md](../../VALIDATION.md).
