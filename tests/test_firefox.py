from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Any, cast

import pytest

from bookmark_exporter.browsers.base import CorruptBookmarkDataError, ProfileNotFoundError
from bookmark_exporter.browsers.firefox import FirefoxProvider, build_tree
from bookmark_exporter.models import BrowserProfile

_SCHEMA = """
CREATE TABLE moz_places (id INTEGER PRIMARY KEY, url LONGVARCHAR);
CREATE TABLE moz_bookmarks (
    id INTEGER PRIMARY KEY,
    type INTEGER,
    fk INTEGER,
    parent INTEGER,
    position INTEGER,
    title LONGVARCHAR,
    dateAdded INTEGER,
    guid TEXT
);
"""

_PLACES: list[tuple[int, str]] = [
    (1, "https://example.com/alpha"),
    (2, "https://example.com/beta"),
    (3, "https://example.org/caf%C3%A9"),
    (4, "place:type=6&sort=14"),
]

# (id, type, fk, parent, position, title, dateAdded, guid)
_BOOKMARKS: list[tuple[int, int, int | None, int, int, str | None, int, str]] = [
    (1, 2, None, 0, 0, "", 0, "root________"),
    (2, 2, None, 1, 0, "", 1_600_000_000_000_000, "menu________"),
    (3, 2, None, 1, 1, "", 1_600_000_000_000_000, "toolbar_____"),
    (4, 2, None, 1, 2, "", 1_600_000_000_000_000, "tags________"),
    (5, 2, None, 1, 3, "", 1_600_000_000_000_000, "unfiled_____"),
    (10, 2, None, 3, 0, "Development", 1_600_000_001_000_000, "dev_________"),
    (11, 1, 2, 3, 1, "Beta", 1_600_000_002_000_000, "beta________"),
    (12, 1, 1, 3, 2, "Alpha", 1_600_000_003_000_000, "alpha_______"),
    (13, 1, 3, 10, 0, "Café ünïcode", 1_600_000_004_000_000, "cafe________"),
    (14, 3, None, 10, 1, None, 1_600_000_005_000_000, "sep_________"),
    (15, 1, 4, 10, 2, "Recent Tags", 1_600_000_006_000_000, "query_______"),
    (16, 1, 1, 4, 0, "Tagged", 1_600_000_007_000_000, "tagged______"),
]


def _make_places_db(path: Path) -> Path:
    connection = sqlite3.connect(path)
    try:
        connection.executescript(_SCHEMA)
        connection.executemany("INSERT INTO moz_places VALUES (?, ?)", _PLACES)
        connection.executemany(
            "INSERT INTO moz_bookmarks VALUES (?, ?, ?, ?, ?, ?, ?, ?)", _BOOKMARKS
        )
        connection.commit()
    finally:
        connection.close()
    return path


def _rows() -> list[tuple[object, ...]]:
    urls = dict(_PLACES)
    return [
        (
            row[0],
            row[3],
            row[1],
            row[5],
            row[4],
            row[6],
            row[7],
            urls.get(row[2]) if row[2] is not None else None,
        )
        for row in _BOOKMARKS
    ]


def test_builds_hierarchy_with_root_labels() -> None:
    root = build_tree(_rows())
    assert [folder.name for folder in root.folders] == [
        "Bookmarks Menu",
        "Bookmarks Toolbar",
        "Other Bookmarks",
    ]


def test_preserves_position_order() -> None:
    toolbar = build_tree(_rows()).folders[1]
    assert [bookmark.title for bookmark in toolbar.bookmarks] == ["Beta", "Alpha"]
    assert [folder.name for folder in toolbar.folders] == ["Development"]
    assert [getattr(child, "name", getattr(child, "title", "")) for child in toolbar.children] == [
        "Development",
        "Beta",
        "Alpha",
    ]


def test_skips_tags_separators_and_queries() -> None:
    root = build_tree(_rows())
    names = [folder.name for folder in root.walk()]
    assert "tags________" not in names

    development = root.folders[1].folders[0]
    assert [bookmark.title for bookmark in development.bookmarks] == ["Café ünïcode"]


def test_dates_are_converted() -> None:
    development = build_tree(_rows()).folders[1].folders[0]
    assert development.bookmarks[0].added is not None
    assert development.bookmarks[0].added.year == 2020


def test_missing_root_is_corrupt() -> None:
    with pytest.raises(CorruptBookmarkDataError):
        build_tree([(2, 1, 2, "Orphan", 0, 0, "x", "https://example.com")])


def test_malformed_rows_are_ignored() -> None:
    rows = _rows() + [("bad",), (None, None, None, None, None, None, None, None)]
    assert build_tree(rows).bookmark_count == 3


def test_load_bookmarks_does_not_modify_the_database(tmp_path: Path) -> None:
    database = _make_places_db(tmp_path / "places.sqlite")
    before = hashlib.sha256(database.read_bytes()).hexdigest()

    profile = BrowserProfile(
        browser_id="firefox",
        browser_name="Mozilla Firefox",
        profile_id=str(database),
        display_name="default-release",
        data_path=str(database),
    )
    root = FirefoxProvider().load_bookmarks(profile)

    assert root.bookmark_count == 3
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before


def test_locked_database_fallback_reads_a_temporary_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = _make_places_db(tmp_path / "places.sqlite")
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    real_connect = sqlite3.connect
    calls = 0

    def fail_first_connect(*args: Any, **kwargs: Any) -> sqlite3.Connection:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise sqlite3.OperationalError("synthetic lock")
        return cast(sqlite3.Connection, real_connect(*args, **kwargs))

    monkeypatch.setattr(sqlite3, "connect", fail_first_connect)
    profile = BrowserProfile(
        browser_id="firefox",
        browser_name="Mozilla Firefox",
        profile_id=str(database),
        display_name="default-release",
        data_path=str(database),
    )

    root = FirefoxProvider().load_bookmarks(profile)

    assert calls == 2
    assert root.bookmark_count == 3
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before


def test_load_bookmarks_missing_profile(tmp_path: Path) -> None:
    profile = BrowserProfile(
        browser_id="firefox",
        browser_name="Mozilla Firefox",
        profile_id="x",
        display_name="Gone",
        data_path=str(tmp_path / "places.sqlite"),
    )
    with pytest.raises(ProfileNotFoundError):
        FirefoxProvider().load_bookmarks(profile)


def test_detects_profiles_from_profiles_ini(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "Firefox"
    (root / "Profiles" / "abc.default-release").mkdir(parents=True)
    (root / "Profiles" / "def.dev").mkdir(parents=True)
    _make_places_db(root / "Profiles" / "abc.default-release" / "places.sqlite")
    _make_places_db(root / "Profiles" / "def.dev" / "places.sqlite")
    (root / "profiles.ini").write_text(
        "[Install123]\nDefault=Profiles/abc.default-release\n\n"
        "[Profile0]\nName=default-release\nIsRelative=1\nPath=Profiles/abc.default-release\n\n"
        "[Profile1]\nName=dev\nIsRelative=1\nPath=Profiles/def.dev\n\n"
        "[Profile2]\nName=stale\nIsRelative=1\nPath=Profiles/missing\n",
        encoding="utf-8",
    )

    provider = FirefoxProvider()
    monkeypatch.setattr(provider, "data_root", lambda: root)

    assert [profile.display_name for profile in provider.detect_profiles()] == [
        "default-release",
        "dev",
    ]


def test_no_profiles_ini_yields_no_profiles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = FirefoxProvider()
    monkeypatch.setattr(provider, "data_root", lambda: tmp_path)
    assert provider.detect_profiles() == []
