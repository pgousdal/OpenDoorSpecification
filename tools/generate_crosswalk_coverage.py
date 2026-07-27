#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"
sys.path.insert(0, str(TOOLS_SRC))

from ods_tools.crosswalk_coverage import build_crosswalk_coverage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "catalog" / "crosswalk" / "coverage.json",
    )
    args = parser.parse_args()
    report = build_crosswalk_coverage(ROOT)
    content = json.dumps(report, indent=2) + "\n"

    if args.check:
        if not args.output.exists():
            raise SystemExit(f"missing generated coverage report: {args.output}")
        if args.output.read_text(encoding="utf-8") != content:
            raise SystemExit(f"stale generated coverage report: {args.output}")
        s = report["summary"]
        print(
            "Crosswalk coverage is current: "
            f"{s['reviewed']}/{s['total']} reviewed mappings."
        )
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    s = report["summary"]
    print(f"Wrote {args.output}: {s['reviewed']}/{s['total']} reviewed mappings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
