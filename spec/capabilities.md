# Capability Model — Draft

## Required core

- `session.identity`
- `session.node`
- `session.connection_state`
- `terminal.write`
- `terminal.read_key`
- `lifecycle.exit`
- `lifecycle.disconnect`

## Common optional capabilities

- `session.time_left`
- `terminal.read_line`
- `terminal.poll_key`
- `terminal.write_file`
- `terminal.abort_output`
- `status.set`
- `user.read`
- `file_area.read`
- `message_area.read`
- `sysop.chat`
- `storage.shared`

Exact semantics remain under study and must not be inferred from names alone.
