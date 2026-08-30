"""Microsoft Edge. Path and profile discovery only; parsing is shared."""

from __future__ import annotations

from pathlib import Path

from bookmark_exporter.browsers.chromium import ChromiumProvider
from bookmark_exporter.utils.paths import (
    is_linux,
    is_macos,
    is_windows,
    local_app_data,
    mac_application_support,
)


class EdgeProvider(ChromiumProvider):
    browser_id = "edge"
    browser_name = "Microsoft Edge"

    def user_data_dirs(self) -> list[Path]:
        if is_windows():
            return [local_app_data() / "Microsoft" / "Edge" / "User Data"]
        if is_macos():
            return [mac_application_support() / "Microsoft Edge"]
        if is_linux():
            return [Path.home() / ".config" / "microsoft-edge"]
        return []
