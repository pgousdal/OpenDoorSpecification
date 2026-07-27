from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .crosswalk_evidence import validate_crosswalk_evidence
from .crosswalk_triage import build_crosswalk_triage
from .crosswalk_work_queue import build_crosswalk_work_queue


BACKLOG_CLASSES = (
    "completion-blocker",
    "deferred-research",
    "archival-source-discovery",
)

GROUP_POLICY = {
    "documented-but-not-reviewed": {
        "backlog_class": "completion-blocker",
        "expected_value": "high",
        "recommended_milestone": "M6.2",
        "summary": (
            "Review already cataloged primary evidence before M6.2 can close."
        ),
    },
    "insufficient-semantics": {
        "backlog_class": "deferred-research",
        "expected_value": "medium",
        "recommended_milestone": "post-M6.2 evidence expansion",
        "summary": (
            "Resolve semantic gaps without treating nearby symbols as mappings."
        ),
    },
    "missing-primary-source": {
        "backlog_class": "archival-source-discovery",
        "expected_value": "high",
        "recommended_milestone": "archive discovery",
        "summary": (
            "Locate and catalog a primary SDK, protocol, or programmer reference."
        ),
    },
    "insufficient-sdk": {
        "backlog_class": "archival-source-discovery",
        "expected_value": "medium",
        "recommended_milestone": "archive discovery",
        "summary": (
            "Find a broader host-specific source because the cataloged SDK omits "
            "the operation."
        ),
    },
    "ambiguous-operation": {
        "backlog_class": "deferred-research",
        "expected_value": "medium",
        "recommended_milestone": "post-M6.2 evidence expansion",
        "summary": (
            "Distinguish the canonical operation from similar documented behavior."
        ),
    },
    "needs-additional-research": {
        "backlog_class": "deferred-research",
        "expected_value": "medium",
        "recommended_milestone": "post-M6.2 evidence expansion",
        "summary": (
            "Perform focused research in cataloged primary material."
        ),
    },
}


def _distribution(items: list[dict[str, Any]], field: str) -> dict[str, int]:
    values = sorted({item[field] for item in items})
    return {value: sum(item[field] == value for item in items) for value in values}


def _build_backlog(triage: dict[str, Any]) -> dict[str, Any]:
    groups = []
    for category in triage["vocabularies"]["categories"]:
        items = [item for item in triage["items"] if item["category"] == category]
        if not items:
            continue
        policy = GROUP_POLICY[category]
        groups.append(
            {
                "id": category,
                **policy,
                "affected_hosts": sorted({item["host"] for item in items}),
                "affected_operations": sorted(
                    {item["operation"] for item in items}
                ),
                "effort_distribution": _distribution(items, "effort"),
                "item_count": len(items),
                "items": [
                    {
                        "id": item["id"],
                        "host": item["host"],
                        "operation": item["operation"],
                        "reason": item["category"],
                        "effort": item["effort"],
                        "confidence": item["confidence"],
                    }
                    for item in items
                ],
            }
        )
    class_distribution = {
        value: sum(
            group["item_count"]
            for group in groups
            if group["backlog_class"] == value
        )
        for value in BACKLOG_CLASSES
    }
    return {
        "summary": {
            "total": sum(group["item_count"] for group in groups),
            "groups": len(groups),
            "classes": class_distribution,
        },
        "groups": groups,
    }


