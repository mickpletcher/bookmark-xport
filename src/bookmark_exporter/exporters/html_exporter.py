"""Netscape Bookmark File Format writer.

Output is deterministic: the same folder always produces the same bytes, which
is what makes the exporter testable.
"""

from __future__ import annotations

from datetime import datetime
from html import escape

from bookmark_exporter.models import Bookmark, BookmarkFolder

_HEADER = (
    "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n"
    "<!-- This is an automatically generated file.\n"
    "     It will be read and overwritten.\n"
    "     DO NOT EDIT! -->\n"
    '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
    "<TITLE>Bookmarks</TITLE>\n"
    "<H1>Bookmarks</H1>\n"
)

_INDENT = "    "


def _escape(value: str) -> str:
    return escape(value, quote=True)


def _timestamp(value: datetime | None) -> str:
    if value is None:
        return ""
    try:
        return f' ADD_DATE="{int(value.timestamp())}"'
    except (OverflowError, OSError, ValueError):
        return ""


def _render_bookmark(bookmark: Bookmark, depth: int) -> str:
    pad = _INDENT * depth
    return (
        f'{pad}<DT><A HREF="{_escape(bookmark.url)}"{_timestamp(bookmark.added)}>'
        f"{_escape(bookmark.title)}</A>\n"
    )


def _render_folder(folder: BookmarkFolder, depth: int) -> str:
    pad = _INDENT * depth
    parts = [
        f"{pad}<DT><H3{_timestamp(folder.added)}>{_escape(folder.name)}</H3>\n",
        f"{pad}<DL><p>\n",
    ]
    parts.extend(_render_children(folder, depth + 1))
    parts.append(f"{pad}</DL><p>\n")
    return "".join(parts)


def _render_children(folder: BookmarkFolder, depth: int) -> list[str]:
    parts = [_render_folder(child, depth) for child in folder.folders]
    parts.extend(_render_bookmark(bookmark, depth) for bookmark in folder.bookmarks)
    return parts


def render(folder: BookmarkFolder) -> str:
    """Render one folder and all of its descendants as bookmark HTML.

    The selected folder becomes the top-level heading in the exported file.
    Siblings and parents are never included.
    """
    body = "".join(
        [
            "<DL><p>\n",
            _render_folder(folder, depth=1),
            "</DL><p>\n",
        ]
    )
    return _HEADER + body
