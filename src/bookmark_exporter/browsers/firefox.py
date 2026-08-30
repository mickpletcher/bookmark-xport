"""Mozilla Firefox.

Firefox stores bookmarks in ``places.sqlite``. Access here is strictly
read-only: the database is opened with ``mode=ro``, and when Firefox holds a
lock the file is copied to a temporary location and the copy is read instead.
The original is never opened for writing and never modified.
"""

from __future__ import annotations

import configparser
import logging
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from bookmark_exporter.browsers.base import (
    BookmarkDataUnavailableError,
    BrowserProvider,
    CorruptBookmarkDataError,
    PermissionDeniedError,
    ProfileNotFoundError,
)
from bookmark_exporter.models import (
    Bookmark,
    BookmarkFolder,
    BrowserProfile,
    assign_source_ids,
)
from bookmark_exporter.utils.paths import (
    is_linux,
    is_macos,
    is_windows,
    mac_application_support,
    roaming_app_data,
)

log = logging.getLogger(__name__)

_TYPE_BOOKMARK = 1
_TYPE_FOLDER = 2

_ROOT_GUID = "root________"
_TAGS_GUID = "tags________"

_ROOT_LABELS = {
    "toolbar_____": "Bookmarks Toolbar",
    "menu________": "Bookmarks Menu",
    "unfiled_____": "Other Bookmarks",
    "mobile______": "Mobile Bookmarks",
}

_MAX_DEPTH = 100

_QUERY = """
SELECT b.id, b.parent, b.type, b.title, b.position, b.dateAdded, b.guid, p.url
FROM moz_bookmarks AS b
LEFT JOIN moz_places AS p ON b.fk = p.id
ORDER BY b.parent, b.position, b.id
"""


def _unix_microseconds(value: object) -> datetime | None:
    try:
        micros = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if micros <= 0:
        return None
    try:
        return datetime.fromtimestamp(micros / 1_000_000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


@contextmanager
def _open_places(path: Path) -> Iterator[sqlite3.Connection]:
    """Yield a read-only connection, copying the database if it is locked."""
    uri = f"file:{path.as_posix()}?mode=ro"
    connection: sqlite3.Connection | None = None
    temp_dir: str | None = None
    try:
        try:
            connection = sqlite3.connect(uri, uri=True, timeout=2.0)
            connection.execute("SELECT 1 FROM moz_bookmarks LIMIT 1").fetchone()
        except sqlite3.Error:
            if connection is not None:
                connection.close()
                connection = None
            log.info("places.sqlite is not directly readable; using a temporary copy.")
            temp_dir = tempfile.mkdtemp(prefix="bookmark-xport-")
            copy = Path(temp_dir) / path.name
            shutil.copy2(path, copy)
            for suffix in ("-wal", "-shm"):
                sidecar = path.with_name(path.name + suffix)
                if sidecar.is_file():
                    shutil.copy2(sidecar, copy.with_name(copy.name + suffix))
            connection = sqlite3.connect(copy)
        yield connection
    finally:
        if connection is not None:
            connection.close()
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)


