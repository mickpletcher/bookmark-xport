"""Application bootstrap."""

from __future__ import annotations

import logging
import sys

from bookmark_exporter.utils.logging_setup import configure_logging

log = logging.getLogger(__name__)


def run(argv: list[str] | None = None) -> int:
    """Start the GUI. Returns the process exit code."""
    args = list(sys.argv if argv is None else argv)
    verbose = "--verbose" in args
    log_path = configure_logging(verbose=verbose)
    log.info("Starting bookmark-xport; log file: %s", log_path)

    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        sys.stderr.write(
            "PySide6 is not installed. Install the project dependencies with:\n"
            "    pip install -e .\n"
        )
        return 1

    from bookmark_exporter.ui.main_window import MainWindow

    app = QApplication(args)
    app.setApplicationName("bookmark-xport")
    app.setOrganizationName("bookmark-xport")

    window = MainWindow()
    window.show()
    return app.exec()
