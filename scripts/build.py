"""PyInstaller build wrapper.

Packaging logic lives here so nothing in ``src/`` has to know it is frozen.

    python scripts/build.py
"""

from __future__ import annotations

import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRY = ROOT / "src" / "bookmark_exporter" / "__main__.py"
APP_NAME = "bookmark-xport"


def main() -> int:
    if find_spec("PyInstaller") is None:
        sys.stderr.write("PyInstaller is not installed. Run: pip install -e .[dev]\n")
        return 1

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        APP_NAME,
        "--paths",
        str(ROOT / "src"),
        "--distpath",
        str(ROOT / "dist"),
        "--workpath",
        str(ROOT / "build"),
        "--specpath",
        str(ROOT / "build"),
        str(ENTRY),
    ]
    print(" ".join(command))
    return subprocess.call(command, cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())
