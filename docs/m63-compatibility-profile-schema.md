# M6.3 PR2 — Compatibility Profile schema and catalog

M6.3 PR2 adds the first machine-readable form of the architecture defined by
PR1. The catalog describes capability targets; it does not describe an
implementation, host mapping, or historical evidence.

The schema is `schemas/compatibility-profile.schema.json` and the source
catalog is `catalog/profiles/compatibility.json`. The existing
`catalog/profiles/conformance.json` and its generated M4.6 conformance report
remain unchanged and continue to provide the required-operation baseline.

## Profile philosophy

A Compatibility Profile is a versioned set of canonical operations and
cross-cutting expectations that an implementation may claim. It is
implementation-independent:

- required operations define the minimum capability target;
- optional operations belong to the profile vocabulary but are not required;
- operations outside the profile are explicitly outside its guarantee;
- compatibility expectations describe observable behavior;
- conformance evidence expectations describe what substantiates a future claim.

Profiles contain no host IDs, mappings, archive references, symbols, or
implementation fields. Historical evidence remains in the M6.1/M6.2 catalog
and provenance model.

## Catalog structure

The catalog contains:

- `schema_version`: compatibility-catalog schema version;
- `profile_version`: version of the profile definitions;
- `spec_version`: targeted ODS specification version;
- `profiles`: the unique profile records.

Each profile contains:

| Field | Meaning |
| --- | --- |
| `id` | Stable lowercase profile identifier. |
| `title` | Human-readable profile name. |
| `description` | Capability-target description. |
| `maturity` | `draft`, `stable`, or `deprecated`. Current M4.6-derived profiles are `draft` at version 0.1.0. |
| `required_operations` | Canonical operations an implementation must support to claim the profile. This list is non-empty. |
| `optional_operations` | Canonical operations the profile recognizes but does not require. |
| `operations_outside_profile` | Canonical operations explicitly outside the profile guarantee. |
| `compatibility_expectations` | Observable profile-wide expectations, independent of implementation technique. |
| `conformance_evidence_expectations` | Evidence a future implementation claim must provide. |

The three operation lists are mutually exclusive and together cover the
current canonical operation catalog. This explicit partition makes omissions
visible and keeps profile interpretation deterministic.

## Validation

The JSON Schema enforces field presence, types, profile identifier syntax,
non-empty required operations, unique operation arrays, and the controlled
maturity vocabulary. Repository validation additionally resolves every
operation ID against `catalog/operations/core.json`, rejects duplicate profile
IDs, rejects overlap between operation sets, and rejects unknown catalog or
profile fields.

The catalog currently contains exactly the existing M4.6 profiles:

- `minimal`: lifecycle-safe output target;
- `interactive`: terminal input and basic caller context;
- `complete`: all current canonical operations required.

Their required-operation semantics are unchanged. No new profile was added.

## CLI

The profile inspection commands are language-neutral and work with installed
or repository-local tooling:

```bash
ods profiles list
ods profiles show minimal
ods profiles show interactive --json
ods profiles show complete
ods profiles validate
```

The pre-existing forms remain available for M4.6 adapter evaluation, including
`ods profiles`, `ods profiles daydream`, and `ods profiles --write ...`.

## Lifecycle and future contracts

Profile records are normative capability targets, not declarations by a
runtime. A future Capability Declaration will identify an implementation’s
profile claim and operation statuses. PR3 now defines machine-readable Adapter
Contract behavior, outcomes, and lifecycle semantics in its own catalog and
schema. Capability Declaration schema remains future M6.3 work.

Historical `verified`, `partial`, and `unassessed` mappings remain evidence
statuses, not profile statuses. A verified mapping can support a host adapter’s
translation rationale; a partial mapping carries limitations; an unassessed
mapping neither proves nor disproves capability. Profiles can therefore be
defined independently of incomplete historical coverage.

## Validation workflow

PR2 does not add a generator because the profile catalog is source-controlled,
not derived data. Validate it directly or through repository validation:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools profiles validate
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
```

Future schema PRs may add canonical JSON Schema validation and generated
artifacts, but they SHALL preserve the three existing profile IDs and their
required-operation semantics.
