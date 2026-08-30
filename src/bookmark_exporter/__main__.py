"""Entry point for ``python -m bookmark_exporter``."""

from __future__ import annotations

import sys

from bookmark_exporter.app import run


def main() -> int:
    return run()


if __name__ == "__main__":
    sys.exit(main())
