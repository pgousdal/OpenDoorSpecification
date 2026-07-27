# M6.0 — Complete API Census

M6.0 consolidates the repository’s historical API knowledge into one deterministic, machine-readable census.

## Scope

The census covers ABBS, AmiExpress/AEDoor, AmBoS, DayDream, door_io.library, FAME, MAXs/Paragon, UCDoor, Zeus, and WWBBS. Each family is classified as a documented SDK, documented protocol, wrapper/binding, or observed-door corpus.

## Evidence rules

- A documented symbol is not automatically a normative ODS mapping.
- An empty parameter list means the current extraction did not preserve a signature unless the source explicitly proves a no-argument call.
- Internal host functions are separated from public door contracts.
- Wrapper APIs and observed door behavior remain distinct from host APIs.
- Numerically equal commands in unrelated protocols are not treated as equivalent.

## Outputs

`catalog/census/index.json` is the canonical index. One record per API family is stored in `catalog/census/`. Records aggregate functions, structures, current semantic mappings, source archives, evidence class, and limitations.

## Current result

The census contains 10 API families, 230 normalized entries, and 26 current semantic mappings. Context-only families remain explicit zero-entry records rather than being silently omitted.
