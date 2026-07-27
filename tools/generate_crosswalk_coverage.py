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
from ods_tools.crosswalk_evidence import (
    EvidenceValidationError,
    validate_crosswalk_evidence,
)


def generate(root: Path, output: Path, check: bool = False) -> int:
    try:
        validate_crosswalk_evidence(root)
    except EvidenceValidationError as exc:
        print(f"Crosswalk evidence validation failed: {exc}")
        return 1
    report = build_crosswalk_coverage(root)
    content = json.dumps(report, indent=2) + "\n"

    if check:
        if not output.exists():
            print(f"missing generated coverage report: {output}")
            return 1
        if output.read_text(encoding="utf-8") != content:
            print(f"stale generated coverage report: {output}")
            return 1
        s = report["summary"]
        print(
            "Crosswalk coverage is current: "
            f"{s['reviewed']}/{s['total']} reviewed mappings."
        )
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    s = report["summary"]
    print(f"Wrote {output}: {s['reviewed']}/{s['total']} reviewed mappings.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "catalog" / "crosswalk" / "coverage.json",
    )
    args = parser.parse_args()
    return generate(ROOT, args.output.resolve(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
