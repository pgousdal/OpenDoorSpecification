# Provenance population

M4.2 begins populating the canonical provenance model with primary-source records.

The first population covers the best-supported mappings and ABI claims for the
DayDream DreamDoor API and the Paragon/MAXs-compatible message protocol. Each
record points to paths already present in an archive manifest, so
`ods validate --strict` can detect renamed archives, missing files, unknown API
IDs, and unknown ODS operation IDs.

## Evidence policy

- `documented` means the SDK or its documentation explicitly describes the claim.
- `observed` means shipped example or historical door source demonstrates it.
- `inferred` is reserved for claims that require interpretation beyond the source.
- A provenance record may cite multiple independent sources.

M4.2 does not claim complete provenance coverage. Remaining provisional mappings
must be populated or explicitly downgraded before ODS 1.0.
