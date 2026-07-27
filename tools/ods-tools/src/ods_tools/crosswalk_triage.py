from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .crosswalk import load_crosswalk
from .crosswalk_work_queue import build_crosswalk_work_queue


CATEGORIES = (
    "documented-but-not-reviewed",
    "insufficient-semantics",
    "missing-primary-source",
    "insufficient-sdk",
    "ambiguous-operation",
    "needs-additional-research",
)
EFFORTS = ("trivial", "small", "moderate", "extensive")
CONFIDENCES = ("high", "medium", "low")
DOCUMENTATION_QUALITIES = ("comprehensive", "targeted", "limited", "observational")
RECOMMENDED_PRIORITIES = ("high", "medium", "low")


ITEM_TRIAGE: dict[str, tuple[str, str, str]] = {
    "abbs:bbs.command": ("needs-additional-research", "moderate", "medium"),
    "abbs:lifecycle.exit": ("needs-additional-research", "moderate", "medium"),
    "aedoor:status.set": ("ambiguous-operation", "moderate", "low"),
    "ambos:bbs.command": ("insufficient-semantics", "moderate", "medium"),
    "ambos:session.time_left": ("insufficient-sdk", "extensive", "low"),
    "ambos:status.set": ("insufficient-sdk", "extensive", "low"),
    "door-io:bbs.command": ("insufficient-sdk", "extensive", "low"),
    "door-io:session.identity": ("insufficient-sdk", "extensive", "low"),
    "door-io:session.time_left": ("insufficient-sdk", "extensive", "low"),
    "door-io:status.set": ("insufficient-sdk", "extensive", "low"),
    "fame:status.set": ("ambiguous-operation", "moderate", "medium"),
    "paragon:session.time_left": ("insufficient-semantics", "moderate", "medium"),
    "paragon:status.set": ("insufficient-semantics", "moderate", "medium"),
    "ucdoor:status.set": ("ambiguous-operation", "moderate", "low"),
    "wwbbs:bbs.command": ("missing-primary-source", "extensive", "low"),
    "wwbbs:lifecycle.disconnect": ("missing-primary-source", "extensive", "low"),
    "wwbbs:lifecycle.exit": ("missing-primary-source", "extensive", "low"),
    "wwbbs:session.identity": ("missing-primary-source", "extensive", "low"),
    "wwbbs:session.time_left": ("missing-primary-source", "extensive", "low"),
    "wwbbs:status.set": ("missing-primary-source", "extensive", "low"),
    "wwbbs:terminal.read_key": ("missing-primary-source", "extensive", "low"),
    "wwbbs:terminal.read_line": ("missing-primary-source", "extensive", "low"),
    "wwbbs:terminal.write": ("missing-primary-source", "extensive", "low"),
    "zeus:bbs.command": ("missing-primary-source", "extensive", "low"),
    "zeus:lifecycle.disconnect": ("missing-primary-source", "extensive", "low"),
    "zeus:lifecycle.exit": ("missing-primary-source", "extensive", "low"),
    "zeus:session.identity": ("missing-primary-source", "extensive", "low"),
    "zeus:session.time_left": ("missing-primary-source", "extensive", "low"),
    "zeus:status.set": ("missing-primary-source", "extensive", "low"),
    "zeus:terminal.read_key": ("missing-primary-source", "extensive", "low"),
    "zeus:terminal.read_line": ("missing-primary-source", "extensive", "low"),
    "zeus:terminal.write": ("missing-primary-source", "extensive", "low"),
}


CATEGORY_RATIONALES = {
    "documented-but-not-reviewed": (
        "Cataloged primary documentation names the required behavior, but the "
        "mapping still needs a focused semantic review."
    ),
    "insufficient-semantics": (
        "Cataloged material exposes nearby commands or fields without defining "
        "enough behavior for the canonical operation."
    ),
    "missing-primary-source": (
        "Observed door code is cataloged, but no primary SDK or protocol contract "
        "is available for this host."
    ),
    "insufficient-sdk": (
        "The cataloged SDK does not expose an interface for this operation."
    ),
    "ambiguous-operation": (
        "Status-related evidence exists, but it does not clearly set the canonical "
        "host-visible activity description."
    ),
    "needs-additional-research": (
        "Primary material is available, but the relevant host interaction has not "
        "yet been isolated and interpreted."
    ),
}


