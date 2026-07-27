# Canonical knowledge model

M4.1 introduces stable identifiers and a common cross-reference layer without moving existing catalog files.

## Stable identifiers

Operation identifiers use `<domain>.<name>` and are permanent after publication. Historical API identifiers use lowercase kebab-case. Provenance identifiers begin with `prov.`. IDs must never be reused for a different concept; superseded records retain their original ID and may point to a replacement.

The authoritative registry is `catalog/knowledge/id-registry.json`.

## Canonical operation index

`catalog/knowledge/operation-index.json` joins the normative ODS Core operation definitions with every historical API mapping. Existing files remain authoritative for their own data during the migration period.

## Provenance records

Provenance records use one evidence vocabulary:

- `documented`: explicitly described by a primary source;
- `observed`: present in historical source code or executable-facing material;
- `inferred`: reasoned from evidence but not directly stated;
- `unknown`: deliberately unresolved.

Every source reference identifies a cataloged archive and a path within that archive. Strict validation rejects dangling operation, API, archive, and archive-entry references.

## Migration rule

M4.1 adds an index, not a second source of truth. Later milestones may generate canonical per-operation records from the existing operation and mapping files, but no current consumer is required to change paths yet.
