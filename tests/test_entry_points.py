from __future__ import annotations

import builtins
from types import ModuleType

import pytest

from bookmark_exporter import __main__, app


def test_run_reports_a_missing_qt_dependency(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    real_import = builtins.__import__

    def import_without_qt(
        name: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> ModuleType:
        if name == "PySide6.QtWidgets":
            raise ImportError
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(app, "configure_logging", lambda verbose: None)
    monkeypatch.setattr(builtins, "__import__", import_without_qt)

    assert app.run(["bookmark-xport"]) == 1
    assert "PySide6 is not installed" in capsys.readouterr().err


def test_module_entry_point_returns_the_application_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(__main__, "run", lambda: 17)

    assert __main__.main() == 17
