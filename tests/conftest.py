"""Shared test fixtures. All bookmark data here is synthetic."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def chromium_json() -> str:
    return (FIXTURES / "chromium_bookmarks.json").read_text(encoding="utf-8")
