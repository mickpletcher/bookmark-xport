from __future__ import annotations

import plistlib
from pathlib import Path

import pytest

from bookmark_exporter.browsers import safari
from bookmark_exporter.browsers.base import (
    CorruptBookmarkDataError,
    PermissionDeniedError,
    UnsupportedPlatformError,
)
from bookmark_exporter.models import BrowserProfile

_PLIST = {
    "WebBookmarkType": "WebBookmarkTypeList",
    "Title": "",
    "Children": [
        {
            "WebBookmarkType": "WebBookmarkTypeList",
            "Title": "BookmarksBar",
            "Children": [
                {
                    "WebBookmarkType": "WebBookmarkTypeLeaf",
                    "URLString": "https://example.com/alpha",
                    "URIDictionary": {"title": "Alpha & Co"},
                },
                {
                    "WebBookmarkType": "WebBookmarkTypeList",
                    "Title": "Travel",
                    "Children": [
                        {
                            "WebBookmarkType": "WebBookmarkTypeLeaf",
                            "URLString": "https://example.org/caf%C3%A9",
                            "URIDictionary": {"title": "Café ünïcode"},
                        },
                        {"WebBookmarkType": "WebBookmarkTypeLeaf"},
                    ],
                },
            ],
        },
        {"WebBookmarkType": "WebBookmarkTypeProxy", "Title": "History"},
    ],
}


def _profile(path: Path) -> BrowserProfile:
    return BrowserProfile(
        browser_id="safari",
        browser_name="Apple Safari",
        profile_id=str(path),
        display_name="Safari",
        data_path=str(path),
    )


def test_parses_lists_and_leaves() -> None:
    root = safari.parse_bookmarks(plistlib.dumps(_PLIST))

    assert [folder.name for folder in root.folders] == ["Favorites"]
    favorites = root.folders[0]
    assert [bookmark.title for bookmark in favorites.bookmarks] == ["Alpha & Co"]
    assert favorites.folders[0].name == "Travel"
    assert favorites.folders[0].bookmarks[0].title == "Café ünïcode"


def test_skips_proxies_and_leaves_without_a_url() -> None:
    root = safari.parse_bookmarks(plistlib.dumps(_PLIST))
    assert "History" not in [folder.name for folder in root.walk()]
    assert root.bookmark_count == 2


def test_corrupt_plist() -> None:
    with pytest.raises(CorruptBookmarkDataError):
        safari.parse_bookmarks(b"not a plist")


def test_non_list_root_is_corrupt() -> None:
    with pytest.raises(CorruptBookmarkDataError):
        safari.parse_bookmarks(plistlib.dumps({"WebBookmarkType": "WebBookmarkTypeProxy"}))


def test_unsupported_platform_reports_clearly(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(safari, "is_macos", lambda: False)
    provider = safari.SafariProvider()

    assert provider.is_supported_platform() is False
    assert provider.detect_profiles() == []
    with pytest.raises(UnsupportedPlatformError):
        provider.load_bookmarks(_profile(tmp_path / "Bookmarks.plist"))


def test_permission_denied_gives_full_disk_access_guidance(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(safari, "is_macos", lambda: True)
    path = tmp_path / "Bookmarks.plist"
    path.write_bytes(plistlib.dumps(_PLIST))

    def deny(self, *args, **kwargs):
        raise PermissionError

    monkeypatch.setattr(Path, "read_bytes", deny)

    with pytest.raises(PermissionDeniedError) as error:
        safari.SafariProvider().load_bookmarks(_profile(path))
    assert "Full Disk Access" in str(error.value)


def test_reads_a_plist_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(safari, "is_macos", lambda: True)
    path = tmp_path / "Bookmarks.plist"
    path.write_bytes(plistlib.dumps(_PLIST))

    root = safari.SafariProvider().load_bookmarks(_profile(path))
    assert root.name == "Safari"
    assert root.bookmark_count == 2
