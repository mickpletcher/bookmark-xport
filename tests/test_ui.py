"""Smoke test for the Qt layer.

Skipped when PySide6 is not installed so the parsing and export suites remain
runnable without a GUI toolkit.
"""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from bookmark_exporter.models import Bookmark, BookmarkFolder  # noqa: E402
from bookmark_exporter.ui.models import build_folder_model, folder_from_index  # noqa: E402


@pytest.fixture(scope="module")
def app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="Bookmarks",
        folders=[
            BookmarkFolder(
                name="Development",
                folders=[BookmarkFolder(name="Tools")],
                bookmarks=[Bookmark("Docs", "https://example.com")],
            )
        ],
    )


def test_model_mirrors_the_folder_tree(app: QApplication) -> None:
    model = build_folder_model(_tree())
    root_index = model.index(0, 0)

    assert model.data(root_index) == "Bookmarks"
    assert model.rowCount(root_index) == 1
    assert model.data(model.index(0, 0, root_index)) == "Development"


def test_folder_round_trips_through_the_model(app: QApplication) -> None:
    model = build_folder_model(_tree())
    index = model.index(0, 0, model.index(0, 0))

    folder = folder_from_index(model, index)
    assert folder is not None
    assert folder.name == "Development"
    assert folder.bookmark_count == 1


def test_main_window_constructs(app: QApplication) -> None:
    from bookmark_exporter.ui.main_window import MainWindow

    window = MainWindow()
    try:
        assert window.export_button.isEnabled() is False
        assert window.windowTitle() == "Bookmark Folder Exporter"
    finally:
        window.close()
