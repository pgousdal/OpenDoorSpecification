# M6.3 — Capability Architecture Completion

## Status

M6.3 is complete. All six PRs have been reviewed and merged.

## Goals

M6.3 defined deterministic, implementation-independent contracts that future
runtimes can consume and validate. It did not introduce adapter runtime code,
new canonical operations, new historical mappings, or new evidence work.

The milestone established three architectural layers between canonical
operations and implementations:

1. **Compatibility Profiles** — implementation-independent capability targets
   that describe which operations form a useful interoperability level.
2. **Adapter Contracts** — language-neutral behavioral boundaries that define
   what an adapter must mean and how it reports outcomes.
3. **Capability Declarations** — versioned statements by one implementation
   identifying which profiles and contracts it supports.

These layers extend the M4.6 conformance profiles and the M6.1/M6.2 crosswalk
evidence without modifying them. Historical evidence, canonical operations,
and mapping provenance remain unchanged.

## Deliverables

| PR | Deliverable | Key Artifacts |
| --- | --- | --- |
| PR1 | Compatibility profile and adapter contract architecture | `docs/m63-compatibility-profile-architecture.md` |
| PR2 | Compatibility Profile schema and catalog | `schemas/compatibility-profile.schema.json`, `catalog/profiles/compatibility.json` |
| PR3 | Adapter Contract schema and canonical catalog | `schemas/adapter-contract.schema.json`, `catalog/contracts/adapter-contracts.json` |
| PR4 | Capability Declaration schema and reference catalog | `schemas/capability-declaration.schema.json`, `catalog/capabilities/` |
| PR5 | Capability/Profile cross-model validation | Validation functions in `ods_tools/capability_declarations.py` |
| PR6 | Milestone review and completion | `docs/m63-completion.md`, documentation consistency updates |

No PR introduced a generator. All M6.3 catalogs are source-controlled, not
derived data.

## Architectural layering

```
canonical operations  (catalog/operations/core.json)
        |
        +--> Compatibility Profile  (catalog/profiles/compatibility.json)
        |
Adapter Contract     (catalog/contracts/adapter-contracts.json)
        |
        +--> Capability Declaration  (catalog/capabilities/*.json)
```

The canonical operation catalog is the single source of truth for operation
identity and semantics. Profiles, contracts, and declarations all reference
operations by their canonical ID.

Historical host mappings (M6.1 crosswalk, M6.2 evidence) supply evidence about
possible translations. They do not themselves constitute a profile, contract,
or declaration.

## Schemas added

Three JSON Schemas were added under `schemas/`:

- `compatibility-profile.schema.json` — enforces field presence, profile
  identifier syntax, non-empty required operations, unique operation arrays,
  and the controlled maturity vocabulary.
- `adapter-contract.schema.json` — enforces field presence, the closed
  outcome vocabulary (`success`, `unsupported`, `invalid-request`,
  `host-failure`, `disconnected`), unique operation identifiers, and
  lifecycle field structure.
- `capability-declaration.schema.json` — enforces field presence, the closed
  capability status vocabulary (`supported`, `partial`, `unsupported`),
  implementation ID syntax, and operation ID patterns.

Repository validation supplements each schema with cross-file checks that
JSON Schema alone cannot express (canonical operation existence, duplicate
prevention across files, operation-set disjointness).

## Catalogs added

Three catalogs were added:

- **Compatibility Profile catalog** (`catalog/profiles/compatibility.json`):
  three profiles (`minimal`, `interactive`, `complete`) preserving the
  existing M4.6 required-operation baseline. Each profile also lists optional
  operations, operations outside the profile, compatibility expectations, and
  conformance evidence expectations.
- **Adapter Contract catalog** (`catalog/contracts/adapter-contracts.json`):
  one contract for every canonical operation, defining normative behavior,
  inputs, output, allowed outcomes, lifecycle semantics, unsupported behavior,
  and implementation obligations.
- **Capability Declaration catalog** (`catalog/capabilities/`):
  reference declarations for `host-simulator` (minimal profile) and
  `daydream` (interactive profile).

## Validation capabilities

Three levels of deterministic, non-executing validation are available:

1. **JSON Schema validation** — structural field presence and type checks
   applied at load time.
2. **Repository structural validation** — cross-file checks for canonical
   operation existence, duplicate IDs, operation-set disjointness, unknown
   fields, and closed-vocabulary membership.
3. **Cross-model validation** (PR5) — profile-satisfaction checking,
   partial-required-operation reporting, contract-reference validation, and
   canonical operation resolution.

CLI commands `ods capabilities validate`, `ods capabilities show <id>`,
`ods profiles validate`, `ods contracts validate`, `ods validate`, and
`ods validate --strict` expose these checks. Output is available in
human-readable text and machine-readable JSON forms.

## CLI commands added

All M6.3 commands are language-neutral and work in both installed and
repository-local forms:

| Command | Purpose |
| --- | --- |
| `ods profiles list` | List all compatibility profiles |
| `ods profiles show <id>` | Show profile details |
| `ods profiles validate` | Validate the profile catalog |
| `ods contracts list` | List all adapter contracts |
| `ods contracts show <op>` | Show contract details |
| `ods contracts validate` | Validate the contract catalog |
| `ods capabilities list` | List all capability declarations |
| `ods capabilities show <id>` | Show declaration with validation summary |
| `ods capabilities validate` | Validate all declarations (structural + cross-model) |

## Repository impact

- 3 new JSON Schema files under `schemas/`
- 3 new catalog files (one multi-record, one per-declaration directory)
- 3 new test files
- 5 new documentation files under `docs/`
- One installable Python CLI package updated
- No existing M4.6, M6.0, M6.1, or M6.2 artifacts were modified
- No generator was added or changed

## Boundary: work intentionally deferred to M7

The following remain outside M6.3 and are deferred to future work:

- **Reference examples**: end-to-end examples of profile claims, contract
  validation, and declaration formats using existing declarations.
- **Conformance testing integration**: using Capability Declarations to drive
  or filter the M4.9 executable conformance suite.
- **Runtime capability discovery**: protocols for querying implementations
  at runtime for their declared capabilities.
- **Capability negotiation**: feature negotiation between doors and adapters.
- **Capability declaration aggregation**: merging declarations across an
  implementation network.
- **Profile extension model**: whether profile extension is represented by
  inheritance or fully expanded operation sets.
- **Explicit partial limitation names**: controlled vocabulary for naming
  profile-permitted partial limitations on required operations.
- **Evidence policy enforcement**: validating declaration evidence references
  against the profile's conformance evidence expectations at runtime.
