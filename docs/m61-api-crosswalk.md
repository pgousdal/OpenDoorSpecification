# M6.1 API crosswalk

M6.1 introduces a deterministic, evidence-based crosswalk between historical
door/BBS host APIs and the canonical Open Door Specification operation model.

## Scope

The milestone covers:

- 10 historical hosts;
- 9 canonical operations;
- 90 host-operation cells;
- 26 reviewed mappings;
- deterministic generated crosswalk artifacts;
- CLI lookup by host or canonical operation;
- evidence coverage and gap reporting;
- repository validation for stale generated data.

The remaining cells are recorded as `unassessed`.

`unassessed` means that no reviewed mapping is currently recorded. It does not
mean that a host lacks the capability.

`partial` means that reviewed evidence exists but does not completely cover the
canonical operation. It also does not mean unsupported.

## Generated artifacts

The crosswalk is stored under:

```text
catalog/crosswalk/
```

The evidence coverage report is:

```text
catalog/crosswalk/coverage.json
```

Regenerate and verify:

```bash
python3 tools/generate_crosswalk.py
python3 tools/generate_crosswalk.py --check

python3 tools/generate_crosswalk_coverage.py
python3 tools/generate_crosswalk_coverage.py --check
```

## CLI

When the package is installed:

```bash
ods crosswalk
ods crosswalk paragon
ods crosswalk terminal.write
ods crosswalk --coverage
ods crosswalk --gaps
ods crosswalk paragon --gaps
ods crosswalk terminal.write --coverage
ods validate
```

Directly from a repository checkout:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk
```

Machine-readable output:

```bash
PYTHONPATH=tools/ods-tools/src   python3 -m ods_tools crosswalk --coverage --json
```

## Acceptance criteria

M6.1 is complete when:

1. both generators pass `--check`;
2. the crosswalk index reports 10 hosts and 9 operations;
3. the coverage report contains 90 cells;
4. reviewed mappings equal verified plus partial mappings;
5. `unassessed` is never represented as unsupported;
6. host and operation CLI lookups succeed;
7. repository validation succeeds;
8. the M6.1 acceptance test passes.

## Next milestone

Further mapping research belongs in M6.2. M6.1 defines the model, generated
artifacts, CLI, validation and coverage semantics; it does not claim complete
coverage of every historical host API.
