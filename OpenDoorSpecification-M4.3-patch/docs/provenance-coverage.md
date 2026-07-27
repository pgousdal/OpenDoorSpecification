# Provenance coverage

M4.3 connects semantic mapping confidence to concrete provenance records.

`catalog/knowledge/provenance-coverage.json` is a generated report. Each row joins one historical API mapping to zero or more `operation-mapping` provenance records and records the available evidence classes.

## Coverage rules

- A mapping is **covered** when at least one operation-mapping provenance record references the same API and ODS operation.
- A `verified` mapping must be covered. `ods validate --strict` rejects verified mappings without provenance.
- `partial` mappings may remain uncovered while the historical evidence is incomplete, but the report makes that gap explicit.
- Behavior, ABI, and structure records do not by themselves satisfy operation-mapping coverage.
- The checked-in report must exactly match regeneration from the mapping and provenance catalogs; strict validation rejects a stale report.

## Commands

```sh
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools coverage
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools coverage --json
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools coverage --write coverage.json
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
```

M4.3 covers every mapping currently marked `verified`. Remaining uncovered rows are deliberately non-verified mappings that require additional primary-source review.
