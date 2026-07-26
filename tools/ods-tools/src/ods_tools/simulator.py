"""JSON-driven execution support for the ODS host adapter."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .adapters.host import DoorDisconnected, DoorExit, HostAdapter


def load_scenario(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("actions"), list):
        raise ValueError("scenario must be an object containing an actions array")
    return data


def run_scenario(data: dict[str, Any]) -> dict[str, Any]:
    session = data.get("session", {})
    inputs = data.get("inputs", {})
    adapter = HostAdapter(
        identity=dict(session.get("identity", {"user_id": "guest", "display_name": "Guest"})),
        node=session.get("node", 1),
        time_left=session.get("time_left"),
        connected=session.get("connected", True),
    )
    adapter.key_input.extend(inputs.get("keys", []))
    adapter.line_input.extend(inputs.get("lines", []))

    command_results = data.get("command_results", {})
    for name, result in command_results.items():
        adapter.register_command(name, lambda _args, value=result: value)

    termination: dict[str, Any] | None = None
    for action in data["actions"]:
        if not isinstance(action, dict) or "operation" not in action:
            raise ValueError("every action must contain an operation")
        try:
            adapter.call(action["operation"], **action.get("arguments", {}))
        except DoorExit as exc:
            termination = {"kind": "exit", "status": exc.status}
            break
        except DoorDisconnected as exc:
            termination = {"kind": "disconnect", "reason": exc.reason}
            break

    return {
        "output": "".join(adapter.output),
        "output_chunks": adapter.output,
        "status": adapter.status_text,
        "connection_state": "connected" if adapter.connected else "disconnected",
        "termination": termination,
        "transcript": adapter.transcript,
    }
