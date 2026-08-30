"""Smoke test for the Qt layer.

Skipped when PySide6 is not installed so the parsing and export suites remain
runnable without a GUI toolkit.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import cast

import pytest

pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402
from pytestqt.qtbot import QtBot  # noqa: E402

from bookmark_exporter.browsers.base import (  # noqa: E402
    BookmarkDataUnavailableError,
    BrowserProvider,
)
from bookmark_exporter.models import Bookmark, BookmarkFolder, BrowserProfile  # noqa: E402
from bookmark_exporter.services.browser_discovery import (  # noqa: E402
    BrowserStatus,
    DiscoveredBrowser,
)
from bookmark_exporter.ui.main_window import MainWindow  # noqa: E402
from bookmark_exporter.ui.models import build_folder_model, folder_from_index  # noqa: E402


@pytest.fixture(scope="module")
def app() -> QApplication:
    instance = QApplication.instance()
    return cast(QApplication, instance) if instance is not None else QApplication([])


def _tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="Bookmarks",
        children=[
            BookmarkFolder(
                name="Development",
                children=[BookmarkFolder(name="Tools"), Bookmark("Docs", "https://example.com")],
            )
        ],
    )


def _profile(profile_id: str, display_name: str) -> BrowserProfile:
    return BrowserProfile("stub", "Stub", profile_id, display_name, profile_id)


class _Provider(BrowserProvider):
    browser_id = "stub"
    browser_name = "Stub Browser"

    def __init__(
        self,
        profiles: list[BrowserProfile],
        roots: dict[str, BookmarkFolder] | None = None,
        error: Exception | None = None,
    ) -> None:
        self._profiles = profiles
        self._roots = roots or {}
        self._error = error

    def is_supported_platform(self) -> bool:
        return True

    def detect_profiles(self) -> list[BrowserProfile]:
        return self._profiles

    def load_bookmarks(self, profile: BrowserProfile) -> BookmarkFolder:
        if self._error is not None:
            raise self._error
        return self._roots[profile.profile_id]


def _window_without_discovery(qtbot: QtBot, monkeypatch: pytest.MonkeyPatch) -> MainWindow:
    monkeypatch.setattr(MainWindow, "_start_discovery", lambda self: None)
    window = MainWindow()
    qtbot.addWidget(window)
    return window


def _discovered(provider: _Provider) -> DiscoveredBrowser:
    return DiscoveredBrowser(
        provider=provider,
        status=BrowserStatus.AVAILABLE,
        profiles=provider.detect_profiles(),
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
    window = MainWindow()
    try:
        assert window.export_button.isEnabled() is False
        assert window.windowTitle() == "Bookmark Folder Exporter"
    finally:
        window.close()


def test_discovery_loads_the_first_usable_browser(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    profile = _profile("one", "Profile One")
    provider = _Provider([profile], {"one": _tree()})
    window = _window_without_discovery(qtbot, monkeypatch)

    window._on_discovered([_discovered(provider)])
    qtbot.waitUntil(lambda: not window._tasks)

    assert window.profile_combo.currentData() == profile
    assert window.tree.model() is not None
    assert window.status_label.text() == "1 bookmarks loaded."


def test_browser_and_profile_switching_load_the_selected_tree(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    first_profile = _profile("first", "First")
    second_profile = _profile("second", "Second")
    other_profile = BrowserProfile("other", "Other", "other", "Other", "other")
    first_provider = _Provider(
        [first_profile, second_profile],
        {
            "first": BookmarkFolder("First", children=[Bookmark("One", "https://one.test")]),
            "second": BookmarkFolder(
                "Second",
                children=[
                    Bookmark("One", "https://one.test"),
                    Bookmark("Two", "https://two.test"),
                ],
            ),
        },
    )
    other_provider = _Provider(
        [other_profile],
        {"other": BookmarkFolder("Other", children=[Bookmark("Three", "https://three.test")])},
    )
    other_provider.browser_id = "other"
    other_provider.browser_name = "Other Browser"
    window = _window_without_discovery(qtbot, monkeypatch)

    window._on_discovered([_discovered(first_provider), _discovered(other_provider)])
    qtbot.waitUntil(lambda: not window._tasks)
    window.profile_combo.setCurrentIndex(1)
    qtbot.waitUntil(lambda: not window._tasks)
    assert window.status_label.text() == "2 bookmarks loaded."

    window.browser_combo.setCurrentIndex(1)
    qtbot.waitUntil(lambda: not window._tasks)
    assert window.profile_combo.currentData() == other_profile
    assert window.status_label.text() == "1 bookmarks loaded."


def test_provider_failure_restores_idle_state(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    profile = _profile("broken", "Broken")
    provider = _Provider(
        [profile],
        error=BookmarkDataUnavailableError("Synthetic bookmark failure."),
    )
    window = _window_without_discovery(qtbot, monkeypatch)

    window._on_discovered([_discovered(provider)])
    qtbot.waitUntil(lambda: not window._tasks)

    assert window.status_label.text() == "Synthetic bookmark failure."
    assert window.browser_combo.isEnabled()
    assert not window.export_button.isEnabled()


def test_selecting_and_exporting_a_folder(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    profile = _profile("one", "Profile One")
    provider = _Provider([profile], {"one": _tree()})
    window = _window_without_discovery(qtbot, monkeypatch)
    destination = tmp_path / "selected.html"

    def choose_destination(*args: object, **kwargs: object) -> tuple[str, str]:
        return str(destination), "Bookmark HTML (*.html)"

    monkeypatch.setattr(
        "bookmark_exporter.ui.main_window.QFileDialog.getSaveFileName", choose_destination
    )

    window._on_discovered([_discovered(provider)])
    qtbot.waitUntil(lambda: not window._tasks)
    model = window.tree.model()
    assert model is not None
    root_index = model.index(0, 0)
    selected_index = model.index(0, 0, root_index)
    window.tree.setCurrentIndex(selected_index)
    qtbot.waitUntil(window.export_button.isEnabled)
    window.export_button.click()

    assert destination.is_file()
    assert "Development" in destination.read_text(encoding="utf-8")
    assert window.status_label.text() == "Exported 1 bookmarks to selected.html."
