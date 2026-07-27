# M6.2 PR7 — Small evidence harvest

M6.2 remains in progress. This intentionally small batch reviews two lifecycle
operations for `door-io`.

## Selection

The Door-IO lifecycle cells form the smallest coherent group in the remaining
queue with direct, reusable primary evidence. The same `door_io12.lha` SDK
manual and public header document:

- registration of a carrier-loss callback;
- the callback's required interface and resource cleanup;
- an explicit carrier-loss result from character input;
- `BOX_stop` as the required normal-exit teardown call.

The remaining Door-IO cells—`session.identity`, `session.time_left`,
`status.set`, and `bbs.command`—are not exposed by the six-function library
contract and remain unassessed.

## Documentation

All evidence uses the cataloged SDK:

- archive: `door_io12.lha`;
- SHA-256:
  `a5e639b6e785d158c4c318aac087e7e47b4b4553a7609c364f5044e57a41a7a1`;
- programmer manual: `doorio/door_io.doc`;
- public header: `doorio/door_io.h`;
- function descriptor: `doorio/door_io.fd`.

The archive identity and referenced paths are recorded in
`catalog/archives/door_io12.json`. The archive itself is not committed.

## Reviewed mappings

| Host and operation | Status | Concrete evidence | Rationale and limitations |
| --- | --- | --- | --- |
| `door-io:lifecycle.disconnect` | `verified` | `BOX_start`, `carrier_lost_hook`, `BOX_stop`, `BOX_wgetchar` | The library reports carrier loss and defines an immediate callback that stops the interface and releases resources. |
| `door-io:lifecycle.exit` | `partial` | `BOX_stop` in the manual, header, and function descriptor | The SDK requires interface teardown when the program quits, but does not document exit-status propagation or explicit host acknowledgement. |

The partial mapping is not an unsupported classification. It records the
documented cleanup portion while preserving the missing lifecycle details.

## Coverage and queue

| Measure | Before PR7 | After PR7 |
| --- | ---: | ---: |
| Reviewed | 54 | 56 |
| Verified | 42 | 43 |
| Partial | 12 | 13 |
| Unassessed | 36 | 34 |
| Total cells | 90 | 90 |
| Queue: high | 29 | 27 |
| Queue: medium | 5 | 5 |
| Queue: low | 2 | 2 |
| Queue: total | 36 | 34 |

Only the two declared Door-IO cells disappear from the queue. Queue scoring
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
