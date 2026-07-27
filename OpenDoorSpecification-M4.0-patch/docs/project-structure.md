# Project structure and migration target

M4 separates the repository conceptually into the specification, toolkit, and
reference implementations. M4.0 documents ownership without moving stable paths.

| Current path | Owner | Role | M4 target |
| --- | --- | --- | --- |
| `spec/` | Specification | Normative operations and behavior | `spec/core/`, `spec/abi/`, `spec/operations/`, `spec/structures/` |
| `catalog/functions/` | Historical catalog | Extracted historical symbols | `catalog/historical/functions/` |
| `catalog/mappings/` | Historical catalog | Semantic mappings to ODS | `catalog/mappings/` |
| `catalog/evidence/` | Historical catalog | Primary-source findings | `catalog/evidence/` |
| `catalog/archives/` | Historical catalog | Archive inventories | `catalog/archives/` |
| `schemas/` | Shared contracts | JSON validation | `schemas/` |
| `tools/ods-tools/` | Toolkit | CLI and research tools | `toolkit/ods/` or retained compatibility path |
| `native/` | Reference implementation | Native C adapters | `reference/adapters/native/` |
| `examples/` | Reference implementation | Demonstrations and fixtures | `reference/examples/` |
| `tests/` | Quality | Repository and conformance tests | `tests/` |

## Migration constraints

The target is directional, not an instruction to move everything at once.
Existing CLI imports, Makefiles, test paths, and user commands must remain valid
until a migration step explicitly replaces them.

Every move must include:

- updated imports and build paths;
- repository validation;
- documentation changes;
- compatibility notes in the changelog;
- a focused commit that does not mix unrelated semantic changes.

## Recommended sequence

1. Canonicalize operation and structure identifiers without moving files.
2. Add provenance schemas and strict cross-reference validation.
3. Introduce generated reference documentation.
4. Consolidate reference adapters behind shared conformance interfaces.
5. Move toolkit/reference paths only after compatibility entry points exist.
