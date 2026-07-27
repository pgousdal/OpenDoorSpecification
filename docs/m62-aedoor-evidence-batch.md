# M6.2 PR4 — AEDoor evidence batch

M6.2 remains in progress. This batch reviews one host only: AEDoor.

## Selection

AEDoor was selected from the high-priority queue because it had nine
high-priority cells and an official, cataloged SDK archive with a programmer
guide, protocol command reference, public headers, and working examples. The
same primary source therefore supports a coherent group of terminal, session,
BBS-command, and lifecycle operations.

The catalog records `aedoor28.lha` with SHA-256
`222e474cf5f9181c25443bd0e754d2a38fda215ffdcc2b5b130476292b98d3fc`.
The archive itself is not committed.

## Reviewed mappings

| Operation | Status | Concrete evidence | Rationale and limitations |
| --- | --- | --- | --- |
| `terminal.write` | `verified` | `WriteStr` and `JH_WRITE` in `Docs/AEDoor.doc`, `doordocs`, and `SAS_C/Examples/Simple/simple.c` | The SDK documents and demonstrates terminal string output. |
| `terminal.read_key` | `verified` | `Hotkey` and `JH_HK` in `Docs/AEDoor.doc`, `doordocs`, and `SAS_C/Include/clib/aedoor_protos.h` | The call waits for one key and returns its character value. |
| `terminal.read_line` | `verified` | `Prompt`, `GetStr`, `JH_PM`, and `JH_LI` in the programmer guide, command reference, and example | The calls provide bounded, edited line input and expose connection failure. |
| `session.identity` | `verified` | `GetDT`, `DT_NAME`, `DT_SLOTNUMBER`, and `DT_LOCATION` in the guide, command reference, and example | The documented fields expose caller identity, including a stable user slot. |
| `session.time_left` | `verified` | `GetDT` and `DT_TIMETOTAL` in `Docs/AEDoor.doc`, `doordocs`, and `SAS_C/Include/libraries/aedoor.h` | `DT_TIMETOTAL` is documented as remaining user time in seconds. |
| `bbs.command` | `verified` | `SendStrCmd` and `PRV_COMMAND` in `doordocs` and the public headers | Command 508 executes the supplied internal AmiExpress menu command. |
| `lifecycle.exit` | `verified` | `DeleteComm` and `JH_SHUTDOWN` in the guide, command reference, header, and example | The documented shutdown call releases the channel and tells AmiExpress that the door finished. |
| `lifecycle.disconnect` | `partial` | Carrier-loss results from `Prompt`, `GetStr`, and `Hotkey`, demonstrated in `simple.c` | AEDoor reliably reports lost carrier, but the SDK leaves termination policy and timing to the door. |

`status.set` remains `unassessed`. The archive contains nearby status-related
symbols, but the reviewed material does not establish the canonical
host-visible activity-description operation. High priority is a research-order
recommendation, not a support claim.

## Coverage and queue

| Measure | Before PR4 | After PR4 |
| --- | ---: | ---: |
| Reviewed | 34 | 42 |
| Verified | 23 | 30 |
| Partial | 11 | 12 |
| Unassessed | 56 | 48 |
| Total cells | 90 | 90 |
| Queue: high | 46 | 40 |
| Queue: medium | 6 | 6 |
| Queue: low | 4 | 2 |
| Queue: total | 56 | 48 |

The eight reviewed cells disappear from the generated queue. Priority changes
for remaining cells are expected because queue scoring considers related
reviewed operations; no scoring rule changed in this PR.

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
```
