"""Apple Safari, macOS only.

Safari keeps bookmarks in ``~/Library/Safari/Bookmarks.plist``. On current
macOS versions that directory is protected, and reading it requires the user to
grant Full Disk Access. That restriction is detected and reported. It is never
worked around, and Safari data is never modified.
"""

from __future__ import annotations

import logging
import plistlib
from pathlib import Path
from typing import Any

from bookmark_exporter.browsers.base import (
    BookmarkDataUnavailableError,
    BrowserProvider,
    CorruptBookmarkDataError,
    PermissionDeniedError,
    ProfileNotFoundError,
    UnsupportedPlatformError,
)
from bookmark_exporter.models import (
    Bookmark,
    BookmarkFolder,
    BrowserProfile,
    assign_source_ids,
)
from bookmark_exporter.utils.paths import is_macos

log = logging.getLogger(__name__)

_MAX_DEPTH = 100

_TITLE_LABELS = {
    "BookmarksBar": "Favorites",
    "BookmarksMenu": "Bookmarks Menu",
    "com.apple.ReadingList": "Reading List",
}

FULL_DISK_ACCESS_MESSAGE = (
    "macOS denied access to Safari's bookmarks. Grant Full Disk Access to this "
    "application in System Settings > Privacy & Security > Full Disk Access, "
    "then restart it."
)


def bookmarks_path() -> Path:
    return Path.home() / "Library" / "Safari" / "Bookmarks.plist"


def _label(node: dict[str, Any]) -> str:
    title = node.get("Title")
    if isinstance(title, str) and title:
        return _TITLE_LABELS.get(title, title)
    return ""


def _parse_node(node: Any, depth: int) -> Bookmark | BookmarkFolder | None:
    if not isinstance(node, dict) or depth > _MAX_DEPTH:
        return None

    node_type = node.get("WebBookmarkType")

    if node_type == "WebBookmarkTypeLeaf":
        url = node.get("URLString")
        if not isinstance(url, str) or not url:
            return None
        uri_dictionary = node.get("URIDictionary")
        title = ""
        if isinstance(uri_dictionary, dict):
            candidate = uri_dictionary.get("title")
            if isinstance(candidate, str):
                title = candidate
        return Bookmark(title=title, url=url)

    if node_type == "WebBookmarkTypeList":
        folder = BookmarkFolder(name=_label(node))
        for child in node.get("Children") or []:
            parsed = _parse_node(child, depth + 1)
            if isinstance(parsed, BookmarkFolder):
                folder.folders.append(parsed)
            elif isinstance(parsed, Bookmark):
                folder.bookmarks.append(parsed)
        return folder

    # WebBookmarkTypeProxy covers History and similar pseudo-entries.
    return None


def parse_bookmarks(data: bytes, root_name: str = "Bookmarks") -> BookmarkFolder:
    """Parse the contents of a Safari ``Bookmarks.plist`` file."""
    try:
        document = plistlib.loads(data)
    except (plistlib.InvalidFileException, ValueError, TypeError) as exc:
        raise CorruptBookmarkDataError("The Safari bookmark file could not be parsed.") from exc

    if not isinstance(document, dict):
        raise CorruptBookmarkDataError("The Safari bookmark file has an unexpected structure.")

    parsed = _parse_node(document, depth=0)
    if not isinstance(parsed, BookmarkFolder):
        raise CorruptBookmarkDataError("The Safari bookmark file contains no bookmark list.")

    parsed.name = root_name
    return assign_source_ids(parsed)


class SafariProvider(BrowserProvider):
    browser_id = "safari"
    browser_name = "Apple Safari"

    def is_supported_platform(self) -> bool:
        return is_macos()

    def detect_profiles(self) -> list[BrowserProfile]:
        if not self.is_supported_platform():
            return []
        path = bookmarks_path()
        try:
            exists = path.is_file()
        except PermissionError:
            raise PermissionDeniedError(FULL_DISK_ACCESS_MESSAGE) from None
        if not exists:
            return []
        return [
            BrowserProfile(
                browser_id=self.browser_id,
                browser_name=self.browser_name,
                profile_id=str(path),
                display_name="Safari",
                data_path=str(path),
            )
        ]

    def load_bookmarks(self, profile: BrowserProfile) -> BookmarkFolder:
        if not self.is_supported_platform():
            raise UnsupportedPlatformError("Safari is only available on macOS.")

        path = Path(profile.data_path)
        try:
            data = path.read_bytes()
        except PermissionError:
            raise PermissionDeniedError(FULL_DISK_ACCESS_MESSAGE) from None
        except FileNotFoundError:
            raise ProfileNotFoundError("Safari's bookmark file no longer exists.") from None
        except OSError as exc:
            raise BookmarkDataUnavailableError(
                "Safari's bookmark file could not be read."
            ) from exc

        return parse_bookmarks(data, root_name=profile.display_name)
