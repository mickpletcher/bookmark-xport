"""Browser discovery.

Reports, for every supported browser, whether its data is available, absent,
unreadable, or impossible on this operating system. A browser that fails here
must never prevent the others from working.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

from bookmark_exporter.browsers.base import (
    BrowserError,
    BrowserProvider,
    PermissionDeniedError,
)
from bookmark_exporter.browsers.chrome import ChromeProvider
from bookmark_exporter.browsers.edge import EdgeProvider
from bookmark_exporter.browsers.firefox import FirefoxProvider
from bookmark_exporter.browsers.safari import SafariProvider
from bookmark_exporter.models import BrowserProfile

log = logging.getLogger(__name__)


class BrowserStatus(Enum):
    AVAILABLE = "available"
    NO_DATA = "no_data"
    UNSUPPORTED_OS = "unsupported_os"
    PERMISSION_DENIED = "permission_denied"
    ERROR = "error"


@dataclass(slots=True)
class DiscoveredBrowser:
    provider: BrowserProvider
    status: BrowserStatus
    profiles: list[BrowserProfile] = field(default_factory=list)
    message: str = ""

    @property
    def browser_id(self) -> str:
        return self.provider.browser_id

    @property
    def browser_name(self) -> str:
        return self.provider.browser_name

    @property
    def is_usable(self) -> bool:
        return self.status is BrowserStatus.AVAILABLE and bool(self.profiles)


def default_providers() -> list[BrowserProvider]:
    return [ChromeProvider(), EdgeProvider(), FirefoxProvider(), SafariProvider()]


def discover(providers: list[BrowserProvider] | None = None) -> list[DiscoveredBrowser]:
    """Inspect every provider and report what can actually be read."""
    results: list[DiscoveredBrowser] = []

    for provider in providers if providers is not None else default_providers():
        if not provider.is_supported_platform():
            results.append(
                DiscoveredBrowser(
                    provider=provider,
                    status=BrowserStatus.UNSUPPORTED_OS,
                    message=f"{provider.browser_name} is not supported on this operating system.",
                )
            )
            continue

        try:
            profiles = provider.detect_profiles()
        except PermissionDeniedError as exc:
            results.append(
                DiscoveredBrowser(
                    provider=provider,
                    status=BrowserStatus.PERMISSION_DENIED,
                    message=str(exc),
                )
            )
            continue
        except BrowserError as exc:
            results.append(
                DiscoveredBrowser(provider=provider, status=BrowserStatus.ERROR, message=str(exc))
            )
            continue
        except Exception:  # A provider defect must not take down discovery.
            log.exception("Unexpected failure while detecting %s profiles", provider.browser_id)
            results.append(
                DiscoveredBrowser(
                    provider=provider,
                    status=BrowserStatus.ERROR,
                    message=f"{provider.browser_name} profiles could not be inspected. See the log.",
                )
            )
            continue

        if profiles:
            results.append(
                DiscoveredBrowser(
                    provider=provider, status=BrowserStatus.AVAILABLE, profiles=profiles
                )
            )
        else:
            results.append(
                DiscoveredBrowser(
                    provider=provider,
                    status=BrowserStatus.NO_DATA,
                    message=f"No {provider.browser_name} bookmark data was found on this machine.",
                )
            )

    return results
