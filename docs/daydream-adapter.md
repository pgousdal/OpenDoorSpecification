# DayDream reference adapter

M2.0 defines the first historical ODS adapter. `DayDreamAdapter` translates ODS
Core calls to the verified DreamDoor surface while keeping the native Amiga
library binding behind a narrow backend protocol.

| ODS operation | DreamDoor symbol |
|---|---|
| `terminal.write` | `DDPutStr` |
| `terminal.read_key` | `DDGetKey` |
| `terminal.read_line` | `Prompt` |
| `session.identity` | `GetAccount` |
| `session.time_left` | `TimeLeft` |
| `session.connection_state` | `Carrier` |
| `status.set` | `ChangeActivity` |
| `bbs.command` | `InternalCommand` |
| `lifecycle.exit` | `CloseDoor` |

`session.node` is supplied by launch context because the present evidence does
not establish a dedicated DreamDoor symbol for it. Carrier is checked before
terminal I/O and BBS commands. Loss of carrier raises the common
`DoorDisconnected` termination signal immediately.

The included recording backend is a portable test double, not an emulator of
DayDream. A later native backend will call `dddoor.library` on AmigaOS without
changing door-facing ODS code.
