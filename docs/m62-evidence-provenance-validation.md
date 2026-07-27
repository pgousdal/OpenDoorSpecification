# M6.2 PR3 — Crosswalk evidence provenance validation

Every reviewed crosswalk mapping must now be independently inspectable and
machine-validatable. The same validator runs during crosswalk generation,
coverage generation, work-queue generation, repository validation, and explicit
CLI evidence validation.

M6.2 remains in progress. This work changes evidence integrity, not coverage:
the crosswalk remains at 34 reviewed and 56 unassessed cells.

## Reviewed mapping requirements

Mappings with status `verified` or `partial` require:

- stable ID in `<host-id>:<canonical-operation-id>` form;
- known host and canonical operation;
- matching source mapping in the host census record;
- at least one concrete mapping symbol;
- a non-placeholder rationale;
- at least one evidence object containing:
  - cataloged archive filename;
  - exact internal document or source path;
  - concrete symbol, command, message, structure, field, or protocol element;
- a limitations array;
- valid referenced provenance-record IDs when provenance records are used.

Evidence references are checked against `catalog/archives/*.json`. Provenance
record references must exist and must identify the same host and operation.
Duplicate mapping IDs, provenance references, and evidence tuples are rejected.

`partial` mappings must have at least one non-empty limitation explaining what
prevents verification. A `verified` mapping may use an empty limitations array.
An `unassessed` cell cannot contain reviewed symbols, evidence, rationale,
limitations, or provenance.

The validator rejects empty strings, whitespace, and placeholders including
`TODO`, `unknown`, `none`, and `n/a`.

## High-quality example

The reviewed UCDoor time-left mapping records:

- ID: `ucdoor:session.time_left`;
- status: `partial`;
- symbols: `cd_GetNumInfo` and `UDC_TIMELEFT`;
- header evidence:
  `ucdoor10.lha:ucdoor/include/ucdoor.h`, symbol `UDC_TIMELEFT`;
- demo evidence:
  `ucdoor10.lha:ucdoor/demo/cd_test1.c`,
  symbol `cd_GetNumInfo(UDC_TIMELEFT)`;
- rationale: the selector returns remaining online time;
- limitation: UCDoor reports minutes while ODS requires seconds.

This is `partial`, rather than `verified`, because an adapter must normalize
the result unit.

## Inspect and validate

```bash
ods crosswalk ucdoor terminal.write --evidence
ods crosswalk daydream lifecycle.exit --evidence
ods crosswalk daydream lifecycle.exit --evidence --json
ods crosswalk --validate-evidence
ods crosswalk --validate-evidence --json
```

Repository-local commands use
`PYTHONPATH=tools/ods-tools/src python3 -m ods_tools` in place of `ods`.

Evidence validation also runs automatically in:

```bash
python3 tools/generate_crosswalk.py --check
python3 tools/generate_crosswalk_coverage.py --check
python3 tools/generate_crosswalk_work_queue.py --check
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
```

## Common failures

- archive filename does not match a cataloged `source_filename`;
- internal path does not occur in that archive manifest;
- evidence names no concrete symbol or protocol element;
- stable mapping ID, host, operation, census status, or provenance record
  disagree;
- `partial` mapping has no substantive limitation;
- evidence or provenance entries are duplicated;
- placeholder text is used instead of reviewed evidence;
- an `unassessed` cell is populated as if it were reviewed.

Contributors should update the census source mapping or operation-provenance
record, regenerate all crosswalk artifacts, and run the complete validation
workflow. Generated crosswalk JSON should not be edited directly.
