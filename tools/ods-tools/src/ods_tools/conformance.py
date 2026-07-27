"""Executable ODS adapter conformance suite."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .adapters.daydream import DayDreamAdapter, RecordingDreamDoorBackend
from .adapters.host import DoorDisconnected, DoorExit, HostAdapter
from .profiles import load_profiles


def load_cases(root: Path) -> dict[str, Any]:
    return json.loads((root / "catalog" / "conformance" / "cases.json").read_text(encoding="utf-8"))


def _build_adapter(adapter_id: str, setup: dict[str, Any]):
    identity = dict(setup.get("identity", {"user_id": "guest", "display_name": "Guest"}))
    node = setup.get("node", 1)
    time_left = setup.get("time_left")
    connected = setup.get("connected", True)
    command_results = dict(setup.get("command_results", {}))
    if adapter_id == "host-simulator":
        adapter = HostAdapter(identity=identity, node=node, time_left=time_left, connected=connected)
        adapter.key_input.extend(setup.get("keys", []))
        adapter.line_input.extend(setup.get("lines", []))
        for name, value in command_results.items():
            adapter.register_command(name, lambda _args, result=value: result)
        return adapter
    if adapter_id == "daydream":
        backend = RecordingDreamDoorBackend(
            account=identity,
            seconds_left=time_left,
            connected=connected,
            keys=list(setup.get("keys", [])),
            lines=list(setup.get("lines", [])),
            command_results=command_results,
        )
        return DayDreamAdapter(backend=backend, node=node)
    raise KeyError(f"no executable conformance harness for adapter: {adapter_id}")


def _snapshot(adapter: Any) -> dict[str, Any]:
    if isinstance(adapter, HostAdapter):
        return {"output": list(adapter.output), "status": adapter.status_text}
    backend = adapter.backend
    return {"output": list(backend.output), "status": backend.activity}


def run_case(adapter_id: str, case: dict[str, Any]) -> dict[str, Any]:
    adapter = _build_adapter(adapter_id, case.get("setup", {}))
    expected = case["expected"]
    result: Any = None
    caught: Exception | None = None
    try:
        result = adapter.call(case["operation"], **case.get("arguments", {}))
    except (DoorExit, DoorDisconnected) as exc:
        caught = exc

    failures: list[str] = []
    expected_exception = expected.get("exception")
    if expected_exception:
        if caught is None:
            failures.append(f"expected {expected_exception}, but no exception was raised")
        elif caught.__class__.__name__ != expected_exception:
            failures.append(f"expected {expected_exception}, got {caught.__class__.__name__}")
        if "status" in expected and getattr(caught, "status", None) != expected["status"]:
            failures.append("exit status did not match")
        if "reason" in expected and getattr(caught, "reason", None) != expected["reason"]:
            failures.append("disconnect reason did not match")
    elif caught is not None:
        failures.append(f"unexpected {caught.__class__.__name__}: {caught}")
    elif result != expected.get("result"):
        failures.append(f"result mismatch: expected {expected.get('result')!r}, got {result!r}")

    state = _snapshot(adapter)
    for key in ("output", "status"):
        if key == "status" and expected_exception:
            continue
        if key in expected and state[key] != expected[key]:
            failures.append(f"{key} mismatch: expected {expected[key]!r}, got {state[key]!r}")

    return {
        "case": case["id"],
        "operation": case["operation"],
        "passed": not failures,
        "failures": failures,
    }


def build_executable_conformance_report(root: Path) -> dict[str, Any]:
    suite = load_cases(root)
    profiles = load_profiles(root)["profiles"]
    adapter_ids: list[str] = []
    for path in sorted((root / "catalog" / "adapters").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        adapter_ids.append(data.get("id", data.get("adapter")))
    adapters = []
    for adapter_id in adapter_ids:
        cases = [run_case(adapter_id, case) for case in suite["cases"]]
        by_operation = {item["operation"]: item for item in cases}
        profile_results = []
        highest = None
        for profile in profiles:
            required = profile["required_operations"]
            failed = [op for op in required if op not in by_operation or not by_operation[op]["passed"]]
            passed = not failed
            if passed:
                highest = profile["id"]
            profile_results.append({"profile": profile["id"], "passed": passed, "failed_operations": failed})
        adapters.append({
            "id": adapter_id,
            "highest_executed_profile": highest,
            "passed_cases": sum(item["passed"] for item in cases),
            "total_cases": len(cases),
            "profiles": profile_results,
            "cases": cases,
        })
    return {
        "schema_version": 1,
        "suite_version": suite["suite_version"],
        "spec_version": suite["spec_version"],
        "case_count": len(suite["cases"]),
        "adapters": adapters,
    }


def write_executable_conformance_report(root: Path, path: Path) -> dict[str, Any]:
    report = build_executable_conformance_report(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
