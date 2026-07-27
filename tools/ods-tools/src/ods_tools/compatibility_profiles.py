from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from .semantic import load_operations


PROFILE_PATH = Path("catalog/profiles/compatibility.json")
MATURITIES = {"draft", "stable", "deprecated"}
PROFILE_FIELDS = {
    "id",
    "title",
    "description",
    "maturity",
    "required_operations",
    "optional_operations",
    "operations_outside_profile",
    "compatibility_expectations",
    "conformance_evidence_expectations",
}
CATALOG_FIELDS = {"schema_version", "profile_version", "spec_version", "profiles"}
OPERATION_FIELDS = (
    "required_operations",
    "optional_operations",
    "operations_outside_profile",
)


def load_compatibility_profiles(root: Path) -> dict[str, Any]:
    return json.loads((root / PROFILE_PATH).read_text(encoding="utf-8"))


def validate_compatibility_profile_document(
    root: Path, document: dict[str, Any] | None = None
) -> int:
    data = document or load_compatibility_profiles(root)
    unknown_catalog_fields = set(data) - CATALOG_FIELDS
    missing_catalog_fields = CATALOG_FIELDS - set(data)
    if unknown_catalog_fields:
        raise ValueError(
            "unknown compatibility catalog fields: "
            + ", ".join(sorted(unknown_catalog_fields))
        )
    if missing_catalog_fields:
        raise ValueError(
            "missing compatibility catalog fields: "
            + ", ".join(sorted(missing_catalog_fields))
        )
    if data.get("schema_version") != 1:
        raise ValueError("compatibility profile schema_version must be 1")
    for field in ("profile_version", "spec_version"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f"compatibility profile {field} must be non-empty")
    profiles = data.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("compatibility profile catalog must contain profiles")
    operation_ids = {
        operation["id"] for operation in load_operations(root)["operations"]
    }
    profile_ids: set[str] = set()
    for profile in profiles:
        if not isinstance(profile, dict):
            raise ValueError("compatibility profile must be an object")
        unknown = set(profile) - PROFILE_FIELDS
        missing = PROFILE_FIELDS - set(profile)
        if unknown:
            raise ValueError(
                f"unknown compatibility profile fields: {', '.join(sorted(unknown))}"
            )
        if missing:
            raise ValueError(
                f"missing compatibility profile fields: {', '.join(sorted(missing))}"
            )
        profile_id = profile["id"]
        if not isinstance(profile_id, str) or not profile_id:
            raise ValueError("compatibility profile ID must be non-empty")
        if not re.fullmatch(r"[a-z][a-z0-9-]*", profile_id):
            raise ValueError(f"invalid compatibility profile ID: {profile_id}")
        if profile_id in profile_ids:
            raise ValueError(f"duplicate compatibility profile ID: {profile_id}")
        profile_ids.add(profile_id)
        if profile["maturity"] not in MATURITIES:
            raise ValueError(f"invalid maturity for compatibility profile: {profile_id}")
        for field in ("title", "description"):
            if not isinstance(profile[field], str) or not profile[field].strip():
                raise ValueError(f"{profile_id}: {field} must be non-empty")
        sets: dict[str, set[str]] = {}
        for field in OPERATION_FIELDS:
            values = profile[field]
            if not isinstance(values, list) or any(
                not isinstance(operation, str) for operation in values
            ):
                raise ValueError(f"{profile_id}: {field} must be a string array")
            if len(values) != len(set(values)):
                raise ValueError(f"{profile_id}: duplicate operation in {field}")
            unknown_operations = sorted(set(values) - operation_ids)
            if unknown_operations:
                raise ValueError(
                    f"{profile_id}: unknown canonical operation: "
                    f"{', '.join(unknown_operations)}"
                )
            sets[field] = set(values)
        if not sets["required_operations"]:
            raise ValueError(f"{profile_id}: required_operations cannot be empty")
        for left_index, left in enumerate(OPERATION_FIELDS):
            for right in OPERATION_FIELDS[left_index + 1 :]:
                overlap = sets[left] & sets[right]
                if overlap:
                    raise ValueError(
                        f"{profile_id}: operation appears in both {left} and {right}: "
                        f"{', '.join(sorted(overlap))}"
                    )
        for field in (
            "compatibility_expectations",
            "conformance_evidence_expectations",
        ):
            values = profile[field]
            if not isinstance(values, list) or not values or any(
                not isinstance(value, str) or not value.strip() for value in values
            ):
                raise ValueError(f"{profile_id}: {field} must contain non-empty strings")
    return len(profiles)


def list_compatibility_profiles(root: Path) -> dict[str, Any]:
    document = load_compatibility_profiles(root)
    validate_compatibility_profile_document(root, document)
    return document


def select_compatibility_profile(root: Path, profile_id: str) -> dict[str, Any]:
    document = list_compatibility_profiles(root)
    for profile in document["profiles"]:
        if profile["id"] == profile_id:
            return profile
    raise KeyError(profile_id)


def format_compatibility_profile(profile: dict[str, Any]) -> str:
    lines = [
        f"{profile['id']} — {profile['title']}",
        profile["description"],
        f"maturity: {profile['maturity']}",
        f"required operations: {len(profile['required_operations'])}",
    ]
    lines.extend(f"  {operation}" for operation in profile["required_operations"])
    lines.append(
        f"optional operations: {len(profile['optional_operations'])}"
    )
    lines.extend(
        f"  {operation}" for operation in profile["optional_operations"]
    )
    lines.append(
        f"outside profile: {len(profile['operations_outside_profile'])}"
    )
    lines.append("compatibility expectations:")
    lines.extend(f"  {value}" for value in profile["compatibility_expectations"])
    lines.append("conformance evidence expectations:")
    lines.extend(
        f"  {value}" for value in profile["conformance_evidence_expectations"]
    )
    return "\n".join(lines)
