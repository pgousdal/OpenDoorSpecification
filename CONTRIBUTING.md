# Contributing

Contributions are welcome. ODS specifies and catalogs door interfaces; it does
not implement a BBS. Keep changes within that boundary and avoid unrelated
refactoring.

## Development setup

Python 3.11 or newer is required. Install the CLI in editable mode:

```bash
python3 -m pip install -e tools/ods-tools
ods validate
```

Alternatively, run it directly:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate
```

## Evidence contributions

Historical claims must remain `verified`, `inferred`, or `unknown` according to
the repository evidence rules. Never promote an inferred claim without direct
support.

For reviewed crosswalk mappings, record:

- stable host and canonical-operation IDs;
- archive filename and SHA-256 identity;
- exact internal document or source path;
- concrete symbol, API, command, message, structure, field, or protocol
  element;
- concise mapping rationale;
- limitations whenever the status is `partial`.

Do not commit proprietary archives or full third-party documentation. Record
hashes, paths, versions, and short factual evidence summaries instead. See
[research methodology](docs/research-methodology.md) and
[crosswalk provenance validation](docs/m62-evidence-provenance-validation.md).

## Crosswalk research workflow

1. Inspect `ods crosswalk --backlog` and select a stable backlog ID.
2. Confirm the triage reason and canonical operation definition.
3. Locate primary or near-primary evidence.
4. Update the census source mapping; do not edit generated crosswalk JSON.
5. Regenerate crosswalk, coverage, queue, triage, and completion reports.
6. Inspect the mapping with `ods crosswalk <host> <operation> --evidence`.
7. Run normal and strict validation.

`unassessed` and `partial` do not mean unsupported. Work-queue priority and
triage confidence are research guidance, not support claims.

## Generated data

Run all crosswalk generators after relevant source or classification changes:

```bash
python3 tools/generate_crosswalk.py
python3 tools/generate_crosswalk_coverage.py
python3 tools/generate_crosswalk_work_queue.py
python3 tools/generate_crosswalk_triage.py
python3 tools/generate_crosswalk_completion.py
```

Use each generator's `--check` option when no regeneration is expected.

## Validation

Before submitting changes:

```bash
python3 tools/generate_crosswalk.py --check
python3 tools/generate_crosswalk_coverage.py --check
python3 tools/generate_crosswalk_work_queue.py --check
python3 tools/generate_crosswalk_triage.py --check
python3 tools/generate_crosswalk_completion.py --check

PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
python3 -m unittest discover -s tests
python3 -m unittest discover -s tools/ods-tools/tests
python3 scripts/check-repository.py
git diff --check
```

Add focused tests for parser, schema, generator, validation, or CLI behavior
when those areas change. Do not hard-code changing research totals unless they
are formal milestone invariants.
