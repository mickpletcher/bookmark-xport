"""Qt adapters for the normalized bookmark model.

The UI layer knows about folders and bookmarks. It never knows which browser
they came from.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from bookmark_exporter.models import BookmarkFolder

FOLDER_ROLE = Qt.ItemDataRole.UserRole + 1


def _item_for(folder: BookmarkFolder) -> QStandardItem:
    item = QStandardItem(folder.name or "(untitled)")
    item.setEditable(False)
    item.setData(folder, FOLDER_ROLE)
    item.setToolTip(
        f"{folder.bookmark_count} bookmarks, {folder.subfolder_count} subfolders"
    )
    item.setAccessibleText(
        f"{folder.name or 'untitled folder'}, {folder.bookmark_count} bookmarks"
    )
    for child in folder.folders:
        item.appendRow(_item_for(child))
    return item


def build_folder_model(root: BookmarkFolder) -> QStandardItemModel:
    """Build a tree model containing every folder under (and including) root."""
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Folder"])
    model.invisibleRootItem().appendRow(_item_for(root))
    return model


def folder_from_index(model: QStandardItemModel, index) -> BookmarkFolder | None:
    if not index.isValid():
        return None
    value = model.data(index, FOLDER_ROLE)
    return value if isinstance(value, BookmarkFolder) else None