def build_m62_completion(root: Path) -> dict[str, Any]:
    queue = build_crosswalk_work_queue(root)
    triage = build_crosswalk_triage(root)
    backlog = _build_backlog(triage)
    queue_ids = [item["id"] for item in queue["items"]]
    triage_ids = [item["id"] for item in triage["items"]]
    backlog_ids = [
        item["id"] for group in backlog["groups"] for item in group["items"]
    ]
    reviewed = validate_crosswalk_evidence(root)
    blockers = [
        item
        for item in triage["items"]
        if item["category"] == "documented-but-not-reviewed"
        or item["confidence"] == "high"
    ]
    criteria = [
        {
            "id": "documented-high-confidence-work-complete",
            "satisfied": not blockers,
            "detail": (
                f"{len(blockers)} documented or high-confidence items remain."
            ),
        },
        {
            "id": "remaining-work-classified",
            "satisfied": (
                queue_ids == triage_ids
                and sorted(queue_ids) == sorted(backlog_ids)
                and len(backlog_ids) == len(set(backlog_ids))
            ),
            "detail": (
                f"{len(backlog_ids)} backlog items classify "
                f"{len(queue_ids)} queue items."
            ),
        },
        {
            "id": "reviewed-provenance-valid",
            "satisfied": reviewed >= 0,
            "detail": f"{reviewed} reviewed mappings have valid provenance.",
        },
        {
            "id": "queue-triage-consistent",
            "satisfied": queue_ids == triage_ids,
            "detail": (
                f"Queue and triage each contain {len(queue_ids)} ordered items."
            ),
        },
        {
            "id": "no-orphaned-backlog-items",
            "satisfied": (
                sorted(backlog_ids) == sorted(queue_ids)
                and len(backlog_ids) == len(set(backlog_ids))
            ),
            "detail": "Backlog IDs are unique and resolve to unassessed cells.",
        },
    ]
    complete = all(item["satisfied"] for item in criteria)
    return {
        "schema_version": 1,
        "milestone": "M6.2",
        "kind": "crosswalk-milestone-completion",
        "source_paths": [
            "catalog/crosswalk/work-queue.json",
            "catalog/crosswalk/triage.json",
        ],
        "complete": complete,
        "completion_semantics": (
            "M6.2 is complete when cataloged documented or high-confidence work "
            "is reviewed and every remaining unassessed cell is consistently "
            "classified. Completion is not a claim that every host supports "
            "every canonical operation."
        ),
        "validation_requirements": [
            "reviewed mapping provenance passes validation",
            "all generators produce byte-identical output for unchanged inputs",
            "generated crosswalk, coverage, queue, triage, and completion data are current",
            "queue, triage, and backlog contain the same unassessed mapping IDs",
            "backlog IDs are unique and no reviewed mapping appears in the backlog",
            "normal and strict repository validation pass",
        ],
        "criteria": criteria,
        "backlog": backlog,
    }


def select_m62_backlog(root: Path) -> dict[str, Any]:
    report = build_m62_completion(root)
    return {
        "schema_version": report["schema_version"],
        "milestone": report["milestone"],
        "kind": "crosswalk-research-backlog",
        **report["backlog"],
    }


def format_m62_completion(report: dict[str, Any]) -> str:
    state = "complete" if report["complete"] else "in progress"
    lines = [f"M6.2 crosswalk evidence expansion: {state}", "criteria:"]
    for criterion in report["criteria"]:
        marker = "PASS" if criterion["satisfied"] else "BLOCK"
        lines.append(f"  {marker:<5} {criterion['id']} — {criterion['detail']}")
    summary = report["backlog"]["summary"]
    lines.append(
        f"backlog: {summary['total']} items in {summary['groups']} reason groups"
    )
    return "\n".join(lines)


def format_m62_backlog(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        (
            f"M6.2 research backlog: {summary['total']} items "
            f"in {summary['groups']} reason groups"
        )
    ]
    for group in report["groups"]:
        hosts = ", ".join(group["affected_hosts"])
        lines.append(
            f"{group['backlog_class']:<27} {group['id']:<28} "
            f"{group['item_count']:>2}  hosts={hosts}"
        )
    return "\n".join(lines)


def validate_m62_completion(root: Path) -> int:
    expected = build_m62_completion(root)
    path = root / "catalog" / "crosswalk" / "m62-completion.json"
    assert path.exists(), "missing M6.2 completion report"
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored == expected, "stale M6.2 completion report"
    queue_ids = {
        item["id"] for item in build_crosswalk_work_queue(root)["items"]
    }
    triage_ids = {item["id"] for item in build_crosswalk_triage(root)["items"]}
    backlog_ids = [
        item["id"]
        for group in stored["backlog"]["groups"]
        for item in group["items"]
    ]
    assert len(backlog_ids) == len(set(backlog_ids)), "duplicate backlog item ID"
    assert set(backlog_ids) == queue_ids == triage_ids, (
        "completion backlog must exactly cover queue and triage"
    )
    assert all(item["satisfied"] for item in stored["criteria"]) == stored[
        "complete"
    ], "completion state does not match criteria"
    return len(backlog_ids)
