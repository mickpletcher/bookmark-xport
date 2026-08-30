from __future__ import annotations

import logging
from pathlib import Path

import pytest

from bookmark_exporter.utils import logging_setup
from bookmark_exporter.utils.logging_setup import configure_logging, redact_url


def test_redact_url_removes_credentials_and_path() -> None:
    redacted = redact_url("https://user:private-password@example.com/private/path?token=secret")

    assert redacted == "https://example.com/<redacted>"
    assert "user" not in redacted
    assert "password" not in redacted
    assert "token" not in redacted


def test_redact_url_preserves_a_non_default_port() -> None:
    assert redact_url("https://example.com:8443/private") == "https://example.com:8443/<redacted>"


def test_redact_url_formats_ipv6_without_userinfo() -> None:
    assert redact_url("https://user:password@[2001:db8::1]:9443/private") == (
        "https://[2001:db8::1]:9443/<redacted>"
    )


def test_redact_url_rejects_an_invalid_port() -> None:
    assert redact_url("https://example.com:not-a-port/private") == "<unparsable url>"


def test_logging_a_redacted_url_does_not_emit_sensitive_values(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        logging.getLogger("bookmark_exporter.test").info(
            "URL: %s", redact_url("https://person:credential@example.com/private")
        )

    assert "person" not in caplog.text
    assert "credential" not in caplog.text
    assert "/private" not in caplog.text


def test_redact_url_handles_empty_relative_and_hostless_values() -> None:
    assert redact_url("") == "<empty>"
    assert redact_url("relative/path") == "<relative url>"
    assert redact_url("mailto:person@example.com") == "mailto:<redacted>"
    assert redact_url("https://[invalid") == "<unparsable url>"


def test_configure_logging_writes_to_the_selected_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = logging.getLogger()
    previous_level = root.level
    previous_handlers = set(root.handlers)
    monkeypatch.setattr(logging_setup, "log_directory", lambda: tmp_path)

    log_path = configure_logging(verbose=True)
    logging.getLogger("bookmark_exporter.synthetic").debug("synthetic diagnostic")

    for handler in list(root.handlers):
        if handler not in previous_handlers:
            handler.flush()
            root.removeHandler(handler)
            handler.close()
    root.setLevel(previous_level)

    assert log_path == tmp_path / "bookmark-xport.log"
    assert "synthetic diagnostic" in log_path.read_text(encoding="utf-8")


def test_configure_logging_falls_back_when_directory_is_unwritable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    root = logging.getLogger()
    previous_level = root.level
    previous_handlers = set(root.handlers)
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    monkeypatch.setattr(logging_setup, "log_directory", lambda: blocker / "logs")

    with caplog.at_level(logging.WARNING):
        assert configure_logging() is None

    for handler in list(root.handlers):
        if handler not in previous_handlers:
            root.removeHandler(handler)
            handler.close()
    root.setLevel(previous_level)
    assert "logging to console only" in caplog.text
