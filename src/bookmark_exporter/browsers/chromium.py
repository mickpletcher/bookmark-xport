"""Chromium bookmark parsing and profile discovery.

Chrome, Edge, and every other Chromium browser share this code. A browser
subclass supplies only its user-data directory and its identity.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from bookmark_exporter.browsers.base import (
    BookmarkDataUnavailableError,
    BrowserProvider,
    CorruptBookmarkDataError,
    PermissionDeniedError,
    ProfileNotFoundError,
)
from bookmark_exporter.models import (
    Bookmark,
    BookmarkFolder,
    BrowserProfile,
    assign_source_ids,
)

log = logging.getLogger(__name__)

# Chromium timestamps are microseconds since 1601-01-01 UTC.
_WEBKIT_EPOCH = datetime(1601, 1, 1, tzinfo=UTC)

# Guards against a malformed or hostile file causing unbounded recursion.
_MAX_DEPTH = 100

_ROOT_LABELS = {
    "bookmark_bar": "Bookmarks Bar",
    "other": "Other Bookmarks",
    "synced": "Mobile Bookmarks",
}


def _webkit_timestamp(value: Any) -> datetime | None:
    """Convert a Chromium timestamp to a datetime, or None if unusable."""
    try:
        microseconds = int(value)
    except (TypeError, ValueError):
        return None
    if microseconds <= 0:
        return None
    try:
        return _WEBKIT_EPOCH + timedelta(microseconds=microseconds)
    except (OverflowError, OSError):
        return None


def _parse_node(node: Any, depth: int) -> Bookmark | BookmarkFolder | None:
    """Convert one Chromium node. Returns None for anything unrecognizable."""
    if not isinstance(node, dict) or depth > _MAX_DEPTH:
        return None

    node_type = node.get("type")
    name = node.get("name")
    title = name if isinstance(name, str) else ""

    if node_type == "url":
        url = node.get("url")
        if not isinstance(url, str) or not url:
            return None
        return Bookmark(title=title, url=url, added=_webkit_timestamp(node.get("date_added")))

    if node_type == "folder":
        folder = BookmarkFolder(name=title, added=_webkit_timestamp(node.get("date_added")))
        children = node.get("children")
        if isinstance(children, list):
            _fill(folder, children, depth + 1)
        return folder

    return None


def _fill(folder: BookmarkFolder, children: Iterable[Any], depth: int) -> None:
    for child in children:
        parsed = _parse_node(child, depth)
        if isinstance(parsed, (Bookmark, BookmarkFolder)):
            folder.children.append(parsed)


def parse_bookmarks(raw: str, root_name: str = "Bookmarks") -> BookmarkFolder:
    """Parse the contents of a Chromium ``Bookmarks`` file.

    Unknown roots are included; unknown node types and malformed entries are
    skipped rather than raising, so one bad record cannot lose a whole profile.
    """
    try:
        document = json.loads(raw)
    except ValueError as exc:
        raise CorruptBookmarkDataError("The bookmark file is not valid JSON.") from exc

    if not isinstance(document, dict):
        raise CorruptBookmarkDataError("The bookmark file has an unexpected structure.")

    roots = document.get("roots")
    if not isinstance(roots, dict):
        raise CorruptBookmarkDataError("The bookmark file contains no bookmark roots.")

    root = BookmarkFolder(name=root_name)
    for key, node in roots.items():
        if not isinstance(node, dict) or node.get("type") != "folder":
            continue
        parsed = _parse_node(node, depth=1)
        if not isinstance(parsed, BookmarkFolder):
            continue
        if not parsed.name:
            parsed.name = _ROOT_LABELS.get(key, key.replace("_", " ").title())
        root.children.append(parsed)

    return assign_source_ids(root)


class ChromiumProvider(BrowserProvider):
    """Base for any Chromium browser. Subclasses supply paths and identity."""

    def user_data_dirs(self) -> list[Path]:
        """Candidate user-data directories for this browser on this OS."""
        raise NotImplementedError

    def is_supported_platform(self) -> bool:
        return bool(self.user_data_dirs())

    def detect_profiles(self) -> list[BrowserProfile]:
        profiles: list[BrowserProfile] = []
        for user_data in self.user_data_dirs():
            try:
                if not user_data.is_dir():
                    continue
                candidates = sorted(
                    (entry for entry in user_data.iterdir() if entry.is_dir()),
                    key=lambda entry: entry.name,
                )
            except PermissionError:
                raise PermissionDeniedError(
                    f"Access to the {self.browser_name} profile directory was denied."
                ) from None
            except OSError:
                log.debug("Could not enumerate %s", user_data, exc_info=True)
                continue

            for directory in candidates:
                bookmarks_file = directory / "Bookmarks"
                if not bookmarks_file.is_file():
                    continue
                profiles.append(
                    BrowserProfile(
                        browser_id=self.browser_id,
                        browser_name=self.browser_name,
                        profile_id=str(bookmarks_file),
                        display_name=self._profile_display_name(directory),
                        data_path=str(bookmarks_file),
                    )
                )
        return profiles

    def load_bookmarks(self, profile: BrowserProfile) -> BookmarkFolder:
        path = Path(profile.data_path)
        try:
            raw = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise ProfileNotFoundError(
                f"The {self.browser_name} profile '{profile.display_name}' no longer exists."
            ) from None
        except PermissionError:
            raise PermissionDeniedError(
                f"Access to the {self.browser_name} bookmark file was denied."
            ) from None
        except (OSError, UnicodeDecodeError) as exc:
            raise BookmarkDataUnavailableError(
                f"The {self.browser_name} bookmark file could not be read."
            ) from exc

        return parse_bookmarks(raw, root_name=profile.display_name)

    def _profile_display_name(self, directory: Path) -> str:
        """Human name for a profile directory, from Chromium's own preferences."""
        preferences = directory / "Preferences"
        try:
            document = json.loads(preferences.read_text(encoding="utf-8"))
            name = document.get("profile", {}).get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
        except (OSError, ValueError, AttributeError, UnicodeDecodeError):
            log.debug("No usable profile name in %s", preferences, exc_info=True)
        return directory.name
