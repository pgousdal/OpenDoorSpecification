"""DayDream DreamDoor reference adapter.

This module models the verified ODS subset over a small backend protocol.  A
native Amiga binding can implement the same protocol using ``dddoor.library``;
tests use ``RecordingDreamDoorBackend`` so behavior is deterministic on hosts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .host import DoorDisconnected, DoorExit


class DreamDoorBackend(Protocol):
    def dd_put_str(self, text: str) -> None: ...
    def dd_get_key(self) -> str: ...
    def prompt(self, max_length: int) -> str: ...
    def get_account(self) -> dict[str, Any]: ...
    def time_left(self) -> int | None: ...
    def change_activity(self, text: str) -> None: ...
    def internal_command(self, command: str, arguments: list[Any]) -> Any: ...
    def carrier(self) -> bool: ...
    def close_door(self, status: int) -> None: ...


@dataclass
class RecordingDreamDoorBackend:
    """Portable test double matching the verified DreamDoor surface."""

    account: dict[str, Any] = field(default_factory=lambda: {"user_id": "guest", "display_name": "Guest"})
    seconds_left: int | None = None
    connected: bool = True
    keys: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    output: list[str] = field(default_factory=list)
    calls: list[dict[str, Any]] = field(default_factory=list)
    activity: str = ""
    command_results: dict[str, Any] = field(default_factory=dict)

    def _call(self, symbol: str, arguments: dict[str, Any], result: Any = None) -> Any:
        self.calls.append({"symbol": symbol, "arguments": arguments, "result": result})
        return result

    def dd_put_str(self, text: str) -> None:
        self.output.append(text); self._call("DDPutStr", {"text": text})

    def dd_get_key(self) -> str:
        if not self.keys: raise EOFError("no queued DreamDoor key input")
        return self._call("DDGetKey", {}, self.keys.pop(0))

    def prompt(self, max_length: int) -> str:
        if not self.lines: raise EOFError("no queued DreamDoor line input")
        value = self.lines.pop(0)[:max_length]
        return self._call("Prompt", {"max_length": max_length}, value)

    def get_account(self) -> dict[str, Any]:
        return self._call("GetAccount", {}, dict(self.account))

    def time_left(self) -> int | None:
        return self._call("TimeLeft", {}, self.seconds_left)

    def change_activity(self, text: str) -> None:
        self.activity = text; self._call("ChangeActivity", {"text": text})

    def internal_command(self, command: str, arguments: list[Any]) -> Any:
        result = self.command_results.get(command)
        return self._call("InternalCommand", {"command": command, "arguments": arguments}, result)

    def carrier(self) -> bool:
        return self._call("Carrier", {}, self.connected)

    def close_door(self, status: int) -> None:
        self._call("CloseDoor", {"status": status})


@dataclass
class DayDreamAdapter:
    """ODS Core 0.1 adapter for the verified DayDream DreamDoor subset."""

    backend: DreamDoorBackend
    node: int | str | None = None
    transcript: list[dict[str, Any]] = field(default_factory=list)

    operations = frozenset({
        "terminal.write", "terminal.read_key", "terminal.read_line",
        "session.identity", "session.node", "session.time_left", "session.connection_state",
        "status.set", "bbs.command", "lifecycle.exit", "lifecycle.disconnect",
    })

    def _record(self, operation: str, inputs: dict[str, Any], result: Any = None) -> Any:
        self.transcript.append({"operation": operation, "inputs": inputs, "result": result})
        return result

    def _require_carrier(self) -> None:
        if not self.backend.carrier():
            self.disconnect("carrier_lost")

    def call(self, operation: str, **kwargs: Any) -> Any:
        methods = {
            "terminal.write": self.write, "terminal.read_key": self.read_key,
            "terminal.read_line": self.read_line, "session.identity": self.get_identity,
            "session.node": self.get_node, "session.time_left": self.get_time_left,
            "session.connection_state": self.connection_state, "status.set": self.set_status,
            "bbs.command": self.bbs_command, "lifecycle.exit": self.exit,
            "lifecycle.disconnect": self.disconnect,
        }
        if operation not in methods: raise KeyError(f"unsupported ODS operation: {operation}")
        return methods[operation](**kwargs)

    def write(self, data: Any) -> None:
        self._require_carrier(); text = str(data); self.backend.dd_put_str(text); self._record("terminal.write", {"data": text})

    def read_key(self) -> str:
        self._require_carrier(); return self._record("terminal.read_key", {}, self.backend.dd_get_key())

    def read_line(self, max_length: int = 255) -> str:
        self._require_carrier()
        if max_length < 0: raise ValueError("max_length must be non-negative")
        return self._record("terminal.read_line", {"max_length": max_length}, self.backend.prompt(max_length))

    def get_identity(self) -> dict[str, Any]:
        return self._record("session.identity", {}, self.backend.get_account())

    def get_node(self) -> int | str | None:
        return self._record("session.node", {}, self.node)

    def get_time_left(self) -> int | None:
        return self._record("session.time_left", {}, self.backend.time_left())

    def connection_state(self) -> str:
        state = "connected" if self.backend.carrier() else "disconnected"
        return self._record("session.connection_state", {}, state)

    def set_status(self, text: str) -> None:
        text = str(text); self.backend.change_activity(text); self._record("status.set", {"text": text})

    def bbs_command(self, command: str, arguments: list[Any] | None = None) -> Any:
        self._require_carrier(); args = list(arguments or [])
        return self._record("bbs.command", {"command": command, "arguments": args}, self.backend.internal_command(command, args))

    def exit(self, status: int = 0) -> None:
        self.backend.close_door(status); self._record("lifecycle.exit", {"status": status}); raise DoorExit(status)

    def disconnect(self, reason: str = "carrier_lost") -> None:
        self._record("lifecycle.disconnect", {"reason": reason}); raise DoorDisconnected(reason)
