from __future__ import annotations
import json
from pathlib import Path


def load_operations(root: Path) -> dict:
    return json.loads((root / "catalog" / "operations" / "core.json").read_text(encoding="utf-8"))


def load_mapping(root: Path, api: str) -> dict:
    path = root / "catalog" / "mappings" / f"{api}.json"
    if not path.is_file():
        raise KeyError(api)
    return json.loads(path.read_text(encoding="utf-8"))


def compare(root: Path, apis: list[str]) -> list[dict]:
    operations = [item["id"] for item in load_operations(root)["operations"]]
    indexed = {}
    for api in apis:
        data = load_mapping(root, api)
        indexed[api] = {m["operation"]: m["status"] for m in data["mappings"]}
    return [{"operation": op, **{api: indexed[api].get(op, "unknown") for api in apis}} for op in operations]
