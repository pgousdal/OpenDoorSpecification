# Changelog

## Unreleased

### Changed

- Refreshed repository, contributor, CLI, and milestone documentation after
  M6.2 completion.
- Consolidated the roadmap into current, next, backlog, completed, and future
  publication sections.
- Clarified that M6.2 batch documents contain historical point-in-time totals.

## M6.2 — Crosswalk evidence expansion

- PR1 added the deterministic crosswalk evidence work queue, explicit priority
  reasons, CLI filtering, generation, and strict stale-data validation.
- PR2 reviewed eight ABBS, AmBoS, DayDream, and UCDoor cells from resolvable
  primary-source references.
- PR3 added provenance validation for stable mapping IDs, archive and document
  references, rationales, concrete symbols, and partial limitations.
- PR4 reviewed eight AEDoor mappings from the cataloged SDK guide, protocol
  reference, headers, and examples.
- PR5 reviewed eight FAME mappings from the cataloged Door-Command Guide v1.30.
- PR6 reviewed four UCDoor mappings from its guide, header, HTML reference, and
  example.
- PR7 reviewed two Door-IO lifecycle mappings from the cataloged SDK manual and
  headers.
- PR8 added deterministic triage by reason, research effort, confidence, and
  host opportunity.
- PR9 reviewed the two small-effort, high-confidence AmBoS mappings from the
  programmer guide, public headers, and SDK example.
- PR10 added deterministic completion criteria and a reason-grouped backlog
  separating completion blockers, deferred research, and archival discovery.

Semantics preserved throughout M6.2:

- `unassessed` is not equivalent to unsupported;
- `partial` is not equivalent to unsupported;
- work-queue priority and triage confidence are research guidance, not support
  claims.

## M6.1 — API crosswalk

- Added the deterministic API crosswalk for ten historical hosts and nine
  canonical operations.
- Added host and operation lookup through `ods crosswalk`.
- Added evidence coverage and gap reporting.
- Added generated-data validation and milestone acceptance tests.

## M6.0 — Complete API census

- Added a deterministic complete API census across ten historical API
  families.
- Consolidated normalized functions, structures, semantic mappings, source
  archives, evidence classes, and limitations.
- Added schema validation and stale-count tests.

## M5.2 — Comprehensive AmiExpress corpus reanalysis

- Reanalyzed twelve AmiExpress, AmiX, and MAXs archives from raw bytes.
- Added AmiExpress and AmiX source snapshots plus DoorStatus and MDoors 1–5
  manifests.
- Added machine-readable evidence and source-corpus provenance.
- Preserved separation between host internals, SDK contracts, and behavioral
  evidence.

## M5.1 — Second comprehensive archive reanalysis

- Reprocessed 20 additional LHA archives from raw bytes.
- Confirmed all uploads as byte-identical redistributions while inspecting
  every payload.
- Added archive-level source, API, command, structure, and evidence reporting.
- Clarified the distinct MAXs/Paragon, FAME, AmBoS, AEDoor, Door-IO, and ABBS
  interface models.

## M5.0 — Comprehensive archive reanalysis

- Reprocessed all 20 supplied archives from raw bytes.
- Added the ABBS 2.0 preservation source snapshot as a canonical archive.
- Added per-archive file, language, symbol, command, and extraction census.
- Added ABBS source corroboration for node state and carrier-loss handling.

## M4.9 — Executable conformance suite

- Added executable cases for all 11 ODS Core operations.
- Added portable execution harnesses for the host simulator and DayDream
  adapter.
- Added `ods conformance` text, filtered, JSON, and report-writing modes.
- Added strict validation of the committed executable conformance report.

## M4.8 — MAXs source expansion

- Added manifests for MAXs Coders, MAXs Guide, and MAXShell 1.01.
- Added primary-source MAXShell protocol evidence.
- Added MAXShell to the historical corpus and provenance catalog.
- Recorded the MAXs Coders duplicate redistribution.

## M4.7 — Historical corpus expansion

- Added ACP 3.00, AX 3.00, mAGNUM cHAT 1.10, and Multi-Quest 1.1 manifests.
- Recorded duplicate redistributions.
- Added conservative research findings and documented MAXs door entries.

## M4.6 — Conformance profiles

- Added cumulative minimal, interactive, and complete adapter profiles.
- Added generated adapter conformance reporting and `ods profiles`.
- Added strict stale-report validation and regression tests.

## M4.5 — Adapter gap report

- Added a generated operation-gap matrix for historical APIs and adapters.
- Added `ods gaps` with summaries, target inspection, JSON, and regeneration.
- Kept supported, partial, and missing classifications distinct.

## M4.4 — Canonical operation records

- Added generated records for every ODS operation.
- Combined definitions, historical mappings, provenance, and adapter support.
- Added `ods operations` and strict stale-record validation.

## M4.3 — Provenance coverage

- Added generated provenance coverage for every semantic mapping.
- Added primary-source records for verified ABBS, AmBoS, and Door-IO mappings.
- Added `ods coverage` and strict coverage validation.

## M4.2 — Provenance population

- Added canonical provenance records for DayDream and Paragon/MAXs.
- Added multi-source operation, structure, and behavior evidence.
- Extended strict validation with population statistics.

## M4.1 — Canonical knowledge model

- Added stable operation, API, and provenance identifiers.
- Added a canonical cross-reference index and common provenance schema.
- Added strict dangling-reference validation and `ods validate --strict`.

## M4.0 — Architecture baseline

- Defined specification, toolkit, catalog, and reference-implementation
  boundaries.
- Defined normative, informative, evidence-strength, and migration rules.

## M2.3 — Historical door corpus

- Added five unique historical door/source archives and one duplicate record.
- Added observed API usage with documented, observed, and inferred evidence.
- Added independent MAXs/Paragon protocol evidence and repository tests.

## M2.2 — Forensic archive analysis

- Added six unique forensic archive inventories and duplicate detection.
- Verified a MAXs/Paragon-compatible message protocol subset.
- Expanded reviewed Paragon mappings and fixed embedded-NUL LHA filenames.

## M2.2.1 — Native test toolchain selection

- Made native DayDream tests select system GCC, archiver, and assembler tools
  when an Amiga cross-toolchain appears earlier in `PATH`.

## M2.1 — Native DayDream adapter

- Added portable C DayDream adapter code and a narrow binding table.
- Added carrier-safe lifecycle behavior, an example, and host C tests.

## M2.0 — DayDream adapter

- Added the first historical reference adapter.
- Added a portable recording backend and shared conformance tests.
- Defined carrier-loss and lifecycle translation behavior.

## M1.9 — Reference adapter

- Added a deterministic host adapter covering ODS Core 0.1.
- Added lifecycle behavior, JSON scenarios, simulator, metadata, and tests.

## M1.8 — ODS Core 0.1

- Added the normative operation catalog.
- Added provisional mappings for seven historical API families.
- Added `ods inspect`, `ods compare`, and mapping validation.

## M1.7 — API extraction and comparison

- Added LH5 decompression and SDK symbol extraction.
- Added Paragon and FAME research contracts and the capability matrix.

## Repository foundation

- Added the initial repository structure, evidence methodology, schemas,
  catalog, and unified `ods` CLI.
