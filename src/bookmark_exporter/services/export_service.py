"""Export service.

Contains no Qt imports. The UI calls it; so could a future command-line entry
point (FU-002).
"""

from __future__ import annotations

import logging
import os
import tempfile
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

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(html)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
    except PermissionError as exc:
        raise ExportError(f"Permission was denied writing to '{path}'.") from exc
    except OSError as exc:
        raise ExportError(f"The file '{path}' could not be written.") from exc
    finally:
        if temporary_path is not None and temporary_path.exists():
            try:
                temporary_path.unlink()
            except OSError:
                log.warning("A temporary export file could not be removed.")

    log.info(
        "Exported %d bookmarks and %d subfolders.",
        folder.bookmark_count,
        folder.subfolder_count,
    )
    return ExportResult(
        path=path,
        bookmark_count=folder.bookmark_count,
        folder_count=folder.subfolder_count,
    )
