# M6.3 PR4 — Capability Declaration schema and reference catalog

M6.3 PR4 adds a machine-readable way for an implementation to declare which
canonical Adapter Contracts it supports. The schema and catalog describe
implementations; they do not redefine Adapter Contracts or Compatibility
Profiles.

The schema is `schemas/capability-declaration.schema.json`. The reference
catalog is `catalog/capabilities/` and contains at least two declarations
representing different implementation capabilities.

## Philosophy

A Capability Declaration states what one implementation supports, partially
supports, or intentionally leaves unsupported. It is not an Adapter Contract
(which defines behavioral and lifecycle semantics for a canonical operation)
and it is not a Compatibility Profile (which defines an implementation-
independent capability target).

Capability Declaration values describe implementation support. They are
distinct from Adapter Contract outcome values, which describe the result of
one operation invocation at runtime:

- `supported`: the implementation provides the operation with full canonical
  semantics;
- `partial`: the implementation provides the operation subject to documented
  limitations;
- `unsupported`: the implementation does not provide the operation.

These are claims about an implementation's design, not runtime outcomes. An
implementation that declares `supported` for `terminal.write` may still return
a `host-failure` outcome if the host fails at runtime.

## Schema fields

| Field | Required | Meaning |
| --- | --- | --- |
| `schema_version` | yes | Capability declaration schema version (currently 1). |
| `spec_version` | yes | Targeted ODS specification version. |
| `implementation_id` | yes | Stable lowercase implementation identifier. |
| `implementation_name` | yes | Human-readable implementation name. |
| `implementation_version` | yes | Implementation version string. |
| `target_platform` | yes | Target platform description. |
| `supported_profiles` | yes | Array of Compatibility Profile IDs the implementation claims. |
| `capabilities` | yes | Array of per-operation capability entries. |

Each capability entry contains:

| Field | Required | Meaning |
| --- | --- | --- |
| `operation` | yes | Canonical operation ID from `catalog/operations/core.json`. |
| `status` | yes | Capability status value. |
| `notes` | no | Optional implementation notes about the operation. |

## Capability vocabulary

The closed vocabulary has three values:

| Value | Meaning |
| --- | --- |
| `supported` | The implementation provides the canonical operation with full contractual semantics. |
| `partial` | The implementation provides the operation with documented limitations, deviations, or host-specific constraints. |
| `unsupported` | The implementation does not provide the operation. |

The vocabulary is deliberately separate from Adapter Contract outcome values
(`success`, `unsupported`, `invalid-request`, `host-failure`, `disconnected`).
Capability status describes implementation support; contract outcomes describe
the result of one operation invocation.

## Relationship to Compatibility Profiles

A Capability Declaration references one or more Compatibility Profiles through
`supported_profiles`. The profiles define capability targets; the declaration
states that the implementation meets those targets. The declaration does not
redefine or modify the profiles.

The implementation's per-operation statuses are independent of its profile
claims. An implementation may claim a profile while declaring some required
operations as `partial` where documented limitations are acceptable for the
profile context.

## Relationship to Adapter Contracts

Each capability entry references a canonical operation. The operation's Adapter
Contract defines the normative behavior, lifecycle semantics, and allowed
outcomes for that operation. The capability declaration does not duplicate the
contract—it references the operation, and the contract is looked up from the
canonical catalog.

The `unsupported` status in a capability declaration is a design claim about
the implementation. The `unsupported` value in an Adapter Contract outcome
vocabulary is a runtime result. These concepts are intentionally kept separate
to avoid conflating implementation design with runtime behavior.

## Intended future use

Capability Declarations are designed for:

1. **Implementation discovery**: tooling can enumerate available
   implementations and their claimed capabilities without loading or
   executing them.
2. **Profile matching**: tooling can check whether an implementation's
   declared capabilities satisfy a given Compatibility Profile.
3. **Contract-aware tooling**: editors, CI systems, and documentation
   generators can link capability entries to the canonical Adapter Contract
   definitions.
4. **Portability assessment**: door authors can check whether their required
   operations are available across target implementations.

Future work may add:
- capability declaration aggregation across an implementation network;
- runtime capability discovery protocols;
- capability-based feature negotiation between doors and adapters.

## CLI

Installed and repository-local forms are equivalent:

```bash
ods capabilities list
ods capabilities show host-simulator
ods capabilities show daydream --json
ods capabilities validate
```

`ods validate` and `ods validate --strict` also validate the committed
capability declaration catalog. This PR does not add a generator because the
catalog is source-controlled and not derived from implementation data.

## Validation

The JSON Schema enforces field presence, types, implementation ID syntax,
capability status membership, and operation ID patterns. Repository validation
additionally:

- resolves every operation ID against `catalog/operations/core.json`;
- rejects duplicate implementation IDs;
- rejects duplicate operation declarations within one implementation;
- rejects invalid capability status values;
- rejects unknown declaration or capability fields;
- checks that `notes` is non-empty when present.

## Reference catalog

The reference catalog contains declarations for two implementations:

- **host-simulator** (`catalog/capabilities/host-simulator.json`): the
  in-memory reference host adapter, claiming the `minimal` profile with
  partial support for line input, time-left, and host commands.
- **daydream** (`catalog/capabilities/daydream.json`): the DayDream DreamDoor
  adapter, claiming the `interactive` profile with partial support for line
  input, node discovery, and host commands.
