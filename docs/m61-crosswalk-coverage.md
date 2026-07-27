# M6.1 Crosswalk evidence coverage

The coverage report measures reviewed evidence, not runtime support.

- `verified`: reviewed evidence maps the host API to the canonical operation.
- `partial`: reviewed evidence exists, but coverage is incomplete.
- `unassessed`: no reviewed mapping is recorded; this does not mean unsupported.

Generate or verify:

```bash
python3 tools/generate_crosswalk_coverage.py
python3 tools/generate_crosswalk_coverage.py --check
```

CLI examples:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk --coverage
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk --gaps
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk paragon --gaps
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools crosswalk terminal.write --coverage
```

`ods validate --strict` rejects a stale committed coverage report.
