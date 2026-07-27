# M6.2 PR6 — UCDoor evidence batch

M6.2 remains in progress. This batch reviews one host only: the UCDoor
compatibility wrapper for MAXs BBS doors.

## Selection

UCDoor was selected after comparing every remaining host:

| Candidate | Queue position | Primary-evidence assessment |
| --- | --- | --- |
| UCDoor | three high and two medium cells | One complete SDK archive directly supports four remaining operations through its guide, public header, and original demo. |
| Door-IO | six high cells | Its six-function SDK directly adds lifecycle cleanup and carrier handling, but no session, BBS-command, or status operations. |
| AmBoS | five high cells | Its programmer guide directly adds caller identity and clean library shutdown; other remaining operations are not established. |
| ABBS | two high cells | Existing documentation is strong, but the two remaining canonical operations require further targeted review. |
| Paragon | two high cells | Current protocol evidence does not directly establish remaining time or status mutation. |
| WWBBS and Zeus | six high cells each | The catalog contains observed doors rather than a complete SDK contract. |

AEDoor and FAME each have one intentionally unassessed status cell. DayDream
has no queue items.

UCDoor therefore offered the largest directly supportable batch from one
primary documentation set.

## Documentation

All mappings use the cataloged `ucdoor10.lha` SDK:

- SHA-256:
  `a895ce805c98a38b7c33830bd30fa71a68f8cfbe1a89863735aa3565462ef05e`;
- programmer guide: `ucdoor/guide/UCDoor_V1.0.guide`;
- public header: `ucdoor/include/ucdoor.h`;
- original example: `ucdoor/demo/cd_test1.c`;
- HTML function references under `ucdoor/html/`.

The archive identity and every referenced path are recorded in
`catalog/archives/ucdoor10.json`. The archive itself is not committed.

## Reviewed mappings

| Operation | Status | Concrete evidence | Rationale |
| --- | --- | --- | --- |
| `terminal.read_key` | `verified` | `cd_GetChar`, `cd_GetCharPrompt`; guide, HTML reference, and demo | The SDK exposes callable single-character input with optional prompting. |
| `session.identity` | `verified` | `cd_GetStrInfo`, `UDC_USERNAME`, `cd_GetUserIndex`; guide, header, and demo | The current caller's username is directly retrievable, with documented stable user-index lookup. |
| `bbs.command` | `verified` | `cd_DoFunction`; guide, HTML reference, and header | The SDK explicitly defines the call as performing a function from the MAX menu configuration. |
| `lifecycle.exit` | `verified` | `cd_Main`, `cd_Door`, `OK`; guide, HTML reference, and demo | Returning from the door callback through `cd_Main` is the documented normal completion path. |

No new partial mapping was necessary: each selected operation is directly
described by the SDK.

`status.set` remains `unassessed`. The SDK includes terminal-color and
user-data mutation calls but no documented operation for setting the
host-visible activity description. Unassessed does not mean unsupported.

## Coverage and queue

| Measure | Before PR6 | After PR6 |
| --- | ---: | ---: |
| Reviewed | 50 | 54 |
| Verified | 38 | 42 |
| Partial | 12 | 12 |
| Unassessed | 40 | 36 |
| Total cells | 90 | 90 |
| Queue: high | 32 | 29 |
| Queue: medium | 6 | 5 |
| Queue: low | 2 | 2 |
| Queue: total | 40 | 36 |

The four reviewed cells disappear from the generated queue. Queue scoring was
not changed.

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
