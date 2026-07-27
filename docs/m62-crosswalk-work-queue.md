# M6.2 Crosswalk evidence work queue

The generated work queue turns every M6.1 `unassessed` host-operation cell into
one deterministic research task. It helps contributors select work without
misrepresenting missing research as missing support:

- `unassessed` does not mean unsupported;
- `partial` does not mean unsupported;
- priority is a research-order recommendation, not a support claim or an
  estimate of support likelihood.

The machine-readable artifact is
`catalog/crosswalk/work-queue.json`. Each item has the stable ID
`<host-id>:<canonical-operation-id>`, host metadata, its unchanged
`unassessed` status, a priority, and human-readable reasons.

## Priority calculation

The generator assigns fixed scores from committed evidence:

| Signal | Points |
| --- | ---: |
| Host evidence class is `documented-sdk` or `documented-protocol` | 3 |
| Operation has reviewed mappings in at least three other hosts | 3 |
| Operation has one or two reviewed mappings in other hosts | 1 |
| Host has a reviewed operation in the same canonical family | 2 |
| Operation is foundational terminal I/O, session identity, or lifecycle exit/disconnect | 2 |
| Host already has cataloged census entries or archives | 1 |

Scores of 5 or more are `high`, scores of 2–4 are `medium`, and lower scores
are `low`. Every emitted signal becomes a reason on the item. With equal
priority, items sort lexically by their stable ID; priorities sort
`high`, `medium`, then `low`.

These rules identify promising research paths only. They do not imply that a
mapping exists.

## Generate and validate

```bash
python3 tools/generate_crosswalk_work_queue.py
python3 tools/generate_crosswalk_work_queue.py --check
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
```

The generator produces byte-identical JSON from unchanged source data.
`--check` fails if the committed artifact is missing or stale. Strict
repository validation also rejects a missing or stale queue.

## Select research work

```bash
ods crosswalk --work-queue
ods crosswalk --work-queue --json
ods crosswalk --work-queue --priority high
ods crosswalk paragon --work-queue
ods crosswalk terminal.write --work-queue
```

Repository-local commands use
`PYTHONPATH=tools/ods-tools/src python3 -m ods_tools` in place of `ods`.

## Resolve an item

1. Use the host census path and its cataloged archive references to find
   primary evidence for the canonical operation.
2. Record exact symbols and evidence without inventing undocumented
   signatures.
3. Mark historical claims `verified`, `inferred`, or `unknown` according to
   the repository evidence rules.
4. Update the canonical census mapping only after review, then regenerate the
   M6.1 crosswalk, coverage report, and this queue.
5. Run all generator checks, strict validation, and crosswalk tests.

Removing an item is a consequence of changing its reviewed crosswalk status;
contributors should never edit the generated queue directly.
