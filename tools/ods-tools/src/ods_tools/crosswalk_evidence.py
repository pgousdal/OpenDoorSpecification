from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .crosswalk import load_crosswalk


REVIEWED_STATUSES = {"verified", "partial"}
VALID_STATUSES = REVIEWED_STATUSES | {"unassessed"}
PLACEHOLDERS = {"todo", "unknown", "none", "n/a", "na", "not applicable"}
EVIDENCE_FIELDS = {"archive", "path", "symbol", "note"}


class EvidenceValidationError(ValueError):
    """Raised when reviewed crosswalk evidence is incomplete or inconsistent."""


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fail(mapping_id: str, message: str) -> None:
    raise EvidenceValidationError(f"{mapping_id}: {message}")


def _text(mapping_id: str, field: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(mapping_id, f"{field} must be a non-empty string")
    text = value.strip()
    normalized = text.casefold()
    if normalized in PLACEHOLDERS or normalized.startswith("todo"):
        _fail(mapping_id, f"{field} contains placeholder text: {text}")
    return text


def _archive_entries(root: Path) -> dict[str, set[str]]:
    archives: dict[str, set[str]] = {}
    for path in sorted((root / "catalog" / "archives").glob("*.json")):
        manifest = _load(path)
        archives[manifest["source_filename"]] = {
            entry["path"] for entry in manifest["entries"]
        }
    return archives


def _provenance_records(root: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "catalog" / "provenance").glob("*.json")):
        record = _load(path)
        record_id = record["id"]
        if record_id in records:
            raise EvidenceValidationError(
                f"{record_id}: duplicate provenance record ID"
            )
        records[record_id] = record
    return records


def validate_crosswalk_evidence(
    root: Path,
    data: dict[str, Any] | None = None,
) -> int:
    crosswalk = data or load_crosswalk(root)
    archives = _archive_entries(root)
    provenance = _provenance_records(root)
    canonical_operations = {
        operation["id"]
        for operation in _load(root / "catalog" / "operations" / "core.json")[
            "operations"
        ]
    }
    census_index = _load(root / "catalog" / "census" / "index.json")
    census_hosts = {item["id"]: item for item in census_index["systems"]}
    seen_ids: set[str] = set()
    reviewed_count = 0

    host_value = crosswalk["hosts"]
    hosts = (
        {record["host"]["id"]: record for record in host_value}
        if isinstance(host_value, list)
        else host_value
    )
    for host_id, host_record in sorted(hosts.items()):
        if host_id not in census_hosts:
            _fail(host_id, "host is not present in the census index")
        census_path_value = host_record["host"].get("census_path")
        census_path = root / _text(
            host_id, "host.census_path", census_path_value
        )
        if not census_path.is_file():
            _fail(host_id, f"orphan census reference: {census_path_value}")
        census = _load(census_path)
        if census.get("id") != host_id:
            _fail(host_id, "census record host does not match")
        census_mappings = {
            mapping["operation"]: mapping
            for mapping in census.get("mappings", [])
        }

        for cell in host_record["operations"]:
            operation_id = cell.get("operation")
            mapping_id = cell.get("id", f"{host_id}:{operation_id}")
            status = cell.get("status")
            if status not in VALID_STATUSES:
                _fail(str(mapping_id), f"invalid status: {status}")
            if operation_id not in canonical_operations:
                _fail(str(mapping_id), f"orphan canonical operation: {operation_id}")

            if status == "unassessed":
                forbidden = (
                    cell.get("symbols")
                    or cell.get("evidence")
                    or cell.get("rationale")
                    or cell.get("limitations")
                    or cell.get("provenance")
                )
                if forbidden:
                    _fail(str(mapping_id), "unassessed cell contains reviewed evidence")
                continue

            reviewed_count += 1
            expected_id = f"{host_id}:{operation_id}"
            if _text(expected_id, "id", cell.get("id")) != expected_id:
                _fail(expected_id, "stable mapping ID does not match host and operation")
            if expected_id in seen_ids:
                _fail(expected_id, "duplicate stable mapping ID")
            seen_ids.add(expected_id)
            if _text(expected_id, "host", cell.get("host")) != host_id:
                _fail(expected_id, "mapping host does not match containing host")
            if operation_id not in census_mappings:
                _fail(expected_id, "orphan census mapping reference")
            if census_mappings[operation_id].get("status") != status:
                _fail(expected_id, "generated status does not match census mapping")

            symbols = cell.get("symbols")
            if not isinstance(symbols, list) or not symbols:
                _fail(expected_id, "symbols must be a non-empty list")
            for index, symbol in enumerate(symbols):
                _text(expected_id, f"symbols[{index}]", symbol)
            _text(expected_id, "rationale", cell.get("rationale"))

            limitations = cell.get("limitations")
            if not isinstance(limitations, list):
                _fail(expected_id, "limitations must be an array")
            if status == "partial" and not limitations:
                _fail(expected_id, "partial mapping requires limitations")
            for index, limitation in enumerate(limitations):
                _text(expected_id, f"limitations[{index}]", limitation)

            evidence = cell.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                _fail(expected_id, "evidence must be a non-empty array")
            seen_evidence: set[tuple[str, str, str]] = set()
            for index, source in enumerate(evidence):
                if not isinstance(source, dict):
                    _fail(expected_id, f"evidence[{index}] must be an object")
                unknown_fields = set(source) - EVIDENCE_FIELDS
                if unknown_fields:
                    _fail(
                        expected_id,
                        f"evidence[{index}] has unknown fields: "
                        f"{', '.join(sorted(unknown_fields))}",
                    )
                archive = _text(
                    expected_id, f"evidence[{index}].archive", source.get("archive")
                )
                document = _text(
                    expected_id, f"evidence[{index}].path", source.get("path")
                )
                symbol = _text(
                    expected_id, f"evidence[{index}].symbol", source.get("symbol")
                )
                if "note" in source:
                    _text(
                        expected_id,
                        f"evidence[{index}].note",
                        source["note"],
                    )
                if archive not in archives:
                    _fail(expected_id, f"orphan archive reference: {archive}")
                if document not in archives[archive]:
                    _fail(
                        expected_id,
                        f"orphan document reference: {archive}:{document}",
                    )
                key = (archive, document, symbol)
                if key in seen_evidence:
                    _fail(expected_id, f"duplicate evidence entry at index {index}")
                seen_evidence.add(key)

            provenance_ids = cell.get("provenance", [])
            if not isinstance(provenance_ids, list):
                _fail(expected_id, "provenance must be an array")
            if len(provenance_ids) != len(set(provenance_ids)):
                _fail(expected_id, "duplicate provenance reference")
            for record_id in provenance_ids:
                record_id = _text(expected_id, "provenance entry", record_id)
                record = provenance.get(record_id)
                if record is None:
                    _fail(expected_id, f"orphan provenance reference: {record_id}")
                if (
                    record.get("claim_type") != "operation-mapping"
                    or record.get("api") != host_id
                    or record.get("operation") != operation_id
                ):
                    _fail(
                        expected_id,
                        f"inconsistent provenance reference: {record_id}",
                    )

    return reviewed_count


