# Open Door Specification Architecture

## Mission

Open Door Specification (ODS) preserves and describes historical BBS door
interfaces as they actually existed, then maps them to a small modern,
implementation-neutral model.

ODS does not rewrite history into a single fictional API. Historical names,
structures, behavior, limitations, and uncertainty remain visible and traceable
to primary evidence. The normalized ODS layer exists to make comparison,
conformance testing, and new implementations possible.

## Primary product

The normative specification is the primary deliverable of this repository.
Tooling, catalogs, adapters, generated documentation, and examples support the
specification but do not define it independently.

## Product boundaries

ODS is organized conceptually as three products that share one repository.

### 1. Specification

The specification defines:

- canonical ODS operations and structures;
- required behavior and lifecycle rules;
- capability and conformance terminology;
- historical ABI descriptions where evidence is sufficient;
- extension points for behavior that cannot be normalized safely.

Normative content belongs under `spec/` and must use explicit normative language.

### 2. Toolkit

The toolkit reads and validates repository data. It may inventory archives,
extract symbols, inspect mappings, compare APIs, run simulations, and generate
reports. It must not silently promote an inference into normative truth.

Toolkit source currently belongs under `tools/ods-tools/`.

### 3. Reference implementations

Reference adapters and native examples demonstrate one possible implementation
of the specification. They are testable examples, not additional sources of
normative requirements.

Reference code currently belongs under `reference/`, `native/`, and `examples/`.
A later migration may consolidate these paths without changing their meaning.

## Architectural layers

The repository has six logical layers:

1. `spec/` — normative ODS definitions.
2. `catalog/` — historical facts, mappings, evidence, and archive metadata.
3. `schemas/` — machine-readable contracts for repository data.
4. `tools/ods-tools/` — extraction, inspection, validation, and generation.
5. `reference/`, `native/`, `examples/` — non-normative implementations.
6. `tests/` and `scripts/` — conformance and repository integrity checks.

Dependencies should point inward toward the specification and schemas:

```text
historical evidence -> catalog mappings -> ODS specification
                                      -> toolkit reports
ODS specification   -> reference adapters -> conformance tests
```

The specification must not depend on a specific adapter, compiler, BBS, or
archive parser.

## Evidence model

Every historical claim must use one of these evidence classes:

- `documented` — stated directly by an original SDK, guide, header, or manual;
- `observed` — present in historical source code or another concrete artifact;
- `inferred` — cautiously derived from surrounding evidence;
- `unknown` — insufficient evidence exists.

A claim may become stronger when new evidence appears. It must never become
stronger merely because an implementation assumes it.

Original third-party archives are research inputs. Repository data should store
hashes, inventories, quotations within legal limits, extracted facts, and
source locations rather than redistributing archives by default.

## Normative versus informative material

A file is normative only when it is under `spec/` and explicitly identified as
normative. Catalog entries, generated matrices, historical notes, examples, and
reference adapters are informative unless the specification incorporates them
by a stable identifier.

When normative text and generated output disagree, validation must fail or the
disagreement must be documented. Generated output must never override the
normative source silently.

## Compatibility principles

- ODS operations describe semantics, not historical symbol spelling.
- Several historical calls may map to one ODS operation.
- One historical call may require several ODS operations or an extension.
- Partial support must remain visible; it must not be reported as full support.
- Unknown ABI details remain unknown until evidence resolves them.
- ODS 1.x must preserve compatibility for stable operation identifiers and
  required behavior. Breaking changes require a major version.

## Repository migration policy

The current repository contains working paths used by tests and tooling. Major
moves must therefore be incremental:

1. define the target location and ownership of each artifact;
2. add compatibility readers or aliases where necessary;
3. move one category at a time;
4. update schemas, tests, documentation, and CLI paths together;
5. remove compatibility paths only in a separately documented change.

M4.0 establishes these boundaries but intentionally performs no disruptive file
moves.

## ODS 1.0 acceptance principles

ODS 1.0 should not be declared until:

- every core operation has a stable identifier and normative definition;
- every historical mapping has evidence and an explicit confidence state;
- schemas validate all normative and catalog data;
- generated documentation comes from the same data used by the toolkit;
- reference adapters report unsupported and partial capabilities honestly;
- one strict command validates repository integrity and conformance;
- no unresolved contradiction is hidden by the generated reports.

## Non-goals

ODS does not aim to:

- emulate an entire historical BBS;
- claim binary compatibility without verified ABI evidence;
- replace original SDK documentation;
- redistribute third-party archives automatically;
- force every historical feature into the portable core;
- make reference implementation behavior normative by accident.

## Decision rule

When a proposed change creates tension between historical accuracy, convenience,
and a cleaner abstraction, preserve the historical evidence first, state the
uncertainty, and keep the portable abstraction explicit and narrow.
