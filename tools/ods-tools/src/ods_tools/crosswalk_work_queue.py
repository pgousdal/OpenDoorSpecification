from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .crosswalk import load_crosswalk


PRIORITIES = ("high", "medium", "low")
PRIORITY_RANK = {priority: rank for rank, priority in enumerate(PRIORITIES)}
DOCUMENTED_EVIDENCE_CLASSES = {"documented-sdk", "documented-protocol"}
FOUNDATIONAL_OPERATIONS = {
    "lifecycle.disconnect",
    "lifecycle.exit",
    "session.identity",
    "terminal.read_key",
    "terminal.read_line",
    "terminal.write",
}


def _load_census(root: Path, host_id: str) -> dict[str, Any]:
    path = root / "catalog" / "census" / f"{host_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _priority(
    host: dict[str, Any],
    operation_id: str,
    reviewed_host_count: int,
    census: dict[str, Any],
) -> tuple[str, list[str]]:
    score = 0
    reasons: list[str] = []
    evidence_class = host["host"].get("evidence_class")

    if evidence_class in DOCUMENTED_EVIDENCE_CLASSES:
        score += 3
        reasons.append("host has documented SDK or protocol evidence")

    if reviewed_host_count >= 3:
        score += 3
        reasons.append("operation has reviewed mappings in at least three other hosts")
    elif reviewed_host_count:
        score += 1
        reasons.append("operation has a reviewed mapping in another host")

    family = operation_id.split(".", 1)[0]
    if any(
        row["status"] != "unassessed"
        and row["operation"].split(".", 1)[0] == family
        for row in host["operations"]
    ):
        score += 2
        reasons.append("host has a related reviewed operation in the same family")

    if operation_id in FOUNDATIONAL_OPERATIONS:
        score += 2
        reasons.append("operation is foundational for terminal, session, or lifecycle behavior")

    if census.get("entry_count", 0) or census.get("archives"):
        score += 1
        reasons.append("host census or archive evidence is already cataloged")

    if score >= 5:
        return "high", reasons
    if score >= 2:
        return "medium", reasons
    if not reasons:
        reasons.append("no higher-priority research signal is currently recorded")
    return "low", reasons


def _summary(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {priority: 0 for priority in PRIORITIES}
    for item in items:
        counts[item["priority"]] += 1
    return {"total": len(items), **counts}


def build_crosswalk_work_queue(root: Path) -> dict[str, Any]:
    data = load_crosswalk(root)
    reviewed_counts = {
        operation["id"]: sum(
            cell["status"] != "unassessed"
            for cell in operation["hosts"].values()
        )
        for operation in data["operations"]["operations"]
    }
    items: list[dict[str, Any]] = []
    for host_id in sorted(data["hosts"]):
        host = data["hosts"][host_id]
        census = _load_census(root, host_id)
        for cell in host["operations"]:
            if cell["status"] != "unassessed":
                continue
            operation_id = cell["operation"]
            priority, reasons = _priority(
                host,
                operation_id,
                reviewed_counts[operation_id],
                census,
            )
            items.append(
                {
                    "id": f"{host_id}:{operation_id}",
                    "host": host_id,
                    "host_name": host["host"].get("name"),
                    "host_evidence_class": host["host"].get("evidence_class"),
                    "operation": operation_id,
                    "status": "unassessed",
                    "priority": priority,
                    "reasons": reasons,
                }
            )

    items.sort(key=lambda item: (PRIORITY_RANK[item["priority"]], item["id"]))
    return {
        "schema_version": 1,
        "milestone": "M6.2",
        "kind": "crosswalk-evidence-work-queue",
        "source_path": "catalog/crosswalk/index.json",
        "semantics": {
            "priority": "Research-order recommendation; not a support claim or support-likelihood estimate.",
            "unassessed": "No reviewed mapping is recorded; this does not mean unsupported.",
        },
        "priority_order": list(PRIORITIES),
        "summary": _summary(items),
        "items": items,
    }


def select_crosswalk_work_queue(
    root: Path,
    target: str | None = None,
    priority: str | None = None,
) -> dict[str, Any]:
    if priority is not None and priority not in PRIORITIES:
        raise ValueError(
            f"invalid work-queue priority: {priority}; "
            f"choose from {', '.join(PRIORITIES)}"
        )
    data = load_crosswalk(root)
    host_ids = set(data["hosts"])
    operation_ids = {
        operation["id"] for operation in data["operations"]["operations"]
    }
    target_kind: str | None = None
    target_id: str | None = None
    if target is not None:
        if target.startswith("host:"):
            target_kind, target_id = "host", target[5:]
        elif target.startswith("operation:"):
            target_kind, target_id = "operation", target[10:]
        else:
            in_hosts = target in host_ids
            in_operations = target in operation_ids
            if in_hosts and in_operations:
                raise ValueError(
                    f"ambiguous crosswalk target: {target}; "
                    f"use host:{target} or operation:{target}"
                )
            if in_hosts:
                target_kind, target_id = "host", target
            elif in_operations:
                target_kind, target_id = "operation", target
            else:
                raise KeyError(target)
        known = host_ids if target_kind == "host" else operation_ids
        if target_id not in known:
            raise KeyError(target)

    report = build_crosswalk_work_queue(root)
    items = report["items"]
    if target_kind == "host":
        items = [item for item in items if item["host"] == target_id]
    elif target_kind == "operation":
        items = [item for item in items if item["operation"] == target_id]
    if priority is not None:
        items = [item for item in items if item["priority"] == priority]

    selected = dict(report)
    selected["summary"] = _summary(items)
    selected["items"] = items
    if target is not None or priority is not None:
        selected["filters"] = {
            **({"target": target} if target is not None else {}),
            **({"priority": priority} if priority is not None else {}),
        }
    return selected


def format_crosswalk_work_queue(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        (
            f"M6.2 crosswalk evidence work queue: {summary['total']} items "
            f"(high {summary['high']}, medium {summary['medium']}, low {summary['low']})"
        )
    ]
    for item in report["items"]:
        lines.append(
            f"{item['priority']:<6} {item['id']:<40} {item['reasons'][0]}"
        )
    if not report["items"]:
        lines.append("no matching unassessed cells")
    return "\n".join(lines)


def validate_crosswalk_work_queue(root: Path) -> int:
    expected = build_crosswalk_work_queue(root)
    path = root / "catalog" / "crosswalk" / "work-queue.json"
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored == expected, "stale crosswalk work queue"
    ids = [item["id"] for item in stored["items"]]
    assert len(ids) == len(set(ids)), "duplicate crosswalk work-queue item ID"
    assert all(item["status"] == "unassessed" for item in stored["items"])
    assert all(item["priority"] in PRIORITIES for item in stored["items"])
    assert all(item["reasons"] for item in stored["items"])
    return len(stored["items"])