def build_tree(rows: list[tuple], root_name: str = "Bookmarks") -> BookmarkFolder:
    """Build a bookmark tree from ``moz_bookmarks`` rows.

    Rows are ``(id, parent, type, title, position, dateAdded, guid, url)`` and
    are assumed to be ordered by parent then position, which is what preserves
    the user's ordering.
    """
    children: dict[int, list[tuple]] = {}
    guid_by_id: dict[int, str] = {}
    root_id: int | None = None

    for row in rows:
        try:
            row_id, parent_id, node_type, title, _position, date_added, guid, url = row
        except (TypeError, ValueError):
            continue
        if not isinstance(row_id, int):
            continue
        guid_by_id[row_id] = guid if isinstance(guid, str) else ""
        if guid == _ROOT_GUID:
            root_id = row_id
            continue
        if isinstance(parent_id, int):
            children.setdefault(parent_id, []).append(
                (row_id, node_type, title, date_added, guid, url)
            )

    if root_id is None:
        raise CorruptBookmarkDataError("The Firefox bookmark database has no root folder.")

    def build(folder: BookmarkFolder, parent_id: int, depth: int) -> None:
        if depth > _MAX_DEPTH:
            return
        for row_id, node_type, title, date_added, guid, url in children.get(parent_id, []):
            if guid == _TAGS_GUID:
                continue
            name = title if isinstance(title, str) else ""
            if node_type == _TYPE_FOLDER:
                child = BookmarkFolder(
                    name=name or _ROOT_LABELS.get(guid or "", "Folder"),
                    added=_unix_microseconds(date_added),
                )
                build(child, row_id, depth + 1)
                folder.folders.append(child)
            elif node_type == _TYPE_BOOKMARK:
                # "place:" entries are saved queries, not real bookmarks.
                if not isinstance(url, str) or not url or url.startswith("place:"):
                    continue
                folder.bookmarks.append(
                    Bookmark(title=name, url=url, added=_unix_microseconds(date_added))
                )

    root = BookmarkFolder(name=root_name)
    build(root, root_id, depth=1)
    return assign_source_ids(root)


class FirefoxProvider(BrowserProvider):
    browser_id = "firefox"
    browser_name = "Mozilla Firefox"

    def data_root(self) -> Path | None:
        if is_windows():
            return roaming_app_data() / "Mozilla" / "Firefox"
        if is_macos():
            return mac_application_support() / "Firefox"
        if is_linux():
            return Path.home() / ".mozilla" / "firefox"
        return None

    def is_supported_platform(self) -> bool:
        return self.data_root() is not None

    def detect_profiles(self) -> list[BrowserProfile]:
        root = self.data_root()
        if root is None:
            return []

        ini_path = root / "profiles.ini"
        if not ini_path.is_file():
            return []

        parser = configparser.ConfigParser()
        try:
            parser.read(ini_path, encoding="utf-8")
        except PermissionError:
            raise PermissionDeniedError(
                "Access to the Firefox profile list was denied."
            ) from None
        except (OSError, configparser.Error) as exc:
            raise BookmarkDataUnavailableError(
                "The Firefox profile list could not be read."
            ) from exc

        profiles: list[BrowserProfile] = []
        for section in parser.sections():
            if not section.lower().startswith("profile"):
                continue
            relative_path = parser.get(section, "Path", fallback=None)
            if not relative_path:
                continue
            is_relative = parser.get(section, "IsRelative", fallback="1") == "1"
            directory = (root / relative_path) if is_relative else Path(relative_path)
            places = directory / "places.sqlite"
            if not places.is_file():
                continue
            profiles.append(
                BrowserProfile(
                    browser_id=self.browser_id,
                    browser_name=self.browser_name,
                    profile_id=str(places),
                    display_name=parser.get(section, "Name", fallback=directory.name),
                    data_path=str(places),
                )
            )
        return profiles

    def load_bookmarks(self, profile: BrowserProfile) -> BookmarkFolder:
        path = Path(profile.data_path)
        if not path.is_file():
            raise ProfileNotFoundError(
                f"The Firefox profile '{profile.display_name}' no longer exists."
            )
        try:
            with _open_places(path) as connection:
                rows = connection.execute(_QUERY).fetchall()
        except PermissionError:
            raise PermissionDeniedError(
                "Access to the Firefox bookmark database was denied."
            ) from None
        except sqlite3.DatabaseError as exc:
            raise CorruptBookmarkDataError(
                "The Firefox bookmark database could not be read. "
                "Closing Firefox and trying again may help."
            ) from exc
        except OSError as exc:
            raise BookmarkDataUnavailableError(
                "The Firefox bookmark database could not be opened."
            ) from exc

        return build_tree(rows, root_name=profile.display_name)
