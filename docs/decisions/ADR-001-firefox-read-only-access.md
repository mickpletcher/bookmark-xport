# ADR-001 — Read Firefox places.sqlite read-only, with a temporary copy as fallback

**Status:** Accepted
**Date:** 2026-08-28

## Context

Firefox stores bookmarks in `places.sqlite`. The file is held open by Firefox while it runs, and Firefox uses WAL journaling. Three properties are non-negotiable: the original must never be modified, a running Firefox must not block the export, and the hierarchy and ordering must be read correctly.

Three options were available:

1. `mode=ro` URI connection.
2. `immutable=1` URI connection.
3. Copy the database to a temporary location and read the copy.

## Decision

Try `mode=ro` first, verified by a probe query against `moz_bookmarks`. If that raises any `sqlite3.Error`, copy `places.sqlite` along with its `-wal` and `-shm` sidecars to a temporary directory and read the copy. Delete the temporary directory afterwards.

## Rationale

`mode=ro` is the correct default: it cannot write, it respects the WAL, and it avoids copying a database that can be tens of megabytes.

`immutable=1` was rejected outright. It tells SQLite the file cannot change, which is false while Firefox is running, and it causes the WAL to be ignored. That produces silently stale or inconsistent reads, which is worse than failing.

Copying is the fallback rather than the default because it is only needed when the lock actually blocks us, and copying the sidecars is what keeps the copy consistent.

## Alternatives Considered

- Copy always. Simpler, but wasteful and it doubles peak disk use for no benefit in the common case.
- Ask the user to close Firefox. Rejected as a user-hostile requirement for a read-only operation.

## Consequences

- Two code paths to keep working. The fallback is exercised in practice on Windows when Firefox is running.
- A temporary copy briefly places bookmark data in the system temp directory. It is removed in a `finally` block.
- Evidence: src/bookmark_exporter/browsers/firefox.py:82-103

## Related

Verified read-only behavior: tests/test_firefox.py, `test_load_bookmarks_does_not_modify_the_database`.