def select_mapping_evidence(
    root: Path,
    host_id: str,
    operation_id: str,
) -> dict[str, Any]:
    data = load_crosswalk(root)
    if host_id not in data["hosts"]:
        raise KeyError(host_id)
    cell = next(
        (
            row
            for row in data["hosts"][host_id]["operations"]
            if row["operation"] == operation_id
        ),
        None,
    )
    if cell is None:
        raise KeyError(operation_id)
    if cell["status"] == "unassessed":
        raise EvidenceValidationError(
            f"{host_id}:{operation_id}: mapping is unassessed and has no reviewed evidence"
        )
    return {
        "id": cell["id"],
        "host": host_id,
        "host_name": data["hosts"][host_id]["host"]["name"],
        "operation": operation_id,
        "status": cell["status"],
        "symbols": cell["symbols"],
        "rationale": cell["rationale"],
        "limitations": cell["limitations"],
        "evidence": cell["evidence"],
        **({"provenance": cell["provenance"]} if cell.get("provenance") else {}),
    }


def format_mapping_evidence(record: dict[str, Any]) -> str:
    lines = [
        f"{record['id']} — {record['status']}",
        f"host: {record['host_name']}",
        f"symbols: {', '.join(record['symbols'])}",
        f"rationale: {record['rationale']}",
        "evidence:",
    ]
    for source in record["evidence"]:
        lines.append(
            f"  {source['archive']}:{source['path']} — {source['symbol']}"
        )
        if source.get("note"):
            lines.append(f"    {source['note']}")
    if record["limitations"]:
        lines.append("limitations:")
        lines.extend(f"  {limitation}" for limitation in record["limitations"])
    else:
        lines.append("limitations: none recorded")
    if record.get("provenance"):
        lines.append(f"provenance: {', '.join(record['provenance'])}")
    return "\n".join(lines)
