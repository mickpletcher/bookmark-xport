"""Browser-independent bookmark models.

All UI and export code operates on these types. Nothing here knows how any
particular browser stores its data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator


@dataclass(slots=True)
class Bookmark:
    """A single bookmark."""

    title: str
    url: str
    added: datetime | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class BookmarkFolder:
    """A folder of bookmarks, holding child folders and bookmarks in order."""

    name: str
    folders: list["BookmarkFolder"] = field(default_factory=list)
    bookmarks: list[Bookmark] = field(default_factory=list)
    source_id: str | None = None
    added: datetime | None = None

    def walk(self) -> Iterator["BookmarkFolder"]:
        """Yield this folder and every descendant folder, depth first."""
        yield self
        for child in self.folders:
            yield from child.walk()

    @property
    def bookmark_count(self) -> int:
        """Bookmarks in this folder and all descendants."""
        return sum(len(folder.bookmarks) for folder in self.walk())

    @property
    def subfolder_count(self) -> int:
        """Descendant folders, excluding this one."""
        return sum(1 for _ in self.walk()) - 1

    def find(self, source_id: str) -> "BookmarkFolder | None":
        """Return the descendant folder with this source identifier."""
        for folder in self.walk():
            if folder.source_id == source_id:
                return folder
        return None


@dataclass(frozen=True, slots=True)
class BrowserProfile:
    """A single browser profile that may contain bookmarks."""

    browser_id: str
    browser_name: str
    profile_id: str
    display_name: str
    data_path: str


def assign_source_ids(root: BookmarkFolder) -> BookmarkFolder:
    """Give every folder a stable identifier derived from its position.

    Providers call this before returning a tree so the UI can refer to a folder
    without holding the object, and without depending on browser-specific ids.
    """

    def walk(folder: BookmarkFolder, prefix: str) -> None:
        folder.source_id = prefix
        for index, child in enumerate(folder.folders):
            walk(child, f"{prefix}.{index}")

    walk(root, "0")
    return root
