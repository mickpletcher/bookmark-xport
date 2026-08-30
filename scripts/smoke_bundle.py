from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _candidates() -> list[Path]:
    if sys.platform.startswith("win"):
        return [ROOT / "dist" / "bookmark-xport" / "bookmark-xport.exe"]
    if sys.platform == "darwin":
        return [
            ROOT / "dist" / "bookmark-xport.app" / "Contents" / "MacOS" / "bookmark-xport",
            ROOT / "dist" / "bookmark-xport" / "bookmark-xport",
        ]
    return [ROOT / "dist" / "bookmark-xport" / "bookmark-xport"]


def main() -> int:
    executable = next((path for path in _candidates() if path.is_file()), None)
    if executable is None:
        sys.stderr.write("The packaged executable was not found.\n")
        return 1

    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    process = subprocess.Popen([str(executable)], env=environment)
    try:
        exit_code = process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        print(f"Bundle smoke test passed: {executable.name} remained running.")
        return 0

    sys.stderr.write(f"The packaged application exited early with code {exit_code}.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
