"""Export service.

Contains no Qt imports. The UI calls it; so could a future command-line entry
point (FU-002).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from bookmark_exporter.exporters.html_exporter import render
from bookmark_exporter.models import BookmarkFolder
from bookmark_exporter.utils.paths import suggested_export_filename

log = logging.getLogger(__name__)


class ExportError(Exception):
    """The export could not be written. Carries a user-facing message."""


@dataclass(frozen=True, slots=True)
class ExportResult:
    path: Path
    bookmark_count: int
    folder_count: int


def suggested_filename(folder: BookmarkFolder) -> str:
    return suggested_export_filename(folder.name)


def export_folder(folder: BookmarkFolder, destination: Path | str) -> ExportResult:
    """Write one folder and its descendants to a bookmark HTML file."""
    path = Path(destination)
    if not path.suffix:
        path = path.with_suffix(".html")

    html = render(folder)

    parent = path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ExportError(f"The folder '{parent}' could not be created.") from exc

    if not os.access(parent, os.W_OK):
        raise ExportError(f"The folder '{parent}' is not writable.")

    try:
        path.write_text(html, encoding="utf-8", newline="\n")
    except PermissionError as exc:
        raise ExportError(f"Permission was denied writing to '{path}'.") from exc
    except OSError as exc:
        raise ExportError(f"The file '{path}' could not be written.") from exc

    log.info(
        "Exported folder '%s' (%d bookmarks, %d subfolders)",
        folder.name,
        folder.bookmark_count,
        folder.subfolder_count,
    )
    return ExportResult(
        path=path,
        bookmark_count=folder.bookmark_count,
        folder_count=folder.subfolder_count,
    )
