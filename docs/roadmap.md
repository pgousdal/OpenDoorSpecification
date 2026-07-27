# Roadmap

## M0 — Repository foundation

- project structure
- contribution and evidence rules
- initial schemas and validation
- unified `ods` CLI

## M1.6 — API extraction

- archive inventories
- `.fd` parser
- C header declaration parser
- Amiga E and assembler symbol extraction
- guide/document indexer
- evidence manifests

## M1.7 — API comparison

- normalized capability mappings
- generated comparison matrix
- equivalent and unique operations

## M1.8 — ODS Core 0.1

- session
- terminal
- lifecycle
- status
- optional file/message/storage services

## M1.9 — Adapter contracts

- ABBS
- Paragon/StarNet
- DayDream
- AmiExpress/AEDoor
- AmBoS
- door_io.library
- FAME DoorPort
- generic CLI/stdio

## M1.9 — Reference adapter

Status: complete.

- Deterministic host/simulator adapter for all ODS Core 0.1 operations.
- Machine-readable execution transcripts.
- Disconnect and normal-exit conformance behavior.

## M2.0 — First historical adapter

Next: implement one verified historical adapter, beginning with ABBS or DayDream,
and execute shared conformance cases against both it and the host adapter.

## M2.0 — DayDream adapter

First host-tested historical adapter. A native Amiga backend follows in M2.1.


## M4.0 — Architecture baseline

Status: complete.

- Establish the normative specification as the primary product.
- Separate specification, toolkit, catalog, and reference implementation responsibilities.
- Define evidence, compatibility, and migration rules.
- Avoid disruptive path changes until compatibility entry points exist.

## M4.1 — Canonical knowledge model

- stable operation and structure identifiers
- canonical provenance records
- strict cross-reference validation
- generated coverage and adapter-gap reports

## M4.2 — Publication candidate

- generated reference documentation
- GitHub Pages publication
- strict one-command validation
- ODS 1.0 release-candidate checklist

## M4.4 — Canonical operation records

Status: complete.

- one generated machine-readable record per ODS operation
- historical implementation and provenance aggregation
- reference-adapter support status
- strict stale-record validation

- [x] M4.6 — Conformance Profiles: cumulative adapter capability levels and generated conformance report.

## M4.7 — Historical corpus expansion

Completed: four new archive inventories, duplicate-distribution evidence, and documented Maxs door findings.

## M4.8 — MAXs source expansion

Status: complete.

- Catalog MAXs Coders, MAXs Guide, and MAXShell 1.01.
- Add verified source-level MAXShell protocol evidence.
- Preserve the evidence boundary by avoiding new mappings from contextual documentation alone.

## M4.9 — Executable Conformance Suite

Completed: executable profile tests for portable reference adapters.


## M5.0 — Comprehensive archive reanalysis

Completed: all supplied archives were reprocessed, a preserved ABBS 2.0 source snapshot was added, and machine-readable archive-level research coverage was introduced.


## M5.1 — Second comprehensive archive reanalysis

Completed: reprocessed 20 additional archive uploads, confirmed their duplicate status, and recorded deeper cross-language API and protocol findings without inflating canonical archive or provenance counts.


## M5.2 — Comprehensive AmiExpress corpus reanalysis (complete)

See `docs/m52-comprehensive-amiexpress-reanalysis.md`.


## M6.0 — Complete API Census (complete)

See `docs/m60-complete-api-census.md`.

<!-- m61-status -->
### M6.1 — API crosswalk: complete

Delivered data model, deterministic generation, CLI lookup, validation,
coverage reporting and milestone acceptance checks. Mapping expansion continues
in M6.2.

### M6.2 — Crosswalk evidence expansion: in progress

- PR1: deterministic evidence work queue, documented priority rules, CLI
  filtering, and stale-data validation.
- PR2: first eight-cell primary-evidence batch across ABBS, AmBoS, DayDream,
  and UCDoor; reviewed coverage increased while M6.2 remains in progress.
- PR3: machine validation for stable mapping identities, evidence references,
  rationales, partial limitations, and provenance cross-references.
- PR4: eight AEDoor mappings reviewed from the cataloged SDK archive; seven
  verified and one partial, with M6.2 still in progress.
- PR5: eight FAME DoorPort mappings verified from the cataloged v1.30 command
  guide; ambiguous node-status mutation remains unassessed.
- PR6: four UCDoor mappings verified from the cataloged programmer guide,
  public header, and original demo; status mutation remains unassessed.
- PR7: two Door-IO lifecycle mappings harvested from the cataloged SDK; one
  verified and one partial, with unrelated gaps left unassessed.
- PR8: deterministic triage for every remaining queue item, including reason,
  research effort, confidence, and per-host next opportunities.
- Future work: research and review queued host-operation cells.
