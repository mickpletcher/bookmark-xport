"""Normalized bookmark models."""

from bookmark_exporter.models.bookmarks import (
    Bookmark,
    BookmarkFolder,
    BrowserProfile,
    assign_source_ids,
)

__all__ = ["Bookmark", "BookmarkFolder", "BrowserProfile", "assign_source_ids"]
