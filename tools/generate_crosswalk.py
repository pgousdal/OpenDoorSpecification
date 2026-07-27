#!/usr/bin/env python3
"""Generate the M6.1 ODS crosswalk from the canonical M6.0 API census."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CENSUS = ROOT / "catalog" / "census"
DEFAULT_OUTPUT = ROOT / "catalog" / "crosswalk"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    path.write_text(rendered, encoding="utf-8")


def collect(census_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    index = load_json(census_dir / "index.json")
    systems: list[dict[str, Any]] = []
    for summary in index["systems"]:
        record_path = ROOT / summary["path"]
        if census_dir != DEFAULT_CENSUS:
            record_path = census_dir / Path(summary["path"]).name
        record = load_json(record_path)
        systems.append(record)
    systems.sort(key=lambda item: item["id"])
    return index, systems


def operation_ids(systems: list[dict[str, Any]]) -> list[str]:
    return sorted(
        {
            mapping["operation"]
            for system in systems
            for mapping in system.get("mappings", [])
        }
    )


def host_status(system: dict[str, Any], operation: str) -> dict[str, Any]:
    matches = [
        mapping
        for mapping in system.get("mappings", [])
        if mapping["operation"] == operation
    ]
    if not matches:
        return {
            "status": "unassessed",
            "symbols": [],
            "evidence_class": system["evidence_class"],
            "notes": [
                "No reviewed semantic mapping exists in the M6.0 census. "
                "This does not mean the host lacks the capability."
            ],
        }

    mapping = matches[0]
    return {
        "status": mapping["status"],
        "symbols": mapping.get("symbols", []),
        "semantic_review": mapping.get("semantic_review", "unknown"),
        "evidence_class": system["evidence_class"],
        "lossiness": "unknown",
        "notes": [],
    }


def build(census_dir: Path) -> dict[str, Any]:
    census_index, systems = collect(census_dir)
    operations = operation_ids(systems)

    operation_records = []
    for operation in operations:
        hosts = {
            system["id"]: host_status(system, operation)
            for system in systems
        }
        operation_records.append(
            {
                "id": operation,
                "hosts": hosts,
            }
        )

    host_records = []
    for system in systems:
        host_records.append(
            {
                "schema_version": 1,
                "milestone": "M6.1",
                "host": {
                    "id": system["id"],
                    "name": system["name"],
                    "evidence_class": system["evidence_class"],
                    "census_path": f"catalog/census/{system['id']}.json",
                },
                "operations": [
                    {
                        "operation": operation,
                        **host_status(system, operation),
                    }
                    for operation in operations
                ],
                "limitations": list(system.get("limitations", [])),
            }
        )

    return {
        "index": {
            "schema_version": 1,
            "milestone": "M6.1",
            "title": "ODS Crosswalk Specification",
            "source_milestone": census_index["milestone"],
            "source_path": "catalog/census/index.json",
            "host_count": len(systems),
            "operation_count": len(operations),
            "mapped_cell_count": sum(
                1
                for operation in operation_records
                for value in operation["hosts"].values()
                if value["status"] != "unassessed"
            ),
            "hosts": [
                {
                    "id": record["host"]["id"],
                    "name": record["host"]["name"],
                    "path": f"catalog/crosswalk/{record['host']['id']}.json",
                }
                for record in host_records
            ],
            "operations_path": "catalog/crosswalk/operations.json",
        },
        "operations": {
            "schema_version": 1,
            "milestone": "M6.1",
            "operations": operation_records,
        },
        "hosts": host_records,
    }


def generate(census_dir: Path, output_dir: Path, check: bool = False) -> int:
    built = build(census_dir)
    expected: dict[Path, Any] = {
        output_dir / "index.json": built["index"],
        output_dir / "operations.json": built["operations"],
    }
    for host in built["hosts"]:
        expected[output_dir / f"{host['host']['id']}.json"] = host

    if check:
        stale: list[str] = []
        for path, value in expected.items():
            rendered = json.dumps(
                value, indent=2, ensure_ascii=False, sort_keys=False
            ) + "\n"
            if not path.exists() or path.read_text(encoding="utf-8") != rendered:
                stale.append(str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path))
        if stale:
            print("Crosswalk is stale or missing:")
            for path in stale:
                print(f"  {path}")
            return 1
        print(
            f"Crosswalk is current: {built['index']['host_count']} hosts, "
            f"{built['index']['operation_count']} operations, "
            f"{built['index']['mapped_cell_count']} reviewed mappings."
        )
        return 0

    for path, value in expected.items():
        write_json(path, value)
    print(
        f"Generated {built['index']['host_count']} host crosswalks and "
        f"{built['index']['operation_count']} operations in {output_dir}."
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic ODS crosswalk data from the API census."
    )
    parser.add_argument("--census-dir", type=Path, default=DEFAULT_CENSUS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when committed crosswalk files are missing or stale.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return generate(args.census_dir.resolve(), args.output_dir.resolve(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
