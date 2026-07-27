# M6.2 PR5 — FAME evidence batch

> Historical batch record: counts and queue statements describe the repository
> immediately after PR5. M6.2 is now complete.

This batch reviewed one host only: FAME DoorPort.

## Selection

FAME was selected because it had nine remaining high-priority cells and the
strongest single primary reference among the candidates. The cataloged
FAME Door-Command Guide v1.30 documents 402 public DoorPort commands, their
numeric identifiers, `FAMEDoorMsg` fields, return codes, and mandatory startup
and shutdown behavior.

Door-IO has a useful primary SDK but only six general I/O functions, so it
does not support as many remaining canonical operations. Paragon has only two
remaining cells, neither of which is established by its current cataloged
protocol evidence.

## Documentation

All mappings use:

- archive: `fcomm130.lha`;
- SHA-256:
  `9b010d4c807fe2fca82f784f2fadc31e5f21231f355c9c609a0e0db31e5462db`;
- document: `Documentation/FAMECommands.guide`;
- document version: FAME Door-Commands 1.30, dated 1998-02-01 in the guide.

The archive identity and document path are cataloged in
`catalog/archives/fcomm130.json`. The archive itself is not committed.

## Reviewed mappings

| Operation | Status | Concrete evidence | Rationale |
| --- | --- | --- | --- |
| `terminal.write` | `verified` | `NR_SendStr` command 10 and `NR_SendStrCRLF` command 11 | The commands send `IOString` to the user, with explicit CR/LF control. |
| `terminal.read_key` | `verified` | `NR_HotKey` command 15 and `AR_WaitRAWChar` command 801 | The protocol supports both nonblocking retrieval and waiting for one typed character. |
| `terminal.read_line` | `verified` | `NR_PromptChars` command 14 | The command accepts a maximum length and prompt, returns typed text, and documents a full line-editor mode. |
| `session.identity` | `verified` | `NR_Name` command 31, `NR_Location` command 33, and `NR_SlotNumber` command 36 | The commands expose the current caller's name, location, and stable user slot. |
| `session.time_left` | `verified` | `NR_TimeRemain` command 48 | The guide explicitly defines total time remaining for the user today in seconds. |
| `bbs.command` | `verified` | `CF_ExecuteCommand` command 403 and `CF_InternalCmd` command 404 | The commands execute supplied FAME menu commands. |
| `lifecycle.exit` | `verified` | `MC_ShutDown` command 2 and `MC_ShutDownLastWords` command 3 | The guide requires shutdown notification on every door exit and decrements the node's door counter. |
| `lifecycle.disconnect` | `verified` | `FAMEDoorMsg.fdom_ReturnCode` value `-2` and `MC_ShutDown` | Carrier loss is explicit; the guide mandates immediate exit with shutdown as the final command. |

No reviewed FAME mapping is partial: the selected behaviors are stated
directly by the protocol guide.

`status.set` remains `unassessed`. `SR_Status` retrieves node status, while
`AC_UserStatus` changes account state; neither establishes the canonical
host-visible activity-description operation. Unassessed does not mean
unsupported.

## Coverage and queue

| Measure | Before PR5 | After PR5 |
| --- | ---: | ---: |
| Reviewed | 42 | 50 |
| Verified | 30 | 38 |
| Partial | 12 | 12 |
| Unassessed | 48 | 40 |
| Total cells | 90 | 90 |
| Queue: high | 40 | 32 |
| Queue: medium | 6 | 6 |
| Queue: low | 2 | 2 |
| Queue: total | 48 | 40 |

The eight reviewed cells disappear from the generated queue. Queue scoring
was not changed.

## Regeneration and validation

```bash
python3 tools/generate_crosswalk.py
python3 tools/generate_crosswalk_coverage.py
python3 tools/generate_crosswalk_work_queue.py

python3 tools/generate_crosswalk.py --check
python3 tools/generate_crosswalk_coverage.py --check
python3 tools/generate_crosswalk_work_queue.py --check

PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
python3 -m unittest discover -s tests
python3 scripts/check-repository.py
```
