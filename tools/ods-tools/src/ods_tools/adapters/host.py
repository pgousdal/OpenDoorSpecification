"""Deterministic host adapter for exercising ODS Core operations.

The adapter is intentionally small and contains no BBS-specific behavior.  It
provides a reproducible environment for door examples, conformance tests, and
future historical adapters.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable


class DoorExit(RuntimeError):
    """Raised when a door invokes ``lifecycle.exit``."""

    def __init__(self, status: int = 0):
        super().__init__(f"door exited with status {status}")
        self.status = status


class DoorDisconnected(RuntimeError):
    """Raised when carrier loss must terminate the door promptly."""

    def __init__(self, reason: str = "carrier_lost"):
        super().__init__(reason)
        self.reason = reason


@dataclass
class HostAdapter:
    """In-memory reference implementation of ODS Core 0.1.

    Input is pre-seeded, output and operation calls are recorded, and host
    commands must be explicitly registered.  This makes executions fully
    deterministic and safe for tests.
    """

    identity: dict[str, Any] = field(default_factory=lambda: {"user_id": "guest", "display_name": "Guest"})
    node: int | str = 1
    time_left: int | None = None
    connected: bool = True
    key_input: deque[str] = field(default_factory=deque)
    line_input: deque[str] = field(default_factory=deque)
    output: list[str] = field(default_factory=list)
    transcript: list[dict[str, Any]] = field(default_factory=list)
    status_text: str = ""
    command_handlers: dict[str, Callable[[list[Any]], Any]] = field(default_factory=dict)

    def _record(self, operation: str, inputs: dict[str, Any], result: Any = None) -> Any:
        self.transcript.append({"operation": operation, "inputs": inputs, "result": result})
        return result

    def _require_connection(self) -> None:
        if not self.connected:
            self.disconnect("carrier_lost")

    def call(self, operation: str, **kwargs: Any) -> Any:
        """Dispatch one ODS operation by its normative identifier."""
        methods = {
            "terminal.write": self.write,
            "terminal.read_key": self.read_key,
            "terminal.read_line": self.read_line,
            "session.identity": self.get_identity,
            "session.node": self.get_node,
            "session.time_left": self.get_time_left,
            "session.connection_state": self.connection_state,
            "status.set": self.set_status,
            "bbs.command": self.bbs_command,
            "lifecycle.exit": self.exit,
            "lifecycle.disconnect": self.disconnect,
        }
        try:
            method = methods[operation]
        except KeyError as exc:
            raise KeyError(f"unsupported ODS operation: {operation}") from exc
        return method(**kwargs)

    def write(self, data: Any) -> None:
        self._require_connection()
        text = str(data)
        self.output.append(text)
        self._record("terminal.write", {"data": text})

    def read_key(self) -> str:
        self._require_connection()
        if not self.key_input:
            raise EOFError("host simulator has no queued key input")
        return self._record("terminal.read_key", {}, self.key_input.popleft())

    def read_line(self, max_length: int = 255) -> str:
        self._require_connection()
        if max_length < 0:
            raise ValueError("max_length must be non-negative")
        if self.line_input:
            value = self.line_input.popleft()
        else:
            chars: list[str] = []
            while self.key_input and len(chars) < max_length:
                char = self.key_input.popleft()
                if char in {"\r", "\n"}:
                    break
                chars.append(char)
            if not chars and not self.key_input:
                raise EOFError("host simulator has no queued line input")
            value = "".join(chars)
        value = value[:max_length]
        return self._record("terminal.read_line", {"max_length": max_length}, value)

    def get_identity(self) -> dict[str, Any]:
        return self._record("session.identity", {}, dict(self.identity))

    def get_node(self) -> int | str:
        return self._record("session.node", {}, self.node)

    def get_time_left(self) -> int | None:
        return self._record("session.time_left", {}, self.time_left)

    def connection_state(self) -> str:
        state = "connected" if self.connected else "disconnected"
        return self._record("session.connection_state", {}, state)

    def set_status(self, text: str) -> None:
        self.status_text = str(text)
        self._record("status.set", {"text": self.status_text})

    def register_command(self, command: str, handler: Callable[[list[Any]], Any]) -> None:
        if not command:
            raise ValueError("command name must not be empty")
        self.command_handlers[command] = handler

    def bbs_command(self, command: str, arguments: list[Any] | None = None) -> Any:
        self._require_connection()
        args = list(arguments or [])
        try:
            handler = self.command_handlers[command]
        except KeyError as exc:
            raise KeyError(f"unregistered host command: {command}") from exc
        result = handler(args)
        return self._record("bbs.command", {"command": command, "arguments": args}, result)

    def exit(self, status: int = 0) -> None:
        self._record("lifecycle.exit", {"status": status})
        raise DoorExit(status)

    def disconnect(self, reason: str = "carrier_lost") -> None:
        self.connected = False
        self._record("lifecycle.disconnect", {"reason": reason})
        raise DoorDisconnected(reason)
