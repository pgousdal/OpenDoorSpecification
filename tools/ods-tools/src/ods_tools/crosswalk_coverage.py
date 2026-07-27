from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .crosswalk import load_crosswalk


def _summary(cells: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"verified": 0, "partial": 0, "unassessed": 0}
    for cell in cells:
        counts[cell["status"]] += 1
    counts["reviewed"] = counts["verified"] + counts["partial"]
    counts["total"] = len(cells)
    return counts


def build_crosswalk_coverage(root: Path) -> dict[str, Any]:
    data = load_crosswalk(root)
    hosts = data["hosts"]
    operations = data["operations"]["operations"]

    host_rows = []
    for host_id in sorted(hosts):
        record = hosts[host_id]
        host_rows.append({
            "id": host_id,
            "name": record["host"]["name"],
            "evidence_class": record["host"]["evidence_class"],
            "summary": _summary(record["operations"]),
            "unassessed_operations": [
                item["operation"] for item in record["operations"]
                if item["status"] == "unassessed"
            ],
        })

    operation_rows = []
    for operation in operations:
        cells = [
            {"host": host_id, **cell}
            for host_id, cell in sorted(operation["hosts"].items())
        ]
        operation_rows.append({
            "id": operation["id"],
            "summary": _summary(cells),
            "unassessed_hosts": [
                item["host"] for item in cells
                if item["status"] == "unassessed"
            ],
        })

    all_cells = [
        cell for host in hosts.values() for cell in host["operations"]
    ]
    return {
        "schema_version": 1,
        "milestone": "M6.1",
        "kind": "evidence-coverage",
        "semantics": {
            "unassessed": (
                "No reviewed mapping is recorded; this does not mean unsupported."
            ),
            "partial": (
                "A reviewed mapping exists, but coverage is incomplete."
            ),
        },
        "summary": _summary(all_cells),
        "hosts": host_rows,
        "operations": operation_rows,
    }


def write_crosswalk_coverage(
    root: Path, output: Path | None = None
) -> dict[str, Any]:
    report = build_crosswalk_coverage(root)
    path = output or root / "catalog" / "crosswalk" / "coverage.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def format_crosswalk_coverage(
    report: dict[str, Any],
    target: str | None = None,
    gaps_only: bool = False,
) -> str:
    if target is None:
        summary = report["summary"]
        lines = [
            "M6.1 crosswalk evidence coverage",
            (
                f"reviewed: {summary['reviewed']}/{summary['total']} "
                f"(verified {summary['verified']}, partial {summary['partial']})"
            ),
            f"unassessed: {summary['unassessed']}",
            "hosts:",
        ]
        for row in report["hosts"]:
            s = row["summary"]
            if gaps_only and not s["unassessed"]:
                continue
            lines.append(
                f"  {row['id']:<12} reviewed={s['reviewed']:<2} "
                f"verified={s['verified']:<2} partial={s['partial']:<2} "
                f"unassessed={s['unassessed']}"
            )
        return "\n".join(lines)

    host = next((x for x in report["hosts"] if x["id"] == target), None)
    if host is not None:
        s = host["summary"]
        lines = [
            f"{host['id']} — {host['name']}",
            (
                f"reviewed: {s['reviewed']}/{s['total']} "
                f"(verified {s['verified']}, partial {s['partial']})"
            ),
            f"unassessed: {s['unassessed']}",
        ]
        lines.extend(f"  {op}" for op in host["unassessed_operations"])
        return "\n".join(lines)

    operation = next(
        (x for x in report["operations"] if x["id"] == target), None
    )
    if operation is not None:
        s = operation["summary"]
        lines = [
            operation["id"],
            (
                f"reviewed: {s['reviewed']}/{s['total']} "
                f"(verified {s['verified']}, partial {s['partial']})"
            ),
            f"unassessed: {s['unassessed']}",
        ]
        lines.extend(f"  {host}" for host in operation["unassessed_hosts"])
        return "\n".join(lines)

    raise KeyError(target)
