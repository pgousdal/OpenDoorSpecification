# Changelog

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

## M2.2

- Added six unique forensic archive inventories.
- Recorded two byte-identical duplicate uploads.
- Verified a concrete MAXs/Paragon-compatible message protocol subset.
- Expanded the reviewed Paragon semantic mapping and command table.
- Fixed embedded-NUL filename handling in LHA inventories.
