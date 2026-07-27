from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from .adapter_contracts import load_adapter_contracts
from .compatibility_profiles import load_compatibility_profiles
from .semantic import load_operations


CAPABILITIES_DIR = Path("catalog/capabilities")
CAPABILITY_STATUSES = frozenset({"supported", "partial", "unsupported"})
DECLARATION_FIELDS = frozenset({
    "schema_version",
    "spec_version",
    "implementation_id",
    "implementation_name",
    "implementation_version",
    "target_platform",
    "supported_profiles",
    "capabilities",
})
CAPABILITY_FIELDS = frozenset({"operation", "status", "notes"})
ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
OPERATION_PATTERN = re.compile(r"^[a-z][a-z0-9-]*\.[a-z][a-z0-9_-]*$")


def load_capability_declarations(root: Path) -> dict[str, dict[str, Any]]:
    declarations: dict[str, dict[str, Any]] = {}
    directory = root / CAPABILITIES_DIR
    if not directory.is_dir():
        return declarations
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "implementation_id" not in data:
            continue
        impl_id = data["implementation_id"]
        declarations[impl_id] = data
    return declarations


def validate_capability_declaration_document(
    root: Path,
    document: dict[str, Any] | None = None,
    declarations: dict[str, dict[str, Any]] | None = None,
) -> int:
    if declarations is not None:
        docs = declarations
    elif document is not None:
        docs = {"__single__": document}
    else:
        docs = load_capability_declarations(root)
    operation_ids = {
        op["id"] for op in load_operations(root)["operations"]
    }
    seen_ids: set[str] = set()

    for decl_id, data in docs.items():
        unknown = set(data) - DECLARATION_FIELDS
        missing = DECLARATION_FIELDS - set(data)
        if unknown:
            raise ValueError(
                f"{decl_id}: unknown declaration fields: "
                + ", ".join(sorted(unknown))
            )
        if missing:
            raise ValueError(
                f"{decl_id}: missing declaration fields: "
                + ", ".join(sorted(missing))
            )
        if data.get("schema_version") != 1:
            raise ValueError(f"{decl_id}: schema_version must be 1")
        for text_field in ("spec_version", "implementation_name", "implementation_version", "target_platform"):
            value = data.get(text_field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{decl_id}: {text_field} must be a non-empty string")
        impl_id_val = data["implementation_id"]
        if not isinstance(impl_id_val, str) or not ID_PATTERN.fullmatch(impl_id_val):
            raise ValueError(f"invalid implementation_id: {impl_id_val}")
        if impl_id_val in seen_ids:
            raise ValueError(f"duplicate implementation_id: {impl_id_val}")
        seen_ids.add(impl_id_val)

        profiles = data["supported_profiles"]
        if not isinstance(profiles, list):
            raise ValueError(f"{decl_id}: supported_profiles must be an array")
        for profile_id in profiles:
            if not isinstance(profile_id, str) or not ID_PATTERN.fullmatch(profile_id):
                raise ValueError(
                    f"{decl_id}: invalid profile ID in supported_profiles: {profile_id}"
                )
        if len(profiles) != len(set(profiles)):
            raise ValueError(f"{decl_id}: duplicate profile in supported_profiles")

        capabilities = data["capabilities"]
        if not isinstance(capabilities, list):
            raise ValueError(f"{decl_id}: capabilities must be an array")
        seen_operations: set[str] = set()
        for cap in capabilities:
            if not isinstance(cap, dict):
                raise ValueError(f"{decl_id}: each capability must be an object")
            unknown_cap = set(cap) - CAPABILITY_FIELDS
            missing_cap = CAPABILITY_FIELDS - set(cap)
            if missing_cap != {"notes"}:
                actual_missing = missing_cap - {"notes"}
                if actual_missing:
                    raise ValueError(
                        f"{decl_id}: missing capability fields: "
                        + ", ".join(sorted(actual_missing))
                    )
            if unknown_cap:
                raise ValueError(
                    f"{decl_id}: unknown capability fields: "
                    + ", ".join(sorted(unknown_cap))
                )
            op = cap.get("operation")
            if not isinstance(op, str) or not OPERATION_PATTERN.fullmatch(op):
                raise ValueError(f"{decl_id}: invalid operation ID: {op}")
            if op not in operation_ids:
                raise ValueError(
                    f"{decl_id}: unknown canonical operation: {op}"
                )
            if op in seen_operations:
                raise ValueError(
                    f"{decl_id}: duplicate operation declaration: {op}"
                )
            seen_operations.add(op)
            status = cap.get("status")
            if status not in CAPABILITY_STATUSES:
                raise ValueError(
                    f"{decl_id}: invalid capability status for {op}: {status}"
                )
            notes = cap.get("notes")
            if notes is not None and (not isinstance(notes, str) or not notes.strip()):
                raise ValueError(f"{decl_id}: notes for {op} must be a non-empty string when present")
    return len(docs)


def list_capability_declarations(root: Path) -> dict[str, Any]:
    declarations = load_capability_declarations(root)
    return {
        "declaration_count": len(declarations),
        "declarations": [
            {
                "implementation_id": d["implementation_id"],
                "implementation_name": d["implementation_name"],
                "implementation_version": d["implementation_version"],
                "target_platform": d["target_platform"],
                "supported_profiles": d["supported_profiles"],
                "capability_count": len(d["capabilities"]),
            }
            for d in declarations.values()
        ],
    }


def select_capability_declaration(root: Path, impl_id: str) -> dict[str, Any]:
    declarations = load_capability_declarations(root)
    if impl_id not in declarations:
        raise KeyError(impl_id)
    return declarations[impl_id]


def format_capability_declaration(declaration: dict[str, Any]) -> str:
    lines = [
        f"{declaration['implementation_id']} — {declaration['implementation_name']}",
        f"version: {declaration['implementation_version']}",
        f"platform: {declaration['target_platform']}",
        f"spec: {declaration['spec_version']}",
        "supported profiles: " + ", ".join(declaration["supported_profiles"]),
        "capabilities:",
    ]
    for cap in declaration["capabilities"]:
        line = f"  {cap['operation']:<28} {cap['status']}"
        if "notes" in cap:
            line += f"  ({cap['notes']})"
        lines.append(line)
    return "\n".join(lines)


def validate_profile_satisfaction(
    root: Path,
    declaration: dict[str, Any],
    profiles_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profiles_source = (
        profiles_data
        if profiles_data is not None
        else load_compatibility_profiles(root)
    )
    profiles_by_id = {p["id"]: p for p in profiles_source["profiles"]}
    capability_by_op = {
        c["operation"]: c["status"] for c in declaration["capabilities"]
    }
    impl_id = declaration["implementation_id"]
    results: dict[str, Any] = {}
    for profile_id in sorted(declaration["supported_profiles"]):
        if profile_id not in profiles_by_id:
            results[profile_id] = {
                "exists": False,
                "satisfied": False,
                "missing_required": [],
                "partial_required": [],
            }
            continue
        profile = profiles_by_id[profile_id]
        required = profile["required_operations"]
        missing: list[str] = []
        partial: list[str] = []
        for op in required:
            status = capability_by_op.get(op)
            if status is None or status == "unsupported":
                missing.append(op)
            elif status == "partial":
                partial.append(op)
            elif status != "supported":
                missing.append(op)
        results[profile_id] = {
            "exists": True,
            "satisfied": not missing and not partial,
            "missing_required": missing,
            "partial_required": partial,
        }
    return results


def validate_contract_references(
    root: Path,
    declaration: dict[str, Any],
    contracts_data: dict[str, Any] | None = None,
    canonical_ids: set[str] | None = None,
) -> dict[str, Any]:
    contracts_source = (
        contracts_data
        if contracts_data is not None
        else load_adapter_contracts(root)
    )
    contract_ops = {c["operation"] for c in contracts_source["contracts"]}
    if canonical_ids is None:
        canonical_ids = {
            op["id"] for op in load_operations(root)["operations"]
        }
    unknown_ops: list[str] = []
    no_contract_ops: list[str] = []
    for cap in declaration["capabilities"]:
        op = cap["operation"]
        if op not in canonical_ids:
            unknown_ops.append(op)
        if op not in contract_ops:
            no_contract_ops.append(op)
    if (root / "catalog" / "contracts" / "adapter-contracts.json").exists():
        for contract in contracts_source["contracts"]:
            op = contract["operation"]
            if op not in canonical_ids:
                if op not in unknown_ops:
                    unknown_ops.append(op)
    return {
        "all_have_contracts": not no_contract_ops,
        "operations_without_contract": sorted(no_contract_ops),
        "unknown_canonical_operations": sorted(unknown_ops),
    }


def validate_capability_declaration(
    root: Path,
    declaration: dict[str, Any],
    profiles_data: dict[str, Any] | None = None,
    contracts_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    impl_id = declaration["implementation_id"]
    profiles = validate_profile_satisfaction(
        root, declaration, profiles_data
    )
    contracts = validate_contract_references(
        root, declaration, contracts_data
    )
    satisfied_count = sum(
        1 for p in profiles.values() if p.get("satisfied")
    )
    partial_count = sum(
        1 for p in profiles.values()
        if p.get("exists") and not p["satisfied"]
    )
    return {
        "implementation_id": impl_id,
        "profiles": profiles,
        "contracts": contracts,
        "profile_count": {
            "satisfied": satisfied_count,
            "partial": partial_count,
            "unknown": sum(
                1 for p in profiles.values() if not p.get("exists")
            ),
        },
    }


def validate_all_capability_declarations(
    root: Path,
    profiles_data: dict[str, Any] | None = None,
    contracts_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    declarations = load_capability_declarations(root)
    results = sorted(
        (
            validate_capability_declaration(
                root, d, profiles_data, contracts_data
            )
            for d in declarations.values()
        ),
        key=lambda r: r["implementation_id"],
    )
    all_satisfied = all(
        all(p.get("satisfied", False) for p in r["profiles"].values())
        for r in results
    )
    return {
        "declaration_count": len(declarations),
        "all_satisfied": all_satisfied,
        "results": results,
    }


def format_validation_text(result: dict[str, Any]) -> str:
    lines: list[str] = []
    profiles = result["profiles"]
    for profile_id in sorted(profiles):
        p = profiles[profile_id]
        if not p.get("exists"):
            lines.append(f"  {profile_id}: unknown profile")
            continue
        if p["satisfied"]:
            lines.append(f"  {profile_id}: satisfies")
        else:
            lines.append(f"  {profile_id}: does not satisfy")
            if p["missing_required"]:
                lines.append("    missing:")
                for op in p["missing_required"]:
                    lines.append(f"      {op}")
            if p["partial_required"]:
                lines.append("    partial:")
                for op in p["partial_required"]:
                    lines.append(f"      {op}")
    contracts = result["contracts"]
    if not contracts["all_have_contracts"]:
        lines.append("  contract issues:")
        for op in contracts["operations_without_contract"]:
            lines.append(f"    {op}: no adapter contract")
        for op in contracts["unknown_canonical_operations"]:
            lines.append(f"    {op}: not a canonical operation")
    return "\n".join(lines)
