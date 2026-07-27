from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_crosswalk(root: Path) -> dict[str, Any]:
    base = root / "catalog" / "crosswalk"
    index = _load(base / "index.json")
    operations = _load(base / "operations.json")
    hosts = {
        summary["id"]: _load(root / summary["path"])
        for summary in index["hosts"]
    }
    return {"index": index, "operations": operations, "hosts": hosts}


def select_crosswalk(root: Path, target: str | None = None) -> dict[str, Any]:
    data = load_crosswalk(root)
    if target is None:
        return data["index"]
    if target.startswith("host:"):
        host_id = target[5:]
        if host_id not in data["hosts"]:
            raise KeyError(target)
        return data["hosts"][host_id]
    if target.startswith("operation:"):
        operation_id = target[10:]
        record = next((item for item in data["operations"]["operations"] if item["id"] == operation_id), None)
        if record is None:
            raise KeyError(target)
        return record
    host = data["hosts"].get(target)
    operation = next((item for item in data["operations"]["operations"] if item["id"] == target), None)
    if host is not None and operation is not None:
        raise ValueError(f"ambiguous crosswalk target: {target}; use host:{target} or operation:{target}")
    if host is not None:
        return host
    if operation is not None:
        return operation
    raise KeyError(target)


def format_host(record: dict[str, Any], include_unassessed: bool = False) -> str:
    host = record["host"]
    lines = [f"{host['id']} — {host['name']}", f"evidence: {host['evidence_class']}"]
    shown = 0
    for item in record["operations"]:
        if item["status"] == "unassessed" and not include_unassessed:
            continue
        symbols = ", ".join(item["symbols"]) if item["symbols"] else "—"
        lines.append(f"{item['operation']:<28} {item['status']:<10} {symbols}")
        shown += 1
    if shown == 0:
        lines.append("no reviewed mappings")
    return "\n".join(lines)


def format_operation(record: dict[str, Any], include_unassessed: bool = False) -> str:
    lines = [record["id"]]
    for host_id, item in sorted(record["hosts"].items()):
        if item["status"] == "unassessed" and not include_unassessed:
            continue
        symbols = ", ".join(item["symbols"]) if item["symbols"] else "—"
        lines.append(f"{host_id:<12} {item['status']:<10} {symbols}")
    if len(lines) == 1:
        lines.append("no reviewed mappings")
    return "\n".join(lines)


def format_index(index: dict[str, Any]) -> str:
    return (
        f"{index['title']}\n"
        f"source: {index['source_milestone']} ({index['source_path']})\n"
        f"hosts: {index['host_count']}\n"
        f"operations: {index['operation_count']}\n"
        f"reviewed mappings: {index['mapped_cell_count']}"
    )


def format_crosswalk(
    record: dict[str, Any], include_unassessed: bool = False
) -> str:
    if "title" in record and "host_count" in record:
        return format_index(record)
    if "host" in record:
        return format_host(record, include_unassessed)
    if "id" in record and "hosts" in record:
        return format_operation(record, include_unassessed)
    raise ValueError("unknown crosswalk record shape")

def validate_crosswalk(root: Path) -> tuple[int, int, int]:
    from .crosswalk_evidence import validate_crosswalk_evidence

    data = load_crosswalk(root)
    index = data["index"]
    hosts = data["hosts"]
    operations = data["operations"]["operations"]
    assert index["milestone"] == "M6.1"
    assert index["source_milestone"] == "M6.0"
    assert index["host_count"] == len(hosts)
    assert index["operation_count"] == len(operations)
    assert [item["id"] for item in index["hosts"]] == sorted(hosts)
    operation_ids = [item["id"] for item in operations]
    assert operation_ids == sorted(operation_ids)
    assert len(operation_ids) == len(set(operation_ids))
    mapped_cells = 0
    for host_id, host in hosts.items():
        assert host["host"]["id"] == host_id
        assert host["milestone"] == "M6.1"
        rows = host["operations"]
        assert [item["operation"] for item in rows] == operation_ids
        for row in rows:
            assert row["status"] in {"verified", "partial", "unassessed"}
            assert row["evidence_class"] == host["host"]["evidence_class"]
            if row["status"] == "unassessed":
                assert not row["symbols"]
            else:
                mapped_cells += 1
    for operation in operations:
        assert sorted(operation["hosts"]) == sorted(hosts)
        for host_id, cell in operation["hosts"].items():
            matching = next(item for item in hosts[host_id]["operations"] if item["operation"] == operation["id"])
            assert cell == {key: value for key, value in matching.items() if key != "operation"}
    assert index["mapped_cell_count"] == mapped_cells
    assert validate_crosswalk_evidence(root, data) == mapped_cells
    return len(hosts), len(operations), mapped_cells
