# M6.1 Crosswalk Data Model

M6.1 PR1 introduces a deterministic, machine-readable crosswalk derived from the
M6.0 API census.

## Evidence boundary

A missing semantic mapping is emitted as `unassessed`, never `unsupported`.
Absence of a reviewed mapping is not evidence that a host lacks the capability.

The generator preserves the M6.0 mapping status, symbols, semantic-review state,
host evidence class, and host limitations. Lossiness remains `unknown` until a
separate evidence-backed translation review establishes whether a mapping is
lossless or lossy.

## Generated files

```text
catalog/crosswalk/
  index.json
  operations.json
  abbs.json
  aedoor.json
  ambos.json
  daydream.json
  door-io.json
  fame.json
  paragon.json
  ucdoor.json
  wwbbs.json
  zeus.json
```

Generate or refresh the committed data:

```bash
python3 tools/generate_crosswalk.py
```

Verify that generated data is current:

```bash
python3 tools/generate_crosswalk.py --check
```

## Scope

PR1 defines the data model and deterministic generation only. It does not yet:

- add the `ods crosswalk` CLI command;
- assert unsupported capabilities;
- infer equivalence from matching command numbers;
- classify mappings as lossless or lossy;
- replace the canonical M6.0 census.

Those tasks belong to later M6.1 pull requests after semantic review.
