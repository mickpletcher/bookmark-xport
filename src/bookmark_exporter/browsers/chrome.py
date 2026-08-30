"""Google Chrome. Path and profile discovery only; parsing is shared."""

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


class ChromeProvider(ChromiumProvider):
    browser_id = "chrome"
    browser_name = "Google Chrome"

    def user_data_dirs(self) -> list[Path]:
        if is_windows():
            return [local_app_data() / "Google" / "Chrome" / "User Data"]
        if is_macos():
            return [mac_application_support() / "Google" / "Chrome"]
        if is_linux():
            return [
                Path.home() / ".config" / "google-chrome",
                Path.home() / ".config" / "chromium",
            ]
        return []
