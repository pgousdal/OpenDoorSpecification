from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from .semantic import load_operations


CONTRACT_PATH = Path("catalog/contracts/adapter-contracts.json")
OUTCOMES = (
    "success",
    "unsupported",
    "invalid-request",
    "host-failure",
    "disconnected",
)
CATALOG_FIELDS = {"schema_version", "spec_version", "outcome_vocabulary", "contracts"}
CONTRACT_FIELDS = {
    "operation",
    "title",
    "description",
    "category",
    "normative_behavior",
    "inputs",
    "output",
    "outcomes",
    "unsupported_behavior",
    "lifecycle",
    "implementation_obligations",
    "compatibility_notes",
}
INPUT_FIELDS = {"name", "description"}
OUTPUT_FIELDS = {"result", "description"}
LIFECYCLE_FIELDS = {
    "normal_completion",
    "disconnect",
    "carrier_loss",
    "implementation_shutdown",
}
CATEGORIES = {"terminal", "session", "status", "host-command", "lifecycle"}
OPERATION_PATTERN = re.compile(r"^[a-z][a-z0-9-]*\.[a-z][a-z0-9_-]*$")


def load_adapter_contracts(root: Path) -> dict[str, Any]:
    return json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))


def _require_text(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _validate_text_list(values: Any, field: str, minimum: int = 0) -> None:
    if not isinstance(values, list) or len(values) < minimum:
        raise ValueError(f"{field} must contain at least {minimum} item(s)")
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{field} must contain non-empty strings")


def validate_adapter_contract_document(
    root: Path, document: dict[str, Any] | None = None
) -> int:
    data = document or load_adapter_contracts(root)
    unknown_catalog = set(data) - CATALOG_FIELDS
    missing_catalog = CATALOG_FIELDS - set(data)
    if unknown_catalog:
        raise ValueError(
            "unknown adapter contract catalog fields: "
            + ", ".join(sorted(unknown_catalog))
        )
    if missing_catalog:
        raise ValueError(
            "missing adapter contract catalog fields: "
            + ", ".join(sorted(missing_catalog))
        )
    if data.get("schema_version") != 1:
        raise ValueError("adapter contract schema_version must be 1")
    _require_text(data.get("spec_version"), "spec_version")

    vocabulary = data["outcome_vocabulary"]
    if not isinstance(vocabulary, list) or [item.get("id") for item in vocabulary] != list(OUTCOMES):
        raise ValueError("outcome vocabulary must use the closed canonical ordering")
    for outcome in vocabulary:
        if set(outcome) != {"id", "description"}:
            raise ValueError("outcome vocabulary entries have invalid fields")
        if outcome["id"] not in OUTCOMES:
            raise ValueError(f"invalid outcome vocabulary value: {outcome['id']}")
        _require_text(outcome["description"], f"outcome {outcome['id']} description")

    canonical = load_operations(root)["operations"]
    canonical_ids = [operation["id"] for operation in canonical]
    canonical_by_id = {operation["id"]: operation for operation in canonical}
    contracts = data["contracts"]
    if not isinstance(contracts, list) or len(contracts) != len(canonical_ids):
        raise ValueError(
            f"adapter contract catalog must contain exactly {len(canonical_ids)} contracts"
        )
    contract_ids = [contract.get("operation") for contract in contracts]
    if contract_ids != canonical_ids:
        raise ValueError("adapter contracts must follow canonical operation ordering")
    if len(contract_ids) != len(set(contract_ids)):
        raise ValueError("duplicate adapter contract operation ID")

    for contract in contracts:
        operation_id = contract.get("operation")
        if not isinstance(operation_id, str) or not OPERATION_PATTERN.fullmatch(operation_id):
            raise ValueError(f"invalid adapter contract operation ID: {operation_id}")
        unknown = set(contract) - CONTRACT_FIELDS
        missing = CONTRACT_FIELDS - set(contract)
        if unknown:
            raise ValueError(
                f"{operation_id}: unknown contract fields: {', '.join(sorted(unknown))}"
            )
        if missing:
            raise ValueError(
                f"{operation_id}: missing contract fields: {', '.join(sorted(missing))}"
            )
        _require_text(contract["title"], f"{operation_id} title")
        _require_text(contract["description"], f"{operation_id} description")
        if contract["category"] not in CATEGORIES:
            raise ValueError(f"{operation_id}: invalid contract category")
        _validate_text_list(contract["normative_behavior"], f"{operation_id} normative_behavior", 1)
        _validate_text_list(
            contract["implementation_obligations"],
            f"{operation_id} implementation_obligations",
            1,
        )
        _validate_text_list(
            contract["compatibility_notes"],
            f"{operation_id} compatibility_notes",
        )
        operation = canonical_by_id[operation_id]
        inputs = contract["inputs"]
        if not isinstance(inputs, list):
            raise ValueError(f"{operation_id}: inputs must be an array")
        input_names = []
        for item in inputs:
            if not isinstance(item, dict) or set(item) != INPUT_FIELDS:
                raise ValueError(f"{operation_id}: invalid input fields")
            if not isinstance(item["name"], str) or not re.fullmatch(
                r"[a-z][a-z0-9_]*", item["name"]
            ):
                raise ValueError(f"{operation_id}: invalid input name")
            _require_text(item["description"], f"{operation_id} input description")
            input_names.append(item["name"])
        if len(input_names) != len(set(input_names)):
            raise ValueError(f"{operation_id}: duplicate input name")
        if input_names != operation["inputs"]:
            raise ValueError(f"{operation_id}: inputs do not match canonical operation")
        output = contract["output"]
        if not isinstance(output, dict) or set(output) != OUTPUT_FIELDS:
            raise ValueError(f"{operation_id}: invalid output fields")
        if output["result"] != operation["result"]:
            raise ValueError(f"{operation_id}: output result does not match canonical operation")
        _require_text(output["description"], f"{operation_id} output description")
        outcomes = contract["outcomes"]
        if not isinstance(outcomes, list) or not outcomes:
            raise ValueError(f"{operation_id}: outcomes must be non-empty")
        if len(outcomes) != len(set(outcomes)):
            raise ValueError(f"{operation_id}: duplicate outcome")
        if any(outcome not in OUTCOMES for outcome in outcomes):
            raise ValueError(f"{operation_id}: invalid outcome value")
        _require_text(contract["unsupported_behavior"], f"{operation_id} unsupported_behavior")
        lifecycle = contract["lifecycle"]
        if not isinstance(lifecycle, dict) or set(lifecycle) != LIFECYCLE_FIELDS:
            raise ValueError(f"{operation_id}: invalid lifecycle fields")
        for field, value in lifecycle.items():
            _require_text(value, f"{operation_id} lifecycle.{field}")
    return len(contracts)


def list_adapter_contracts(root: Path) -> dict[str, Any]:
    document = load_adapter_contracts(root)
    validate_adapter_contract_document(root, document)
    return document


def select_adapter_contract(root: Path, operation_id: str) -> dict[str, Any]:
    document = list_adapter_contracts(root)
    for contract in document["contracts"]:
        if contract["operation"] == operation_id:
            return contract
    raise KeyError(operation_id)


def format_adapter_contract(contract: dict[str, Any]) -> str:
    lines = [
        f"{contract['operation']} — {contract['title']}",
        contract["description"],
        f"category: {contract['category']}",
        "normative behavior:",
    ]
    lines.extend(f"  {value}" for value in contract["normative_behavior"])
    lines.append(f"inputs: {', '.join(item['name'] for item in contract['inputs']) or 'none'}")
    lines.append(f"output: {contract['output']['result']}")
    lines.append("outcomes: " + ", ".join(contract["outcomes"]))
    lines.append("unsupported behavior: " + contract["unsupported_behavior"])
    lines.append("lifecycle:")
    for field, value in contract["lifecycle"].items():
        lines.append(f"  {field}: {value}")
    return "\n".join(lines)
