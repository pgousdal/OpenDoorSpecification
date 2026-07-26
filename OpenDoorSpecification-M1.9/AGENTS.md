# AGENTS.md

## Scope

These instructions apply to the entire repository.

## Project boundaries

- ODS specifies and catalogs door interfaces; it does not implement a BBS.
- DoorForge is a separate reference implementation.
- Do not copy proprietary archives or full third-party documentation into this repository.
- Record hashes, file paths, versions, and short evidence summaries instead.

## Evidence rules

Every historical claim must be marked as one of:

- `verified`: directly supported by archived documentation, headers, source, or runtime tests.
- `inferred`: strongly indicated but not directly specified.
- `unknown`: not established.

Never upgrade `inferred` to `verified` without adding evidence.

## Data rules

- Keep catalog identifiers stable and lowercase with hyphens.
- Validate JSON against the repository schemas.
- Preserve original symbol names exactly.
- Add normalized capability mappings separately from extracted symbols.
- Never invent signatures for undocumented functions.

## Development

- Python code targets Python 3.11 or newer.
- Prefer the standard library unless a dependency materially improves correctness.
- Add tests for parser changes and malformed input.
- Run `python -m unittest discover -s tests` and the tool tests before committing.
