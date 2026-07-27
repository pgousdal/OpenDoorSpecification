from __future__ import annotations
import argparse, json
from pathlib import Path
from .parsers.lha import inspect
from .semantic import compare, load_mapping, load_operations
from .coverage import build_coverage, write_coverage
from .simulator import load_scenario, run_scenario


def repo_root() -> Path:
    p = Path.cwd()
    for candidate in [p, *p.parents]:
        if (candidate / "catalog" / "archives").is_dir():
            return candidate
    raise SystemExit("ODS repository root not found")


def validate(root: Path, strict: bool = False) -> tuple[int, int, int]:
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
    for path in sorted((root / "catalog" / "adapters").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["operations"], path
        assert len(data["operations"]) == len(set(data["operations"])), path
        assert set(data["operations"]).issubset(operation_ids), path
    registry = json.loads((root / "catalog" / "knowledge" / "id-registry.json").read_text(encoding="utf-8"))
    registered_operations = [item["id"] for item in registry["operations"]]
    registered_apis = [item["id"] for item in registry["apis"]]
    assert len(registered_operations) == len(set(registered_operations))
    assert len(registered_apis) == len(set(registered_apis))
    assert set(registered_operations) == set(operation_ids)

    index = json.loads((root / "catalog" / "knowledge" / "operation-index.json").read_text(encoding="utf-8"))
    indexed_operations = [item["id"] for item in index["operations"]]
    assert indexed_operations == operation_ids
    assert all(item["definition_ref"] == "catalog/operations/core.json" for item in index["operations"])
    for item in index["operations"]:
        for implementation in item["implementations"]:
            assert implementation["api"] in registered_apis

    provenance_count = 0
    if strict:
        archive_entries = {
            manifest["source_filename"]: {entry["path"] for entry in manifest["entries"]}
            for manifest in manifests
        }
        provenance_ids = set()
        for path in sorted((root / "catalog" / "provenance").glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            assert record["id"] not in provenance_ids, path
            provenance_ids.add(record["id"])
            assert path.stem == record["id"], path
            assert record["status"] in {"documented", "observed", "inferred", "unknown"}, path
            if "operation" in record:
                assert record["operation"] in operation_ids, path
            if "api" in record:
                assert record["api"] in registered_apis, path
            assert record["sources"], path
            for source in record["sources"]:
                assert source["archive"] in archive_entries, path
                assert source["path"] in archive_entries[source["archive"]], path
            provenance_count += 1
        coverage = build_coverage(root)
        assert coverage["summary"]["verified_without_provenance"] == 0, "verified mappings without provenance"
        stored_coverage = json.loads((root / "catalog" / "knowledge" / "provenance-coverage.json").read_text(encoding="utf-8"))
        assert stored_coverage == coverage, "stale provenance coverage report"
    return len(manifests), sum(d["entry_count"] for d in manifests), mapping_count, provenance_count


def main() -> int:
    parser = argparse.ArgumentParser(prog="ods")
    sub = parser.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("inventory", help="inventory an LHA archive")
    inv.add_argument("archive", type=Path)
    inv.add_argument("--json", type=Path)
    sub.add_parser("list-archives", help="list cataloged archives")
    val = sub.add_parser("validate", help="validate repository catalog invariants")
    val.add_argument("--strict", action="store_true", help="also validate every provenance cross-reference")
    ins = sub.add_parser("inspect", help="inspect an ODS operation or historical API mapping")
    ins.add_argument("name")
    cmp = sub.add_parser("compare", help="compare historical APIs against ODS operations")
    cmp.add_argument("apis", nargs="+")
    cmp.add_argument("--json", action="store_true")
    cov = sub.add_parser("coverage", help="report provenance coverage for semantic mappings")
    cov.add_argument("--json", action="store_true", help="print the complete machine-readable report")
    cov.add_argument("--write", type=Path, help="write the report to a JSON file")
    sim = sub.add_parser("simulate", help="run an ODS host-adapter scenario")
    sim.add_argument("scenario", type=Path)
    sim.add_argument("--transcript", action="store_true", help="print complete JSON execution result")
    args = parser.parse_args()
    if args.command == "simulate":
        result = run_scenario(load_scenario(args.scenario))
        if args.transcript:
            print(json.dumps(result, indent=2))
        else:
            print(result["output"], end="")
            if result["termination"]:
                print(f"\n[{result['termination']['kind']}]", file=__import__("sys").stderr)
        return 0
    if args.command == "inventory":
        result = inspect(args.archive)
        if args.json:
            args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2)); return 0
    root = repo_root()
    if args.command == "coverage":
        report = write_coverage(root, args.write) if args.write else build_coverage(root)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            summary = report["summary"]
            print(f"Mappings: {summary['covered']}/{summary['total']} covered; {summary['uncovered']} uncovered")
            print(f"Verified without provenance: {summary['verified_without_provenance']}")
            for row in report["mappings"]:
                evidence = ",".join(row["evidence_statuses"]) or "missing"
                print(f"{row['api']:<12} {row['operation']:<28} {row['mapping_status']:<8} {evidence}")
        return 0
    if args.command == "list-archives":
        for path in sorted((root / "catalog" / "archives").glob("*.json")):
            d = json.loads(path.read_text(encoding="utf-8"))
            print(f"{d['source_filename']}: {d['entry_count']} entries {d['source_sha256'][:12]}")
        return 0
    if args.command == "validate":
        archives, entries, mappings, provenance = validate(root, strict=args.strict)
        suffix = f", {provenance} provenance records, strict provenance" if args.strict else ""
        print(f"OK: {archives} archives, {entries} entries, {mappings} semantic mappings{suffix}")
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
