from __future__ import annotations

import json
from pathlib import Path

from .semantic import load_operations


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_profiles(root: Path) -> dict:
    return _load_json(root / "catalog" / "profiles" / "conformance.json")


def build_conformance_report(root: Path) -> dict:
    operations_doc = load_operations(root)
    operation_ids = [item["id"] for item in operations_doc["operations"]]
    profiles_doc = load_profiles(root)
    profiles = profiles_doc["profiles"]

    adapters = []
    for path in sorted((root / "catalog" / "adapters").glob("*.json")):
        data = _load_json(path)
        adapter_id = data.get("id", data.get("adapter"))
        supported = set(data["operations"])
        evaluations = []
        highest = None
        for profile in profiles:
            required = profile["required_operations"]
            missing = [operation for operation in required if operation not in supported]
            passed = not missing
            if passed:
                highest = profile["id"]
            evaluations.append({
                "profile": profile["id"],
                "passed": passed,
                "required_count": len(required),
                "supported_required_count": len(required) - len(missing),
                "missing_required_operations": missing,
            })
        adapters.append({
            "id": adapter_id,
            "kind": data.get("kind", "historical-adapter"),
            "implementation": data["implementation"],
            "declared_operation_count": len(supported),
            "unknown_operations": sorted(supported - set(operation_ids)),
            "highest_profile": highest,
            "profiles": evaluations,
        })

    return {
        "schema_version": 1,
        "spec_version": operations_doc["spec_version"],
        "profile_version": profiles_doc["profile_version"],
        "profiles": profiles,
        "adapters": adapters,
        "summary": {
            "profile_count": len(profiles),
            "adapter_count": len(adapters),
            "complete_adapters": sum(item["highest_profile"] == "complete" for item in adapters),
            "nonconforming_adapters": sum(item["highest_profile"] is None for item in adapters),
        },
    }


def write_conformance_report(root: Path, destination: Path | None = None) -> dict:
    report = build_conformance_report(root)
    target = destination or root / "catalog" / "knowledge" / "conformance-report.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
