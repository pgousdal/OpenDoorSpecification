from __future__ import annotations
import argparse, json
from pathlib import Path
from .parsers.lha import inspect
from .semantic import compare, load_mapping, load_operations
from .coverage import build_coverage, write_coverage
from .operations import build_operation_records, write_operation_records
from .gaps import build_adapter_gap_report, write_adapter_gap_report
from .profiles import build_conformance_report, write_conformance_report
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
        generated_records = build_operation_records(root)
        operation_dir = root / "catalog" / "knowledge" / "operations"
        stored_index = json.loads((operation_dir / "index.json").read_text(encoding="utf-8"))
        assert [item["id"] for item in stored_index["operations"]] == operation_ids, "stale operation record index"
        for record in generated_records["operations"]:
            path = operation_dir / (record["id"].replace(".", "-") + ".json")
            assert json.loads(path.read_text(encoding="utf-8")) == record, f"stale operation record: {record['id']}"
        gap_report = build_adapter_gap_report(root)
        stored_gap_report = json.loads((root / "catalog" / "knowledge" / "adapter-gap-report.json").read_text(encoding="utf-8"))
        assert stored_gap_report == gap_report, "stale adapter gap report"
        conformance_report = build_conformance_report(root)
        profile_ids = [item["id"] for item in conformance_report["profiles"]]
        profile_levels = [item["level"] for item in conformance_report["profiles"]]
        assert len(profile_ids) == len(set(profile_ids)), "duplicate conformance profile ID"
        assert profile_levels == sorted(profile_levels), "conformance profiles must be level-ordered"
        previous_required = set()
        for profile in conformance_report["profiles"]:
            required = profile["required_operations"]
            assert len(required) == len(set(required)), f"duplicate operation in profile: {profile['id']}"
            assert set(required).issubset(operation_ids), f"unknown operation in profile: {profile['id']}"
            assert previous_required.issubset(required), f"non-cumulative profile: {profile['id']}"
            previous_required = set(required)
        for adapter in conformance_report["adapters"]:
            assert not adapter["unknown_operations"], f"unknown adapter operations: {adapter['id']}"
        stored_conformance = json.loads((root / "catalog" / "knowledge" / "conformance-report.json").read_text(encoding="utf-8"))
        assert stored_conformance == conformance_report, "stale conformance report"
    return len(manifests), sum(d["entry_count"] for d in manifests), mapping_count, provenance_count


def _format_operation_record(record: dict) -> str:
    lines = [record["id"], record["definition"]["summary"]]
    lines.append(f"stability: {record['definition']['stability']}")
    lines.append("historical implementations:")
    if record["historical_implementations"]:
        for item in record["historical_implementations"]:
            evidence = ",".join(item["evidence_statuses"]) or "missing"
            lines.append(f"  {item['api']}: {', '.join(item['symbols'])} [{item['status']}; {evidence}]")
    else:
        lines.append("  none")
    lines.append("adapters:")
    for adapter in record["adapter_status"]:
        state = "supported" if adapter["supported"] else "unsupported"
        lines.append(f"  {adapter['adapter']}: {state} ({adapter['conformance']})")
    return "\n".join(lines)



