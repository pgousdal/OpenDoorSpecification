# M6.2 PR9 — AmBoS high-confidence evidence batch

> Historical batch record: counts and triage statements describe the repository
> immediately after PR9. M6.2 is now complete.

This batch reviewed exactly the two AmBoS cells that the PR8 triage classified
as `small` research effort and `high` confidence: `lifecycle.exit` and
`session.identity`.

## Selection

Both cells reuse the cataloged AmBoS developer archive and are directly
documented by its programmer guide, public headers, and original example
source. No other remaining AmBoS cell had the same triage combination. The
other three AmBoS cells remain unassessed.

## Evidence consulted

- archive: `AmBoS_doc_dev.lha`;
- SHA-256:
  `1785840c7dc5303bc3d59accdf1250ce003af36bcfd3804917a25207f7259b27`;
- programmer guide: `Dokumentation/BBS.lib.guide`;
- public headers:
  `Dokumentation/include/clib/BBS_protos.h` and
  `Dokumentation/include/libraries/BBS_library.h`;
- original SDK example: `Dokumentation/Source/Beispiel.c`.

The archive identity, hash, and paths are recorded in
`catalog/archives/AmBoS_doc_dev.json`. The archive itself is not committed.

## Reviewed mappings

| Host and operation | Status | Concrete evidence | Rationale |
| --- | --- | --- | --- |
| `ambos:lifecycle.exit` | `verified` | The guide requires `bbs_close` before exit to unregister the external program and return port control to AmBoS; the public prototype and example confirm the call. | `bbs_close` is the documented normal-exit operation. |
| `ambos:session.identity` | `verified` | The guide says `bbs_open` returns `ExternInfo`; the public structure defines `UserName` and `City`; the example reads those fields for the current caller. | The returned structure directly supplies current-session identity. |

Neither mapping has a known limitation against its canonical operation, so
both are `verified`. No inference from an undocumented symbol or behavior is
used.

## Coverage, queue, and triage

| Measure | Before PR9 | After PR9 |
| --- | ---: | ---: |
| Reviewed | 56 | 58 |
| Verified | 43 | 45 |
| Partial | 13 | 13 |
| Unassessed | 34 | 32 |
| Total cells | 90 | 90 |
| Queue: high | 27 | 25 |
| Queue: medium | 5 | 5 |
| Queue: low | 2 | 2 |
| Queue: total | 34 | 32 |
| Triage: total | 34 | 32 |
| Triage: `documented-but-not-reviewed` | 2 | 0 |
| Triage effort: `small` | 2 | 0 |
| Triage confidence: `high` | 2 | 0 |

The same two stable IDs disappear from both generated artifacts. Queue scoring
and triage vocabularies are unchanged. The remaining AmBoS work is categorized
as `insufficient-semantics` or `insufficient-sdk`, with moderate or extensive
research effort.

## Regeneration and validation

```bash
python3 tools/generate_crosswalk.py
python3 tools/generate_crosswalk_coverage.py
python3 tools/generate_crosswalk_work_queue.py
python3 tools/generate_crosswalk_triage.py

python3 tools/generate_crosswalk.py --check
python3 tools/generate_crosswalk_coverage.py --check
python3 tools/generate_crosswalk_work_queue.py --check
python3 tools/generate_crosswalk_triage.py --check

PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
python3 -m unittest discover -s tests
python3 scripts/check-repository.py
```
