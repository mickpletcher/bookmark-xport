from __future__ import annotations

from pathlib import Path

import pytest

from bookmark_exporter.models import Bookmark, BookmarkFolder
from bookmark_exporter.services.export_service import (
    ExportError,
    export_folder,
    suggested_filename,
)
from bookmark_exporter.utils.paths import sanitize_filename


def _folder() -> BookmarkFolder:
    return BookmarkFolder(
        name="Development",
        folders=[BookmarkFolder(name="Tools", bookmarks=[Bookmark("T", "https://a.test")])],
        bookmarks=[Bookmark("Docs", "https://example.com")],
    )


def test_writes_utf8_html(tmp_path: Path) -> None:
    destination = tmp_path / "out.html"
    result = export_folder(_folder(), destination)

    assert result.path == destination
    assert result.bookmark_count == 2
    assert result.folder_count == 1
    assert "Development" in destination.read_text(encoding="utf-8")


def test_adds_an_html_suffix_when_missing(tmp_path: Path) -> None:
    result = export_folder(_folder(), tmp_path / "out")
    assert result.path.name == "out.html"


def test_creates_missing_parent_directories(tmp_path: Path) -> None:
    result = export_folder(_folder(), tmp_path / "a" / "b" / "out.html")
    assert result.path.is_file()


def test_suggested_filename() -> None:
    assert suggested_filename(_folder()) == "Development-Bookmarks.html"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("../../etc/passwd", "etc-passwd"),
        ("C:\\Windows\\System32", "C-Windows-System32"),
        ("con", "Bookmarks"),
        ("", "Bookmarks"),
        ("   ", "Bookmarks"),
        ("...", "Bookmarks"),
        ("Café ünïcode", "Café ünïcode"),
    ],
)
def test_sanitize_filename(name: str, expected: str) -> None:
    assert sanitize_filename(name) == expected


def test_sanitized_names_cannot_escape_the_chosen_directory() -> None:
    assert "/" not in sanitize_filename("../../etc/passwd")
    assert "\\" not in sanitize_filename("..\\..\\windows")


def test_unwritable_destination_reports_an_export_error(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("bookmark_exporter.services.export_service.os.access", lambda *_: False)
    with pytest.raises(ExportError):
        export_folder(_folder(), tmp_path / "out.html")
