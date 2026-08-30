from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from bookmark_exporter.browsers.base import CorruptBookmarkDataError, ProfileNotFoundError
from bookmark_exporter.browsers.chrome import ChromeProvider
from bookmark_exporter.browsers.chromium import ChromiumProvider, parse_bookmarks
from bookmark_exporter.models import BrowserProfile
from bookmark_exporter.utils.paths import is_windows


def test_parses_roots_and_nesting(chromium_json: str) -> None:
    root = parse_bookmarks(chromium_json)

    assert [folder.name for folder in root.folders] == [
        "Bookmarks bar",
        "Other Bookmarks",
        "Mobile Bookmarks",
    ]

    bar = root.folders[0]
    development = bar.folders[0]
    assert development.name == "Development"
    assert [folder.name for folder in development.folders] == ["Tools", "Empty"]
    assert [bookmark.title for bookmark in development.bookmarks] == ["Example Docs"]
    assert [
        getattr(child, "name", getattr(child, "title", "")) for child in development.children
    ] == [
        "Example Docs",
        "Tools",
        "Empty",
    ]


def test_skips_malformed_and_unknown_nodes(chromium_json: str) -> None:
    development = parse_bookmarks(chromium_json).folders[0].folders[0]

    titles = [bookmark.title for bookmark in development.bookmarks]
    assert "Missing URL" not in titles
    assert "Unknown node" not in titles


def test_preserves_unicode(chromium_json: str) -> None:
    bar = parse_bookmarks(chromium_json).folders[0]
    assert bar.bookmarks[0].title == "Café ünïcode ✓"


def test_counts_are_recursive(chromium_json: str) -> None:
    development = parse_bookmarks(chromium_json).folders[0].folders[0]
    assert development.bookmark_count == 2
    assert development.subfolder_count == 2


def test_empty_folder_has_no_children(chromium_json: str) -> None:
    empty = parse_bookmarks(chromium_json).folders[0].folders[0].folders[1]
    assert empty.name == "Empty"
    assert empty.bookmarks == []
    assert empty.folders == []


def test_source_ids_are_unique(chromium_json: str) -> None:
    root = parse_bookmarks(chromium_json)
    ids = [folder.source_id for folder in root.walk()]
    assert len(ids) == len(set(ids))
    source_id = ids[3]
    assert source_id is not None
    assert root.find(source_id) is not None


def test_date_added_is_converted(chromium_json: str) -> None:
    bookmark = parse_bookmarks(chromium_json).folders[0].folders[0].bookmarks[0]
    assert bookmark.added is not None
    assert bookmark.added.year == 2022


@pytest.mark.parametrize("payload", ["", "not json", "[]", "{}", '{"roots": []}'])
def test_malformed_documents(payload: str) -> None:
    with pytest.raises(CorruptBookmarkDataError):
        parse_bookmarks(payload)


def test_unparsable_root_is_skipped_not_fatal() -> None:
    assert parse_bookmarks('{"roots": {"bookmark_bar": 3}}').folders == []


def test_deeply_nested_input_does_not_recurse_without_bound() -> None:
    node: dict[str, Any] = {"type": "folder", "name": "leaf", "children": []}
    for _ in range(500):
        node = {"type": "folder", "name": "deep", "children": [node]}

    root = parse_bookmarks(json.dumps({"roots": {"bookmark_bar": node}}))
    assert root.folders[0].subfolder_count < 500


class _FakeChromium(ChromiumProvider):
    browser_id = "fake"
    browser_name = "Fake Chromium"

    def __init__(self, root: Path) -> None:
        self._root = root

    def user_data_dirs(self) -> list[Path]:
        return [self._root]


def _write_profile(root: Path, directory: str, payload: str, display_name: str | None) -> None:
    profile_dir = root / directory
    profile_dir.mkdir(parents=True)
    (profile_dir / "Bookmarks").write_text(payload, encoding="utf-8")
    if display_name is not None:
        (profile_dir / "Preferences").write_text(
            json.dumps({"profile": {"name": display_name}}), encoding="utf-8"
        )


def test_detects_multiple_profiles(tmp_path: Path, chromium_json: str) -> None:
    user_data = tmp_path / "User Data"
    _write_profile(user_data, "Default", chromium_json, "Personal")
    _write_profile(user_data, "Profile 1", chromium_json, None)
    (user_data / "Crashpad").mkdir()

    profiles = _FakeChromium(user_data).detect_profiles()

    assert [profile.display_name for profile in profiles] == ["Personal", "Profile 1"]


def test_missing_user_data_directory_yields_no_profiles(tmp_path: Path) -> None:
    assert _FakeChromium(tmp_path / "absent").detect_profiles() == []


def test_load_bookmarks_round_trip(tmp_path: Path, chromium_json: str) -> None:
    user_data = tmp_path / "User Data"
    _write_profile(user_data, "Default", chromium_json, "Personal")
    provider = _FakeChromium(user_data)

    profile = provider.detect_profiles()[0]
    root = provider.load_bookmarks(profile)

    assert root.name == "Personal"
    assert root.bookmark_count == 4


def test_load_bookmarks_missing_file(tmp_path: Path) -> None:
    provider = _FakeChromium(tmp_path)
    profile = BrowserProfile(
        browser_id="fake",
        browser_name="Fake Chromium",
        profile_id="x",
        display_name="Gone",
        data_path=str(tmp_path / "nope" / "Bookmarks"),
    )
    with pytest.raises(ProfileNotFoundError):
        provider.load_bookmarks(profile)


@pytest.mark.skipif(not is_windows(), reason="LOCALAPPDATA is a Windows concept")
def test_chrome_paths_come_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", r"D:\elsewhere\Local")
    expected = Path(r"D:\elsewhere\Local") / "Google" / "Chrome" / "User Data"
    assert ChromeProvider().user_data_dirs() == [expected]
