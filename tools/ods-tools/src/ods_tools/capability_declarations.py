from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

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
