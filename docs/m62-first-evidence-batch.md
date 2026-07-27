# M6.2 PR2 — First crosswalk evidence expansion batch

This batch resolves eight foundational crosswalk cells backed by original SDK
documentation, headers, declarations, and example source already cataloged by
the repository. The selection favors a coherent terminal/session/lifecycle
group and deliberately leaves higher-scoring but ambiguous cells unassessed.

`partial` remains a reviewed mapping with a documented limitation; it does not
mean unsupported. Work-queue priority remains a research-order recommendation,
not evidence that support exists.

## Reviewed cells

| Host | Operation | Status | Primary evidence | Rationale and caveat |
| --- | --- | --- | --- | --- |
| ABBS | `lifecycle.disconnect` | `partial` | `ABBS320_999.lha`: `ABBS/Docs/abbsrexx.doc`, `GETCONSTAT` | Reports connection status, but the door must perform prompt termination. |
| AmBoS | `terminal.read_key` | `partial` | `AmBoS_doc_dev.lha`: `Dokumentation/BBS.lib.guide` and `Dokumentation/include/fd/BBS_library.fd`, `bbs_getc`/`bbs_Wgetc` | Character input is documented; return encoding and disconnect signaling remain unnormalized. |
| AmBoS | `terminal.read_line` | `partial` | Same guide and FD file, `bbs_gets`/`bbs_sgets`/`bbs_Wgets` | Bounded string input is documented; editing modes and disconnect signaling need further review. |
| DayDream | `lifecycle.exit` | `verified` | `DayDreamBBSDev.lha`: DreamDoor documentation and `clib/dddoor_protos.h`, `CloseDoor` | The documented close operation completes a door and returns control to the host. |
| UCDoor | `terminal.write` | `verified` | `ucdoor10.lha`: `UCDoor_V1.0.guide` and `html/cdputstr.htm`, `cd_PutStr` | The SDK’s callable terminal string-output operation fully covers canonical output. |
| UCDoor | `terminal.read_line` | `partial` | Guide plus `html/cdgetstr.htm` and `html/getstrpr.htm`, `cd_GetStr`/`cd_GetStrPrompt` | String input exists, but extracted evidence does not fully establish editing, bounds, or disconnect behavior. |
| UCDoor | `session.time_left` | `partial` | `include/ucdoor.h`, `UDC_TIMELEFT`; `demo/cd_test1.c`, `cd_GetNumInfo` | Remaining time is explicit, but the SDK reports minutes and ODS requires seconds. |
| UCDoor | `lifecycle.disconnect` | `verified` | Guide, `html/carrier.htm`, and `demo/cd_test1.c`, `cd_CarrierLost` plus `cd_End(ERROR_CARRIER)` | The documented sequence detects carrier loss and terminates with its explicit reason. |

Every generated cell carries its archive, internal path, concrete symbol,
mapping rationale, and limitations. References resolve against
`catalog/archives/*.json`.

## Coverage and queue impact

| Metric | Before PR2 | After PR2 |
| --- | ---: | ---: |
| Total cells | 90 | 90 |
| Reviewed | 26 | 34 |
| Verified | 20 | 23 |
| Partial | 6 | 11 |
| Unassessed / queued | 64 | 56 |
| Queue high | 52 | 46 |
| Queue medium | 6 | 6 |
| Queue low | 6 | 4 |

The changed priority distribution is expected because operation prevalence and
same-family reviewed evidence are inputs to the deterministic queue score.

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
```

M6.2 remains in progress. The remaining 56 cells require separate evidence
review; none is classified as unsupported by this batch.
