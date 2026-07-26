# Reference host adapter

ODS M1.9 introduces a deterministic in-memory adapter for ODS Core 0.1. It is a
reference and conformance implementation, not an emulation of any historical
BBS.

## Purpose

The adapter lets door logic be exercised before an ABBS, DayDream, Paragon, or
other native adapter exists. It records every operation, accepts queued input,
and captures terminal output without using a real terminal or BBS process.

## Lifecycle behavior

`lifecycle.exit` raises `DoorExit` and records the requested status.
`lifecycle.disconnect` raises `DoorDisconnected`. Any terminal or host-command
operation attempted after carrier loss also surfaces `DoorDisconnected`
immediately. This is the reference behavior for the ODS requirement that a door
must terminate promptly when its connection is no longer usable.

## CLI simulator

Run a checked-in scenario from the repository root:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools simulate \
  examples/host-simulator/hello.json
```

Use `--transcript` to print the complete machine-readable result:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools simulate \
  examples/host-simulator/hello.json --transcript
```

A scenario contains optional session data and queued input followed by an
ordered array of ODS calls. The format is described by
`schemas/host-scenario.schema.json`.

## Host commands

`bbs.command` is deny-by-default. A command must be registered explicitly by
name. The JSON simulator exposes deterministic return values through
`command_results`; it does not execute shell commands.
