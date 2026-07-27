from __future__ import annotations

import json
from pathlib import Path

from .coverage import build_coverage
from .semantic import load_operations


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_operation_records(root: Path) -> dict:
    definitions = load_operations(root)["operations"]
    index = _load_json(root / "catalog" / "knowledge" / "operation-index.json")
    coverage = build_coverage(root)

    implementations_by_operation = {
        item["id"]: item["implementations"] for item in index["operations"]
    }
    coverage_by_pair = {
        (row["api"], row["operation"]): row for row in coverage["mappings"]
    }

    adapters: list[dict] = []
    for path in sorted((root / "catalog" / "adapters").glob("*.json")):
        data = _load_json(path)
        adapters.append({
            "id": data.get("id", data.get("adapter")),
            "kind": data.get("kind", "historical"),
            "implementation": data["implementation"],
            "conformance": data.get("conformance", "unspecified"),
            "operations": data["operations"],
        })

    records = []
    for definition in definitions:
        operation_id = definition["id"]
        historical = []
        for implementation in implementations_by_operation[operation_id]:
            row = coverage_by_pair[(implementation["api"], operation_id)]
            historical.append({
                **implementation,
                "evidence_statuses": row["evidence_statuses"],
                "provenance_ids": row["provenance_ids"],
                "covered": row["covered"],
            })
        adapter_status = [
            {
                "adapter": adapter["id"],
                "kind": adapter["kind"],
                "implementation": adapter["implementation"],
                "conformance": adapter["conformance"],
                "supported": operation_id in adapter["operations"],
            }
            for adapter in adapters
        ]
        records.append({
            "schema_version": 1,
            "spec_version": load_operations(root)["spec_version"],
            "id": operation_id,
            "definition": definition,
            "historical_implementations": historical,
            "adapter_status": adapter_status,
            "summary": {
                "historical_implementation_count": len(historical),
                "covered_historical_implementation_count": sum(i["covered"] for i in historical),
                "adapter_count": sum(a["supported"] for a in adapter_status),
            },
        })

    return {
        "schema_version": 1,
        "spec_version": load_operations(root)["spec_version"],
        "operations": records,
    }


def write_operation_records(root: Path, destination: Path | None = None) -> dict:
    result = build_operation_records(root)
    target = destination or root / "catalog" / "knowledge" / "operations"
    target.mkdir(parents=True, exist_ok=True)
    expected = {record["id"].replace(".", "-") + ".json" for record in result["operations"]}
    for path in target.glob("*.json"):
        if path.name not in expected:
            path.unlink()
    for record in result["operations"]:
        path = target / (record["id"].replace(".", "-") + ".json")
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    index = {
        "schema_version": 1,
        "spec_version": result["spec_version"],
        "operations": [
            {
                "id": record["id"],
                "path": "catalog/knowledge/operations/" + record["id"].replace(".", "-") + ".json",
                "historical_implementation_count": record["summary"]["historical_implementation_count"],
                "adapter_count": record["summary"]["adapter_count"],
            }
            for record in result["operations"]
        ],
    }
    (target / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return result
