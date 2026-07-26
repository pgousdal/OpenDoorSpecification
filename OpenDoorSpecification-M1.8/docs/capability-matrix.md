# Capability matrix — M1.7

| Capability | ABBS | Paragon | DayDream | AmBoS | AEDoor | door_io | FAME |
|---|---|---|---|---|---|---|---|
| terminal.write | verified | unknown | verified | verified | unknown | verified | unknown |
| terminal.read_key | verified | unknown | verified | unknown | unknown | verified | unknown |
| terminal.read_line | verified | unknown | verified | unknown | unknown | verified | unknown |
| session.user | verified | unknown | verified | unknown | unknown | unknown | unknown |
| session.time | verified | unknown | verified | unknown | unknown | unknown | unknown |
| lifecycle.disconnect | unknown | verified | verified | verified | unknown | unknown | unknown |
| bbs.command | unknown | unknown | verified | unknown | unknown | unknown | unknown |
| bbs.status | verified | unknown | verified | unknown | unknown | unknown | unknown |
| bbs.message | unknown | verified | verified | unknown | unknown | unknown | unknown |
| bbs.files | unknown | unknown | verified | unknown | unknown | unknown | unknown |

`verified` means at least one extracted symbol matched the conservative capability rule. `unknown` does not mean unsupported.
