from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

EVIDENCE_ORDER = {"documented": 0, "observed": 1, "inferred": 2, "unknown": 3}


def load_provenance(root: Path) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((root / "catalog" / "provenance").glob("*.json"))
    ]


def build_coverage(root: Path) -> dict:
    by_pair: dict[tuple[str, str], list[dict]] = {}
    for record in load_provenance(root):
        api = record.get("api")
        operation = record.get("operation")
        if api and operation and record.get("claim_type") == "operation-mapping":
            by_pair.setdefault((api, operation), []).append(record)

    rows = []
    evidence_counts: Counter[str] = Counter()
    verified_without_provenance = 0
    for path in sorted((root / "catalog" / "mappings").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        api = data["api"]
        for mapping in data["mappings"]:
            records = by_pair.get((api, mapping["operation"]), [])
            statuses = sorted({r["status"] for r in records}, key=EVIDENCE_ORDER.__getitem__)
            covered = bool(records)
            for status in statuses:
                evidence_counts[status] += 1
            if mapping["status"] == "verified" and not covered:
                verified_without_provenance += 1
            rows.append({
                "api": api,
                "operation": mapping["operation"],
                "mapping_status": mapping["status"],
                "evidence_statuses": statuses,
                "provenance_ids": sorted(r["id"] for r in records),
                "covered": covered,
            })

    covered_count = sum(row["covered"] for row in rows)
    return {
        "schema_version": 1,
        "summary": {
            "total": len(rows),
            "covered": covered_count,
            "uncovered": len(rows) - covered_count,
            "verified_without_provenance": verified_without_provenance,
            "by_evidence_status": dict(sorted(evidence_counts.items())),
        },
        "mappings": rows,
    }


def write_coverage(root: Path, destination: Path | None = None) -> dict:
    report = build_coverage(root)
    target = destination or root / "catalog" / "knowledge" / "provenance-coverage.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
