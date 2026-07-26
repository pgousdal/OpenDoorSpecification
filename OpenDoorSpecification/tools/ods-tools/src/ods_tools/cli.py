from __future__ import annotations
import argparse, json
from pathlib import Path
from .parsers.lha import inspect
from .semantic import compare, load_mapping, load_operations


def repo_root() -> Path:
    p = Path.cwd()
    for candidate in [p, *p.parents]:
        if (candidate / "catalog" / "archives").is_dir():
            return candidate
    raise SystemExit("ODS repository root not found")


def validate(root: Path) -> tuple[int, int, int]:
    manifests = []
    for path in sorted((root / "catalog" / "archives").glob("*.json")):
        manifests.append(json.loads(path.read_text(encoding="utf-8")))
    seen = set()
    for data in manifests:
        assert data["entry_count"] == len(data["entries"]), data["source_filename"]
        assert len(data["source_sha256"]) == 64
        assert data["source_filename"] not in seen
        seen.add(data["source_filename"])
        for entry in data["entries"]:
            assert not Path(entry["path"]).is_absolute()
            assert ".." not in Path(entry["path"]).parts
    operations = load_operations(root)["operations"]
    operation_ids = [item["id"] for item in operations]
    assert len(operation_ids) == len(set(operation_ids))
    mapping_count = 0
    for path in sorted((root / "catalog" / "mappings").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for mapping in data["mappings"]:
            assert mapping["operation"] in operation_ids, path
            assert mapping["symbols"], path
            mapping_count += 1
    return len(manifests), sum(d["entry_count"] for d in manifests), mapping_count


def main() -> int:
    parser = argparse.ArgumentParser(prog="ods")
    sub = parser.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("inventory", help="inventory an LHA archive")
    inv.add_argument("archive", type=Path)
    inv.add_argument("--json", type=Path)
    sub.add_parser("list-archives", help="list cataloged archives")
    sub.add_parser("validate", help="validate repository catalog invariants")
    ins = sub.add_parser("inspect", help="inspect an ODS operation or historical API mapping")
    ins.add_argument("name")
    cmp = sub.add_parser("compare", help="compare historical APIs against ODS operations")
    cmp.add_argument("apis", nargs="+")
    cmp.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.command == "inventory":
        result = inspect(args.archive)
        if args.json:
            args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2)); return 0
    root = repo_root()
    if args.command == "list-archives":
        for path in sorted((root / "catalog" / "archives").glob("*.json")):
            d = json.loads(path.read_text(encoding="utf-8"))
            print(f"{d['source_filename']}: {d['entry_count']} entries {d['source_sha256'][:12]}")
        return 0
    if args.command == "validate":
        archives, entries, mappings = validate(root)
        print(f"OK: {archives} archives, {entries} entries, {mappings} semantic mappings")
        return 0
    if args.command == "inspect":
        operations = {o["id"]: o for o in load_operations(root)["operations"]}
        if args.name in operations:
            print(json.dumps(operations[args.name], indent=2)); return 0
        try:
            print(json.dumps(load_mapping(root, args.name), indent=2)); return 0
        except KeyError:
            raise SystemExit(f"unknown operation or API: {args.name}")
    if args.command == "compare":
        try:
            rows = compare(root, args.apis)
        except KeyError as exc:
            raise SystemExit(f"unknown API: {exc.args[0]}")
        if args.json:
            print(json.dumps(rows, indent=2)); return 0
        widths = {"operation": max(len("operation"), *(len(r["operation"]) for r in rows))}
        for api in args.apis:
            widths[api] = max(len(api), *(len(r[api]) for r in rows))
        print("  ".join(["operation".ljust(widths["operation"]), *(a.ljust(widths[a]) for a in args.apis)]))
        for row in rows:
            print("  ".join([row["operation"].ljust(widths["operation"]), *(row[a].ljust(widths[a]) for a in args.apis)]))
        return 0
    return 2
