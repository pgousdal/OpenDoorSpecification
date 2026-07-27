#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"
sys.path.insert(0, str(TOOLS_SRC))

from ods_tools.crosswalk_triage import build_crosswalk_triage


def render(root: Path) -> str:
    return json.dumps(
        build_crosswalk_triage(root),
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def generate(root: Path, output: Path, check: bool = False) -> int:
    try:
        content = render(root)
    except ValueError as exc:
        print(f"Crosswalk triage generation failed: {exc}")
        return 1
    if check:
        if not output.exists():
            print(f"missing generated crosswalk evidence triage: {output}")
            return 1
        if output.read_text(encoding="utf-8") != content:
            print(f"stale generated crosswalk evidence triage: {output}")
            return 1
        report = build_crosswalk_triage(root)
        print(
            "Crosswalk evidence triage is current: "
            f"{report['summary']['total']} unassessed cells."
        )
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    report = build_crosswalk_triage(root)
    print(f"Wrote {output}: {report['summary']['total']} triage items.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic M6.2 remaining-evidence triage."
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "catalog" / "crosswalk" / "triage.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return generate(ROOT, args.output.resolve(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