HOST_RESEARCH = {
    "abbs": {
        "documentation_quality": "comprehensive",
        "recommended_priority": "medium",
        "next_evidence_opportunity": (
            "Review the ARexx guide and door lifecycle documentation for host "
            "command dispatch and normal script completion."
        ),
    },
    "aedoor": {
        "documentation_quality": "comprehensive",
        "recommended_priority": "low",
        "next_evidence_opportunity": (
            "Locate an AmiExpress node-action or status-text setter beyond the "
            "public AEDoor calls already reviewed."
        ),
    },
    "ambos": {
        "documentation_quality": "comprehensive",
        "recommended_priority": "medium",
        "next_evidence_opportunity": (
            "Determine whether bbs_menu can satisfy the canonical host-command "
            "namespace without conflating menu presentation with command dispatch."
        ),
    },
    "door-io": {
        "documentation_quality": "targeted",
        "recommended_priority": "low",
        "next_evidence_opportunity": (
            "Seek host-specific wrapper documentation; the public library itself "
            "contains only terminal I/O and lifecycle cleanup."
        ),
    },
    "fame": {
        "documentation_quality": "comprehensive",
        "recommended_priority": "medium",
        "next_evidence_opportunity": (
            "Check developer-only DoorPort commands for a node action-string "
            "setter distinct from account status."
        ),
    },
    "paragon": {
        "documentation_quality": "limited",
        "recommended_priority": "medium",
        "next_evidence_opportunity": (
            "Find a primary MAXs command table defining remaining-time fields and "
            "host-visible activity mutation."
        ),
    },
    "ucdoor": {
        "documentation_quality": "comprehensive",
        "recommended_priority": "low",
        "next_evidence_opportunity": (
            "Research the underlying MAXs protocol for a node activity-description "
            "setter not exposed by UCDoor."
        ),
    },
    "wwbbs": {
        "documentation_quality": "observational",
        "recommended_priority": "low",
        "next_evidence_opportunity": (
            "Locate and catalog a WWBBS ARexx programmer reference or protocol "
            "definition before reviewing individual operations."
        ),
    },
    "zeus": {
        "documentation_quality": "observational",
        "recommended_priority": "low",
        "next_evidence_opportunity": (
            "Locate and catalog a Zeus door SDK or protocol specification before "
            "reviewing individual operations."
        ),
    },
}


def _distribution(
    items: list[dict[str, Any]], field: str, vocabulary: tuple[str, ...]
) -> dict[str, int]:
    counts = {value: 0 for value in vocabulary}
    for item in items:
        counts[item[field]] += 1
    return counts


