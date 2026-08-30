"""Logging setup and privacy helpers.

Bookmark data is sensitive. Full URLs are never written at normal log levels;
callers pass URLs through :func:`redact_url` unless logging at DEBUG.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path
from urllib.parse import urlsplit

from bookmark_exporter.utils.paths import is_macos, is_windows, local_app_data

_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def log_directory() -> Path:
    """Per-user directory for diagnostic logs."""
    if is_windows():
        return local_app_data() / "bookmark-xport" / "logs"
    if is_macos():
        return Path.home() / "Library" / "Logs" / "bookmark-xport"
    return Path.home() / ".local" / "state" / "bookmark-xport"


def redact_url(url: str) -> str:
    """Return scheme and host only, so a log never leaks a full URL."""
    if not url:
        return "<empty>"
    try:
        parts = urlsplit(url)
    except ValueError:
        return "<unparsable url>"
    if not parts.scheme:
        return "<relative url>"
    if not parts.hostname:
        return f"{parts.scheme}:<redacted>"
    hostname = parts.hostname
    if ":" in hostname:
        hostname = f"[{hostname}]"
    try:
        port = parts.port
    except ValueError:
        return "<unparsable url>"
    authority = f"{hostname}:{port}" if port is not None else hostname
    return f"{parts.scheme}://{authority}/<redacted>"


def configure_logging(verbose: bool = False) -> Path | None:
    """Configure root logging to a rotating file and the console.

    Returns the log file path, or None when no writable location was available.
    Logging must never prevent the application from starting.
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if verbose else logging.INFO)

    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(logging.Formatter(_LOG_FORMAT))
    root.addHandler(console)

    try:
        directory = log_directory()
        directory.mkdir(parents=True, exist_ok=True)
        log_path = directory / "bookmark-xport.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=512_000, backupCount=2, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        root.addHandler(file_handler)
        return log_path
    except OSError:
        root.warning("No writable log directory; logging to console only.")
        return None
