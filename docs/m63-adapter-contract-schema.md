# M6.3 PR3 — Adapter Contract schema and canonical catalog

M6.3 PR3 adds the normative, language-neutral contract for each canonical ODS
operation. The schema and catalog describe semantics at the ODS boundary. They
do not describe programming-language APIs, transports, host mappings,
historical evidence, or runtime implementation details.

The schema is `schemas/adapter-contract.schema.json`. The source catalog is
`catalog/contracts/adapter-contracts.json`. It contains exactly one contract
for every operation in `catalog/operations/core.json`.

## Contract philosophy

An Adapter Contract specifies what an adapter must mean and how it reports
outcomes. It is not an interface definition in the programming-language sense.
Implementations may use any language, transport, threading model, or host
integration provided that behavior at the ODS boundary satisfies the contract.

Each contract defines:

- canonical operation identity and category;
- normative behavior;
- canonical inputs and output result kind;
- allowed outcome values;
- explicit behavior when unsupported;
- normal-completion, disconnect, carrier-loss, and implementation-shutdown
  semantics;
- implementation obligations and compatibility notes.

## Catalog structure

The catalog contains `schema_version`, targeted `spec_version`, a single closed
`outcome_vocabulary`, and the ordered `contracts` array. Contract order is the
same as the canonical operation catalog, making generation and review
deterministic.

The operation inputs and output result are copied from the canonical operation
definition. Contract text adds behavioral meaning but does not rename or
redesign canonical operations.

Each contract has exactly one canonical-operation identifier field, `operation`.
It uses the same identifier values as `catalog/operations/core.json`; no
parallel `operation_id` field is present.

## Outcome vocabulary

Every contract uses values from this closed vocabulary:

| Outcome | Meaning |
| --- | --- |
| `success` | The operation completed with a valid canonical result or terminal outcome. |
| `unsupported` | The adapter does not provide the operation. |
| `invalid-request` | Canonical input violates the operation contract. |
| `host-failure` | The host rejected or could not complete the operation. |
| `disconnected` | The caller connection became unusable. |

An adapter SHALL fail explicitly and MUST NOT fabricate success. Unsupported
behavior SHALL be discoverable from a future Capability Declaration and SHALL
also be explicit if the operation is invoked.

## Lifecycle semantics

The catalog distinguishes four lifecycle concepts for every operation, using a
non-applicable statement where the operation is not itself terminal:

- **normal completion** returns a successful operation result or returns
  control through `lifecycle.exit`;
- **disconnect** is the canonical terminal path after a connection becomes
  unusable;
- **carrier loss** is one cause of disconnect and is not normal completion;
- **implementation shutdown** is cleanup performed by an implementation and
  is not itself a canonical lifecycle outcome.

After disconnect is observed, blocking interactive work SHALL stop and the
adapter MUST NOT later report normal exit. `lifecycle.exit` and
`lifecycle.disconnect` are distinct canonical operations.

## Validation rules

Repository validation enforces:

- exactly one contract for every canonical operation;
- canonical operation existence and deterministic canonical ordering;
- unique operation identifiers and input names;
- exact canonical input names and output result kind;
- the closed outcome vocabulary and unique per-contract outcome values;
- required normative, unsupported, lifecycle, and obligation fields;
- known categories and lifecycle field names;
- rejection of unknown catalog, contract, input, output, and lifecycle fields.

The JSON Schema enforces the structural portion of these rules. The repository
validator performs cross-file canonical-operation checks that JSON Schema alone
cannot express.

## CLI

Installed and repository-local forms are equivalent:

```bash
ods contracts list
ods contracts show terminal.write
ods contracts show lifecycle.exit
ods contracts show terminal.write --json
ods contracts validate
```

`ods validate` and `ods validate --strict` also validate the committed contract
catalog. PR3 does not add a generator because the catalog is source-controlled
and not derived from implementation data.

## Relationship to profiles and declarations

Compatibility Profiles define capability targets; Adapter Contracts define
operation behavior. A future Capability Declaration will identify an
implementation’s claimed profile and report operation statuses against these
contracts.

Historical `verified`, `partial`, and `unassessed` mappings remain evidence
statuses. They do not become contract outcomes. A verified mapping may support
a host translation, a partial mapping carries limitations, and an unassessed
mapping neither proves nor disproves implementation capability.

Capability Declaration schema and runtime conformance examples are future
M6.3 work; they are intentionally outside PR3.
