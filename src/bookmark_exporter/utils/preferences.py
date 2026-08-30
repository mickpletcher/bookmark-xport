"""Small user preference store.

Holds the last export directory and nothing else. Bookmark titles, URLs, and
browser profile contents are never persisted here.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from bookmark_exporter.utils.paths import is_macos, is_windows, roaming_app_data

log = logging.getLogger(__name__)

_ALLOWED_KEYS = {"last_export_directory"}


def config_path() -> Path:
    if is_windows():
        base = roaming_app_data() / "bookmark-xport"
    elif is_macos():
        base = Path.home() / "Library" / "Preferences" / "bookmark-xport"
    else:
        base = Path.home() / ".config" / "bookmark-xport"
    return base / "preferences.json"


class Preferences:
    """Load-on-demand, save-on-change preference store."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or config_path()
        self._values: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if isinstance(raw, dict):
            self._values = {
                key: value
                for key, value in raw.items()
                if key in _ALLOWED_KEYS and isinstance(value, str)
            }

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(self._values, indent=2), encoding="utf-8")
        except OSError:
            log.debug("Could not write preferences to %s", self._path, exc_info=True)

    @property
    def last_export_directory(self) -> str | None:
        return self._values.get("last_export_directory")

    @last_export_directory.setter
    def last_export_directory(self, value: str) -> None:
        self._values["last_export_directory"] = value
        self._save()
