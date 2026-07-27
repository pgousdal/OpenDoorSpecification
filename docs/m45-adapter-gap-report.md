# M4.5 Adapter Gap Report

M4.5 adds a generated matrix comparing every ODS Core operation with each
historical API mapping and each executable adapter.

Statuses are:

- `supported`: verified historical mapping or implemented adapter operation.
- `partial`: historical evidence exists, but the mapping remains provisional.
- `missing`: no mapping or adapter implementation is declared.

The committed report is generated from the operation catalog, semantic mappings,
and adapter metadata. It must not be edited by hand.

```sh
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools gaps
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools gaps api:daydream
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools gaps adapter:daydream
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools gaps --json
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools gaps --write catalog/knowledge/adapter-gap-report.json
```

Strict validation rejects a stale committed report.
