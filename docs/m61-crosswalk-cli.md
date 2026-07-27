# M6.1 Crosswalk CLI

PR2 adds read-only inspection of the M6.1 crosswalk and integrates crosswalk consistency checks into repository validation.

## Commands

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk paragon
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk terminal.write
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk terminal.write --json
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk paragon --all
```

Explicit prefixes are supported:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk host:paragon
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk operation:terminal.write
```

Text output hides `unassessed` cells by default. `--all` includes them. Unassessed remains distinct from unsupported.

## Validation

`ods validate` now checks index counts, deterministic ordering, complete host-operation coverage, mirrored host and operation views, evidence-class consistency, and reviewed mapping totals.
