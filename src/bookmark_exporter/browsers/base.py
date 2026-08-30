"""Provider interface and the error types every provider raises."""

from __future__ import annotations

from abc import ABC, abstractmethod

from bookmark_exporter.models import BookmarkFolder, BrowserProfile


class BrowserError(Exception):
    """Base class for every recoverable browser access failure.

    Carries a user-facing message. Technical detail belongs in the log, not here.
    """


class BrowserNotInstalledError(BrowserError):
    """No profile data for this browser exists on this machine."""


class ProfileNotFoundError(BrowserError):
    """The requested profile no longer exists."""


class BookmarkDataUnavailableError(BrowserError):
    """Bookmark data exists but could not be read."""


class CorruptBookmarkDataError(BrowserError):
    """Bookmark data was read but is not in a shape we can parse."""


class PermissionDeniedError(BrowserError):
    """The operating system refused access to the bookmark data."""


class UnsupportedPlatformError(BrowserError):
    """This browser is not supported on the current operating system."""


class BrowserProvider(ABC):
    """Reads bookmarks for one browser family.

    Implementations are strictly read-only. Nothing in this package may open a
    browser data file for writing.
    """

    browser_id: str
    browser_name: str

    @abstractmethod
    def is_supported_platform(self) -> bool:
        """Whether this browser can exist on the current operating system."""

    @abstractmethod
    def detect_profiles(self) -> list[BrowserProfile]:
        """Return every profile with readable bookmark data.

        Returns an empty list when the browser is not installed. Raises only when
        the browser appears installed but its data cannot be enumerated.
        """

    @abstractmethod
    def load_bookmarks(self, profile: BrowserProfile) -> BookmarkFolder:
        """Return the full bookmark tree for a profile as a synthetic root."""
