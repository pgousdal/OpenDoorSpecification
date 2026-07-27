# M4.4 canonical operation records

M4.4 adds a generated, operation-centric view of ODS Core. Each record combines the normative operation definition with historical API mappings, provenance coverage, and current reference-adapter support.

The records under `catalog/knowledge/operations/` are generated artifacts. Their sources of truth remain:

- `catalog/operations/core.json`
- `catalog/knowledge/operation-index.json`
- `catalog/provenance/`
- `catalog/adapters/`

Regenerate or inspect them with:

```sh
ods operations
ods operations terminal.write
ods operations terminal.write --json
ods operations --write catalog/knowledge/operations
```

`ods validate --strict` rejects stale records or an index whose ordering no longer matches the canonical operation registry. This prevents the generated view from silently drifting away from normative definitions or historical evidence.
