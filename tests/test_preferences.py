from __future__ import annotations

import json
from pathlib import Path

from bookmark_exporter.utils.preferences import Preferences


def test_preferences_load_only_the_allowed_string_value(tmp_path: Path) -> None:
    path = tmp_path / "preferences.json"
    path.write_text(
        json.dumps(
            {
                "last_export_directory": "C:/Exports",
                "bookmark_title": "private",
                "another": 42,
            }
        ),
        encoding="utf-8",
    )

    preferences = Preferences(path)

    assert preferences.last_export_directory == "C:/Exports"
    preferences.last_export_directory = "C:/Other"
    assert json.loads(path.read_text(encoding="utf-8")) == {"last_export_directory": "C:/Other"}


def test_corrupt_preferences_are_ignored(tmp_path: Path) -> None:
    path = tmp_path / "preferences.json"
    path.write_text("not json", encoding="utf-8")

    assert Preferences(path).last_export_directory is None


def test_preference_write_failure_does_not_raise(tmp_path: Path) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    preferences = Preferences(blocker / "preferences.json")

    preferences.last_export_directory = "C:/Exports"

    assert preferences.last_export_directory == "C:/Exports"
