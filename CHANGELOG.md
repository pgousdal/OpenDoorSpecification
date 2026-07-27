## M5.2

- Reanalysed twelve AmiExpress, AmiX and MAXs archives from raw bytes.
- Added AmiExpress and AmiX source snapshots plus DoorStatus and MDoors 1–5 manifests.
- Added machine-readable evidence and source-corpus provenance.
- Preserved strict separation between host internals, SDK contracts and behavioral evidence.

# Changelog

## M5.1 - Second comprehensive archive reanalysis

- Reprocessed a second batch of 20 LHA archives from raw bytes.
- Confirmed all 20 uploads as byte-identical redistributions while still unpacking and inspecting every payload.
- Added a machine-readable archive-by-archive source, API, command, structure and evidence report.
- Clarified the distinct MAXs/Paragon, FAME, AmBoS, AEDoor, door_io and ABBS interface models.
- Preserved evidence boundaries: duplicate copies and undocumented numeric commands do not create new semantic mappings.
- Added regression tests for full batch coverage and key source findings.

## M5.0 - Comprehensive archive reanalysis

- Reprocessed all 20 supplied archives from raw bytes, including 19 byte-identical redistributions.
- Added the complete ABBS 2.0 preservation source snapshot as a canonical archive.
- Added a machine-readable per-archive file, language, symbol, command and extraction census.
- Added direct ABBS source corroboration for node state and carrier-loss handling.
- Kept ACP/AX `-lh1-` findings explicitly bounded instead of inferring unavailable source semantics.
- Added seven regression tests for the full reanalysis.

## M4.9 - Executable Conformance Suite

- Added executable cases for all 11 ODS Core operations.
- Added portable execution harnesses for the host simulator and DayDream adapter.
- Added `ods conformance` with text, filtered, JSON, and report-writing modes.
- Added strict validation of the committed executable conformance report.
- Both portable reference adapters pass the complete profile.

## M4.8

- Added manifests for MAXs Coders, MAXs Guide, and MAXShell 1.01.
- Added a primary-source MAXShell C analysis confirming the DoorMsg layout and commands 1, 6, 8, 10, 13, 14, 20, 100+, 200, 201, and 203.
- Added MAXShell to the historical door corpus and canonical provenance catalog.
- Recorded `MAXs_Coders (1).lha` as a byte-identical redistribution.
- Expanded the catalog to 29 archives and 904 entries.

## M4.7

- Added four archive manifests covering ACP 3.00, AX 3.00, mAGNUM cHAT 1.10, and Multi-Quest 1.1.
- Recorded five byte-identical redistributions.
- Added conservative research findings and two documented Maxs door corpus entries.
- Expanded the catalog to 26 archives and 880 entries.


## M4.6 — Conformance Profiles

- Added cumulative minimal, interactive, and complete adapter profiles.
- Added generated adapter conformance reporting and the `ods profiles` command.
- Extended strict validation to reject invalid profiles and stale conformance output.
- Added profile schemas, documentation, and regression tests.

## Unreleased

### Added

- Initial repository structure.
- Evidence and research methodology.
- Draft ODS capability model.
- `ods` command-line tool with LHA inventory support.
- Machine-readable inventories for the initial Amiga BBS SDK corpus.

## M1.7

- Added LH5 payload decompressor.
- Added verified symbol manifests from historical SDK files.
- Added Paragon and FAME research contracts.
- Added initial capability matrix.

## M1.8

- Added the normative ODS Core 0.1 operation catalog.
- Added provisional semantic mappings for seven historical API families.
- Added `ods inspect` and `ods compare`.
- Extended repository validation to cover operations and mappings.

## M1.9

- Added a deterministic reference host adapter covering all ODS Core 0.1 operations.
- Added prompt disconnect and lifecycle termination behavior.
- Added the JSON scenario simulator and `ods simulate`.
- Added adapter metadata, scenario schema, examples, documentation, and conformance tests.

## M2.0

- Added the first historical reference adapter for DayDream DreamDoor.
- Added a portable recording backend and shared conformance tests.
- Defined explicit carrier-loss and lifecycle translation behavior.

## M2.1

- Added a portable C implementation of the DayDream adapter.
- Added a narrow binding table for compiler- and SDK-specific DreamDoor calls.
- Added carrier-safe lifecycle handling, a minimal native door example, and host C conformance tests.

## M2.2.1

- Fixed native DayDream host tests to select the system GCC, archiver, and assembler toolchain even when an Amiga cross-toolchain appears earlier in `PATH`.

## M2.2

- Added six unique forensic archive inventories.
- Recorded two byte-identical duplicate uploads.
- Verified a concrete MAXs/Paragon-compatible message protocol subset.
- Expanded the reviewed Paragon semantic mapping and command table.
- Fixed embedded-NUL filename handling in LHA inventories.

## M2.3

- Added five unique historical door/source archives and one duplicate record.
- Added observed API-usage corpus with documented/observed/inferred evidence classes.
- Added independent MAXs/Paragon protocol evidence from C and Amiga E doors.
- Added historical corpus reports and repository tests.


## M4.0

- Added the repository-level architecture manifesto.
- Defined specification, toolkit, and reference implementation boundaries.
- Defined normative/informative and evidence-strength rules.
- Added an incremental project-structure migration target with no disruptive file moves.

## M4.1

- Added stable operation, API, and provenance identifier rules.
- Added a canonical cross-reference index for ODS operations and historical mappings.
- Added a common provenance schema and strict dangling-reference validation.
- Added `ods validate --strict`.

## M4.2

- Populated canonical provenance records for DayDream and Paragon/MAXs.
- Added multi-source evidence for operation mappings, message structure, and observed behavior.
- Extended strict validation with unique provenance IDs and population statistics.
- Documented the provenance population and remaining coverage limits.

## M4.3

- Added generated provenance coverage for every semantic mapping.
- Added documented primary-source records for verified ABBS, AmBoS, and door_io mappings.
- Added `ods coverage` with text, JSON, and file output.
- Made strict validation reject verified mappings without provenance and stale coverage reports.

## M4.4

- Added generated canonical records for every ODS operation.
- Combined normative definitions, historical mappings, provenance coverage, and adapter support.
- Added `ods operations` for listing, inspection, JSON output, and regeneration.
- Made strict validation reject stale operation records and indexes.

## M4.5

- Added a generated operation-gap matrix for historical APIs and executable adapters.
- Added `ods gaps` with summary, target inspection, JSON output, and report regeneration.
- Classified coverage as supported, partial, or missing without overstating historical evidence.
- Made strict validation reject a stale adapter-gap report.