def _format_gap_target(target: dict) -> str:
    lines = [f"{target['id']} ({target['kind']})"]
    for row in target['rows']:
        symbols = f" — {', '.join(row.get('symbols', []))}" if row.get('symbols') else ""
        lines.append(f"  {row['operation']:<28} {row['status']}{symbols}")
    summary = target['summary']
    lines.append(f"summary: {summary['supported']} supported, {summary['partial']} partial, {summary['missing']} missing")
    return "\n".join(lines)


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
    gaps = sub.add_parser("gaps", help="report historical API and adapter operation gaps")
    gaps.add_argument("target", nargs="?", help="historical API or adapter ID")
    gaps.add_argument("--json", action="store_true", help="print machine-readable JSON")
    gaps.add_argument("--write", type=Path, help="write the report to a JSON file")
    profiles = sub.add_parser("profiles", help="list conformance profiles or evaluate an adapter")
    profiles.add_argument("name", nargs="?", help="profile ID or adapter ID")
    profiles.add_argument("--json", action="store_true", help="print machine-readable JSON")
    profiles.add_argument("--write", type=Path, help="write the conformance report to a JSON file")
    ops = sub.add_parser("operations", help="list or inspect canonical operation records")
    ops.add_argument("operation", nargs="?", help="operation ID to inspect")
    ops.add_argument("--json", action="store_true", help="print machine-readable JSON")
    ops.add_argument("--write", type=Path, help="regenerate operation records in a directory")
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
    if args.command == "gaps":
        report = write_adapter_gap_report(root, args.write) if args.write else build_adapter_gap_report(root)
        targets = [*report["historical_apis"], *report["adapters"]]
        if args.target:
            if args.target.startswith("api:"):
                matches = [item for item in report["historical_apis"] if item["id"] == args.target[4:]]
            elif args.target.startswith("adapter:"):
                matches = [item for item in report["adapters"] if item["id"] == args.target[8:]]
            else:
                matches = [item for item in targets if item["id"] == args.target]
            if not matches:
                raise SystemExit(f"unknown API or adapter: {args.target}")
            if len(matches) > 1:
                raise SystemExit(f"ambiguous target: {args.target}; use api:{args.target} or adapter:{args.target}")
            target = matches[0]
            print(json.dumps(target, indent=2) if args.json else _format_gap_target(target))
        elif args.json:
            print(json.dumps(report, indent=2))
        else:
            print("target                       kind                 supported partial missing")
            for item in targets:
                summary = item["summary"]
                print(f"{item['id']:<28} {item['kind']:<20} {summary['supported']:<9} {summary['partial']:<7} {summary['missing']}")
        return 0
    if args.command == "profiles":
        report = write_conformance_report(root, args.write) if args.write else build_conformance_report(root)
        if args.name:
            profile = next((item for item in report["profiles"] if item["id"] == args.name), None)
            adapter = next((item for item in report["adapters"] if item["id"] == args.name), None)
            if profile is None and adapter is None:
                raise SystemExit(f"unknown profile or adapter: {args.name}")
            item = profile if profile is not None else adapter
            if args.json:
                print(json.dumps(item, indent=2))
            elif profile is not None:
                print(profile["id"])
                print(profile["summary"])
                print(f"required operations: {len(profile['required_operations'])}")
                for operation in profile["required_operations"]:
                    print(f"  {operation}")
            else:
                print(f"{adapter['id']}: highest profile = {adapter['highest_profile'] or 'none'}")
                for result in adapter["profiles"]:
                    state = "PASS" if result["passed"] else "FAIL"
                    print(f"  {result['profile']:<12} {state} ({result['supported_required_count']}/{result['required_count']})")
                    for operation in result["missing_required_operations"]:
                        print(f"    missing: {operation}")
        elif args.json:
            print(json.dumps(report, indent=2))
        else:
            print("profiles:")
            for profile in report["profiles"]:
                print(f"  {profile['id']:<12} {len(profile['required_operations'])} required — {profile['summary']}")
            print("adapters:")
            for adapter in report["adapters"]:
                print(f"  {adapter['id']:<20} {adapter['highest_profile'] or 'none'}")
        return 0
    if args.command == "operations":
        result = write_operation_records(root, args.write) if args.write else build_operation_records(root)
        records = result["operations"]
        if args.operation:
            record = next((item for item in records if item["id"] == args.operation), None)
            if record is None:
                raise SystemExit(f"unknown operation: {args.operation}")
            print(json.dumps(record, indent=2) if args.json else _format_operation_record(record))
        elif args.json:
            print(json.dumps(result, indent=2))
        else:
            for record in records:
                summary = record["summary"]
                print(f"{record['id']:<28} historical={summary['historical_implementation_count']:<2} adapters={summary['adapter_count']}")
        return 0
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
