#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"
sys.path.insert(0, str(TOOLS_SRC))

from ods_tools.crosswalk_work_queue import build_crosswalk_work_queue


def render(root: Path) -> str:
    return json.dumps(
        build_crosswalk_work_queue(root),
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def generate(root: Path, output: Path, check: bool = False) -> int:
    content = render(root)
    if check:
        if not output.exists():
            print(f"missing generated crosswalk work queue: {output}")
            return 1
        if output.read_text(encoding="utf-8") != content:
            print(f"stale generated crosswalk work queue: {output}")
            return 1
        report = build_crosswalk_work_queue(root)
        print(
            "Crosswalk work queue is current: "
            f"{report['summary']['total']} unassessed cells."
        )
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    report = build_crosswalk_work_queue(root)
    print(
        f"Wrote {output}: {report['summary']['total']} unassessed cells."
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the deterministic M6.2 crosswalk research queue."
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "catalog" / "crosswalk" / "work-queue.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return generate(ROOT, args.output.resolve(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
