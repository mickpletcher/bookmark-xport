"""Path helpers. No username or home directory is ever hard-coded."""

from __future__ import annotations

import os
import re
import sys
import unicodedata
from pathlib import Path

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# Reserved on Windows regardless of extension.
_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def local_app_data() -> Path:
    """Windows per-user local application data directory."""
    return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")


def roaming_app_data() -> Path:
    """Windows per-user roaming application data directory."""
    return Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")


def mac_application_support() -> Path:
    """macOS per-user Application Support directory."""
    return Path.home() / "Library" / "Application Support"


def is_windows() -> bool:
    return sys.platform.startswith("win")


def is_macos() -> bool:
    return sys.platform == "darwin"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def sanitize_filename(name: str, fallback: str = "Bookmarks") -> str:
    """Return a filename that is safe on Windows and macOS.

    Strips directory separators, control characters, and Windows reserved names.
    A folder called ``../../etc`` cannot escape the directory the user chose.
    """
    cleaned = unicodedata.normalize("NFC", name).strip()
    cleaned = _INVALID_FILENAME_CHARS.sub("-", cleaned)
    cleaned = cleaned.strip(". -")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"-{2,}", "-", cleaned)

    if not cleaned or cleaned.upper() in _RESERVED_NAMES:
        cleaned = fallback

    return cleaned[:120]


def suggested_export_filename(folder_name: str) -> str:
    """Suggested save-dialog filename for an exported folder."""
    return f"{sanitize_filename(folder_name)}-Bookmarks.html"
