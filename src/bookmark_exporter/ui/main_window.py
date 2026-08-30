"""Main application window."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, SignalInstance, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from bookmark_exporter.browsers.base import BrowserError
from bookmark_exporter.models import BookmarkFolder, BrowserProfile
from bookmark_exporter.services import export_service
from bookmark_exporter.services.browser_discovery import (
    BrowserStatus,
    DiscoveredBrowser,
    discover,
)
from bookmark_exporter.ui.models import build_folder_model, folder_from_index
from bookmark_exporter.utils.preferences import Preferences

log = logging.getLogger(__name__)


class _TaskSignals(QObject):
    succeeded = Signal(object)
    failed = Signal(str)


class _Task(QRunnable):
    """Runs one callable off the GUI thread and reports back by signal."""

    def __init__(self, work: Callable[[], object]) -> None:
        super().__init__()
        self.setAutoDelete(False)
        self._work = work
        self.signals = _TaskSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self._work()
        except BrowserError as exc:
            self._emit(self.signals.failed, str(exc))
        except Exception:
            log.exception("Background task failed")
            self._emit(
                self.signals.failed,
                "Something went wrong reading the bookmarks. See the log for details.",
            )
        else:
            self._emit(self.signals.succeeded, result)

    @staticmethod
    def _emit(signal: SignalInstance, payload: object) -> None:
        # The window may have been closed while this task was running.
        try:
            signal.emit(payload)
        except RuntimeError:
            log.debug("Result discarded; the receiver is gone.")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Bookmark Folder Exporter")
        self.resize(720, 560)

        self._pool = QThreadPool.globalInstance()
        self._preferences = Preferences()
        self._browsers: list[DiscoveredBrowser] = []
        self._selected_folder: BookmarkFolder | None = None
        self._tasks: set[_Task] = set()

        self._build_ui()
        self._start_discovery()

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)

        selectors = QFormLayout()
        self.browser_combo = QComboBox()
        self.browser_combo.setAccessibleName("Browser")
        self.browser_combo.currentIndexChanged.connect(self._on_browser_changed)

        self.profile_combo = QComboBox()
        self.profile_combo.setAccessibleName("Profile")
        self.profile_combo.currentIndexChanged.connect(self._on_profile_changed)

        selectors.addRow("&Browser:", self.browser_combo)
        selectors.addRow("&Profile:", self.profile_combo)
        layout.addLayout(selectors)

        self.tree = QTreeView()
        self.tree.setAccessibleName("Bookmark folders")
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tree, stretch=1)

        self.summary_label = QLabel("No folder selected.")
        self.summary_label.setAccessibleName("Selected folder summary")
        layout.addWidget(self.summary_label)

        actions = QHBoxLayout()
        self.status_label = QLabel("Looking for installed browsers...")
        self.status_label.setAccessibleName("Status")
        self.status_label.setWordWrap(True)
        actions.addWidget(self.status_label, stretch=1)

        self.export_button = QPushButton("&Export Folder")
        self.export_button.setEnabled(False)
        self.export_button.setDefault(True)
        self.export_button.clicked.connect(self._on_export)
        actions.addWidget(self.export_button)
        layout.addLayout(actions)

        self.setCentralWidget(central)
        QShortcut(QKeySequence.StandardKey.Quit, self, self.close)

    # Discovery ---------------------------------------------------------

    def _start_discovery(self) -> None:
        self._set_busy(True, "Looking for installed browsers...")
        task = _Task(discover)
        task.signals.succeeded.connect(self._on_discovered)
        task.signals.failed.connect(self._on_error)
        self._start(task)

    @Slot(object)
    def _on_discovered(self, result: object) -> None:
        self._browsers = list(result)  # type: ignore[arg-type]
        self.browser_combo.blockSignals(True)
        self.browser_combo.clear()

        first_usable = -1
        for index, browser in enumerate(self._browsers):
            label = browser.browser_name
            if browser.status is not BrowserStatus.AVAILABLE:
                label = f"{browser.browser_name} (unavailable)"
            self.browser_combo.addItem(label, browser)
            if not browser.is_usable:
                item = self.browser_combo.model().item(index)
                if item is not None:
                    item.setEnabled(False)
            elif first_usable < 0:
                first_usable = index
        self.browser_combo.blockSignals(False)

        self._set_busy(False, "")
        if first_usable < 0:
            self.status_label.setText(
                "No readable bookmark data was found for any supported browser."
            )
            return
        self.browser_combo.setCurrentIndex(first_usable)

    # Profiles and bookmarks --------------------------------------------

    @Slot()
    def _on_browser_changed(self) -> None:
        browser = self.browser_combo.currentData()
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profile_combo.blockSignals(False)
        self._clear_tree()

        if not isinstance(browser, DiscoveredBrowser):
            return
        if not browser.is_usable:
            self.status_label.setText(browser.message or "This browser is unavailable.")
            return

        self.profile_combo.blockSignals(True)
        for profile in browser.profiles:
            self.profile_combo.addItem(profile.display_name, profile)
        self.profile_combo.blockSignals(False)
        self.profile_combo.setCurrentIndex(0)
        self._load_bookmarks()

    @Slot()
    def _on_profile_changed(self) -> None:
        if self.profile_combo.currentIndex() >= 0:
            self._load_bookmarks()

    def _load_bookmarks(self) -> None:
        browser = self.browser_combo.currentData()
        profile = self.profile_combo.currentData()
        if not isinstance(browser, DiscoveredBrowser) or not isinstance(profile, BrowserProfile):
            return

        self._clear_tree()
        self._set_busy(True, f"Loading {profile.display_name}...")
        provider = browser.provider
        task = _Task(lambda: provider.load_bookmarks(profile))
        task.signals.succeeded.connect(self._on_bookmarks_loaded)
        task.signals.failed.connect(self._on_error)
        self._start(task)

    @Slot(object)
    def _on_bookmarks_loaded(self, result: object) -> None:
        if not isinstance(result, BookmarkFolder):
            self._on_error("The bookmarks could not be read.")
            return

        model = build_folder_model(result)
        self.tree.setModel(model)
        self.tree.expandToDepth(1)
        selection = self.tree.selectionModel()
        if selection is not None:
            selection.selectionChanged.connect(self._on_selection_changed)
        self._set_busy(False, f"{result.bookmark_count} bookmarks loaded.")

    @Slot()
    def _on_selection_changed(self) -> None:
        model = self.tree.model()
        indexes = self.tree.selectionModel().selectedIndexes() if self.tree.selectionModel() else []
        folder = folder_from_index(model, indexes[0]) if indexes else None
        self._selected_folder = folder

        if folder is None:
            self.summary_label.setText("No folder selected.")
            self.export_button.setEnabled(False)
            return

        self.summary_label.setText(
            f"Selected: {folder.name or '(untitled)'}  |  "
            f"{folder.bookmark_count} bookmarks  |  {folder.subfolder_count} subfolders"
        )
        self.export_button.setEnabled(True)

    # Export -------------------------------------------------------------

    @Slot()
    def _on_export(self) -> None:
        folder = self._selected_folder
        if folder is None:
            return

        start_dir = self._preferences.last_export_directory or str(Path.home())
        suggested = str(Path(start_dir) / export_service.suggested_filename(folder))
        destination, _ = QFileDialog.getSaveFileName(
            self, "Export Bookmark Folder", suggested, "Bookmark HTML (*.html)"
        )
        if not destination:
            return

        try:
            result = export_service.export_folder(folder, destination)
        except export_service.ExportError as exc:
            QMessageBox.warning(self, "Export failed", str(exc))
            self.status_label.setText("Export failed.")
            return

        self._preferences.last_export_directory = str(result.path.parent)
        self.status_label.setText(
            f"Exported {result.bookmark_count} bookmarks to {result.path.name}."
        )

    # Helpers -------------------------------------------------------------

    def _start(self, task: _Task) -> None:
        # Qt does not own the Python signal object, so the task must be kept
        # alive here until it reports back.
        self._tasks.add(task)
        task.signals.succeeded.connect(lambda _=None, t=task: self._tasks.discard(t))
        task.signals.failed.connect(lambda _=None, t=task: self._tasks.discard(t))
        self._pool.start(task)

    def _clear_tree(self) -> None:
        self.tree.setModel(None)
        self._selected_folder = None
        self.summary_label.setText("No folder selected.")
        self.export_button.setEnabled(False)

    def _set_busy(self, busy: bool, message: str) -> None:
        self.setCursor(Qt.CursorShape.BusyCursor if busy else Qt.CursorShape.ArrowCursor)
        self.browser_combo.setEnabled(not busy)
        self.profile_combo.setEnabled(not busy)
        if message:
            self.status_label.setText(message)

    @Slot(str)
    def _on_error(self, message: str) -> None:
        self._set_busy(False, message)
        log.warning("User-facing error: %s", message)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        self._pool.waitForDone(2000)
        super().closeEvent(event)
