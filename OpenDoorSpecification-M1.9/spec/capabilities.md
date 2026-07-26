# ODS Core capabilities 0.1

The normative operation catalog is `catalog/operations/core.json`.

## Required core

- `session.identity`
- `session.node`
- `session.connection_state`
- `terminal.write`
- `terminal.read_key`
- `lifecycle.exit`
- `lifecycle.disconnect`

## Optional in 0.1

- `session.time_left`
- `terminal.read_line`
- `status.set`
- `bbs.command`

Capability discovery returns support state, not merely a host-family name. A `partial`
historical mapping is research metadata and does not by itself establish conforming runtime
support.
