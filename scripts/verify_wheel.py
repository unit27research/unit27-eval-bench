"""Verify wheel contents for Unit27 Eval Bench."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path


REQUIRED = {
    "eval_bench/__init__.py",
    "eval_bench/cli.py",
    "eval_bench/core.py",
}
ENTRY_POINT = "eval-bench = eval_bench.cli:main"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_wheel.py PATH_TO_WHEEL", file=sys.stderr)
        return 2

    wheel = Path(sys.argv[1])
    if not wheel.exists():
        print(f"wheel not found: {wheel}", file=sys.stderr)
        return 2

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        entry_points = [
            archive.read(name).decode("utf-8")
            for name in names
            if name.endswith(".dist-info/entry_points.txt")
        ]

    missing = sorted(required for required in REQUIRED if not any(name.endswith(required) for name in names))
    if missing:
        print("missing wheel contents:")
        for item in missing:
            print(f"- {item}")
        return 1
    if not any(ENTRY_POINT in entry_point for entry_point in entry_points):
        print(f"missing console entry point: {ENTRY_POINT}")
        return 1

    print("wheel contents verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
