# ADR-004 — Preserve mixed bookmark and folder order in the normalized model

**Status:** Accepted
**Date:** 2026-08-29

## Context

Browser bookmark stores represent bookmarks and subfolders as one ordered child sequence. The initial normalized model split them into separate `folders` and `bookmarks` lists. That preserved hierarchy but forced every export to place all folders before all bookmarks, changing the user's source order.

## Decision

`BookmarkFolder` stores one heterogeneous `children` list containing `Bookmark` and `BookmarkFolder` values in source order. Providers append parsed nodes to that list as they encounter them. The HTML exporter renders the list in order. Filtered `folders` and `bookmarks` properties remain the browser-independent views used for folder navigation and counts.

## Rationale

Order is part of bookmark data fidelity. Preserving it in the normalized model prevents every downstream consumer from reconstructing information that was previously discarded. The UI still needs only folders, while exporters and future non-GUI consumers can use the complete ordered sequence.

## Alternatives Considered

- Keep two lists and attach position metadata. Rejected because every consumer would have to merge and sort them.
- Preserve mixed order only in the exporter. Rejected because the model had already discarded the information.
- Continue grouping folders first. Rejected because a single-folder exporter should not silently reorder its output.

## Consequences

- Provider parsers and model constructors use `children` rather than separate mutable lists.
- `folders` and `bookmarks` are computed filtered views.
- Existing folder-only UI behavior remains unchanged.
- Mixed-order behavior is covered by Chromium, Firefox, and HTML exporter tests.

## Related

Architecture data model and HTML export sections in [ARCHITECTURE.md](../../ARCHITECTURE.md).