def build_crosswalk_triage(root: Path) -> dict[str, Any]:
    queue = build_crosswalk_work_queue(root)
    crosswalk = load_crosswalk(root)
    queue_ids = {item["id"] for item in queue["items"]}
    configured_ids = set(ITEM_TRIAGE)
    missing = sorted(queue_ids - configured_ids)
    orphaned = sorted(configured_ids - queue_ids)
    if missing or orphaned:
        details = []
        if missing:
            details.append(f"untriaged queue items: {', '.join(missing)}")
        if orphaned:
            details.append(f"orphan triage items: {', '.join(orphaned)}")
        raise ValueError("; ".join(details))

    items = []
    for queue_item in queue["items"]:
        category, effort, confidence = ITEM_TRIAGE[queue_item["id"]]
        items.append(
            {
                **queue_item,
                "category": category,
                "effort": effort,
                "confidence": confidence,
                "triage_rationale": CATEGORY_RATIONALES[category],
            }
        )

    host_summaries = []
    for host_id in sorted({item["host"] for item in items}):
        host_items = [item for item in items if item["host"] == host_id]
        host = crosswalk["hosts"][host_id]
        reviewed = sum(
            row["status"] in {"verified", "partial"}
            for row in host["operations"]
        )
        research = HOST_RESEARCH[host_id]
        host_summaries.append(
            {
                "host": host_id,
                "host_name": host["host"].get("name"),
                "reviewed_mappings": reviewed,
                "remaining_mappings": len(host_items),
                "triage_categories": [
                    category
                    for category in CATEGORIES
                    if any(item["category"] == category for item in host_items)
                ],
                **research,
            }
        )

    return {
        "schema_version": 1,
        "milestone": "M6.2",
        "kind": "crosswalk-evidence-triage",
        "source_path": "catalog/crosswalk/work-queue.json",
        "semantics": {
            "category": "Primary reason the cell remains unassessed.",
            "effort": "Estimated evidence-research effort, not implementation effort.",
            "confidence": (
                "Confidence that sufficient additional evidence can be found."
            ),
            "unassessed": (
                "No reviewed mapping is recorded; this does not mean unsupported."
            ),
        },
        "vocabularies": {
            "categories": list(CATEGORIES),
            "efforts": list(EFFORTS),
            "confidences": list(CONFIDENCES),
            "documentation_qualities": list(DOCUMENTATION_QUALITIES),
            "recommended_priorities": list(RECOMMENDED_PRIORITIES),
        },
        "summary": {
            "total": len(items),
            "categories": _distribution(items, "category", CATEGORIES),
            "efforts": _distribution(items, "effort", EFFORTS),
            "confidences": _distribution(items, "confidence", CONFIDENCES),
        },
        "hosts": host_summaries,
        "items": items,
    }


def select_crosswalk_triage(
    root: Path, host: str | None = None
) -> dict[str, Any]:
    report = build_crosswalk_triage(root)
    if host is None:
        return report
    known_hosts = {summary["host"] for summary in report["hosts"]}
    if host not in known_hosts:
        raise KeyError(host)
    items = [item for item in report["items"] if item["host"] == host]
    selected = dict(report)
    selected["summary"] = {
        "total": len(items),
        "categories": _distribution(items, "category", CATEGORIES),
        "efforts": _distribution(items, "effort", EFFORTS),
        "confidences": _distribution(items, "confidence", CONFIDENCES),
    }
    selected["hosts"] = [
        summary for summary in report["hosts"] if summary["host"] == host
    ]
    selected["items"] = items
    selected["filters"] = {"host": host}
    return selected


def format_crosswalk_triage(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"M6.2 remaining evidence triage: {summary['total']} items",
        "hosts:",
    ]
    for host in report["hosts"]:
        categories = ", ".join(host["triage_categories"])
        lines.append(
            f"  {host['host']:<10} reviewed={host['reviewed_mappings']:<2} "
            f"remaining={host['remaining_mappings']:<2} "
            f"priority={host['recommended_priority']:<6} {categories}"
        )
    lines.append("items:")
    for item in report["items"]:
        lines.append(
            f"  {item['id']:<40} {item['category']:<29} "
            f"{item['effort']:<9} confidence={item['confidence']}"
        )
    if not report["items"]:
        lines.append("  no remaining unassessed cells")
    return "\n".join(lines)


def validate_crosswalk_triage(root: Path) -> int:
    expected = build_crosswalk_triage(root)
    path = root / "catalog" / "crosswalk" / "triage.json"
    assert path.exists(), "missing crosswalk evidence triage"
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored == expected, "stale crosswalk evidence triage"
    queue = build_crosswalk_work_queue(root)
    queue_ids = [item["id"] for item in queue["items"]]
    triage_ids = [item["id"] for item in stored["items"]]
    assert triage_ids == queue_ids, "triage must exactly cover the work queue"
    assert len(triage_ids) == len(set(triage_ids)), "duplicate triage item ID"
    assert all(item["status"] == "unassessed" for item in stored["items"])
    assert all(item["category"] in CATEGORIES for item in stored["items"])
    assert all(item["effort"] in EFFORTS for item in stored["items"])
    assert all(item["confidence"] in CONFIDENCES for item in stored["items"])
    return len(stored["items"])
