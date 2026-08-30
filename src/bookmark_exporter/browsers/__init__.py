"""Browser providers. Browser-specific logic lives here and nowhere else."""

from bookmark_exporter.browsers.base import (
    BookmarkDataUnavailableError,
    BrowserError,
    BrowserNotInstalledError,
    BrowserProvider,
    CorruptBookmarkDataError,
    PermissionDeniedError,
    ProfileNotFoundError,
    UnsupportedPlatformError,
)

__all__ = [
    "BookmarkDataUnavailableError",
    "BrowserError",
    "BrowserNotInstalledError",
    "BrowserProvider",
    "CorruptBookmarkDataError",
    "PermissionDeniedError",
    "ProfileNotFoundError",
    "UnsupportedPlatformError",
]
