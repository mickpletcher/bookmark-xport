from __future__ import annotations

from bookmark_exporter.browsers.base import (
    BrowserNotInstalledError,
    BrowserProvider,
    PermissionDeniedError,
)
from bookmark_exporter.models import BookmarkFolder, BrowserProfile
from bookmark_exporter.services.browser_discovery import BrowserStatus, discover


class _Stub(BrowserProvider):
    def __init__(
        self,
        browser_id: str,
        supported: bool = True,
        profiles: list[BrowserProfile] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.browser_id = browser_id
        self.browser_name = browser_id.title()
        self._supported = supported
        self._profiles = profiles or []
        self._error = error

    def is_supported_platform(self) -> bool:
        return self._supported

    def detect_profiles(self) -> list[BrowserProfile]:
        if self._error is not None:
            raise self._error
        return self._profiles

    def load_bookmarks(self, profile: BrowserProfile) -> BookmarkFolder:
        return BookmarkFolder(name="root")


def _profile() -> BrowserProfile:
    return BrowserProfile("stub", "Stub", "p", "Default", "path")


def test_reports_available_browsers() -> None:
    result = discover([_Stub("chrome", profiles=[_profile()])])[0]
    assert result.status is BrowserStatus.AVAILABLE
    assert result.is_usable


def test_reports_installed_browser_with_no_data() -> None:
    result = discover([_Stub("edge")])[0]
    assert result.status is BrowserStatus.NO_DATA
    assert not result.is_usable
    assert result.message


def test_reports_unsupported_platform() -> None:
    result = discover([_Stub("safari", supported=False)])[0]
    assert result.status is BrowserStatus.UNSUPPORTED_OS


def test_reports_permission_denied() -> None:
    result = discover([_Stub("safari", error=PermissionDeniedError("Grant access"))])[0]
    assert result.status is BrowserStatus.PERMISSION_DENIED
    assert result.message == "Grant access"


def test_browser_error_does_not_stop_discovery() -> None:
    results = discover(
        [
            _Stub("firefox", error=BrowserNotInstalledError("nope")),
            _Stub("chrome", profiles=[_profile()]),
        ]
    )
    assert results[0].status is BrowserStatus.ERROR
    assert results[1].status is BrowserStatus.AVAILABLE


def test_unexpected_provider_failure_is_contained() -> None:
    results = discover(
        [_Stub("broken", error=RuntimeError("boom")), _Stub("chrome", profiles=[_profile()])]
    )
    assert results[0].status is BrowserStatus.ERROR
    assert "See the log" in results[0].message
    assert results[1].is_usable


def test_default_discovery_never_raises() -> None:
    for browser in discover():
        assert isinstance(browser.status, BrowserStatus)
