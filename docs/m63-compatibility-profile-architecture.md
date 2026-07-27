# M6.3 PR1 — Compatibility profiles and adapter contract architecture

## Status and scope

This document defines the language-neutral architecture for M6.3. It specifies
concepts and normative relationships, not a serialization format, programming
interface, runtime, or adapter implementation.

ODS remains a specification and evidence-catalog project. DoorForge and other
runtimes may consume these contracts, but their implementation architecture is
outside this repository.

## Normative language

The key words **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **MAY**, and
**MUST NOT** are to be interpreted as normative requirement levels consistent
with RFC 2119. **SHALL** expresses the same mandatory requirement level as
**MUST**. **SHOULD** permits a documented exception when its consequences are
understood. **MAY** denotes a genuinely optional choice. **MUST NOT** and
**SHALL NOT** express an absolute prohibition.

Lowercase uses of these words are descriptive.

## Architectural layers

The architecture separates three concerns:

1. a **Compatibility Profile** defines a capability target in canonical ODS
   terms;
2. an **Adapter Contract** defines the language-neutral behavior every adapter
   exposes at the ODS boundary;
3. a **Capability Declaration** states what one implementation provides
   against a profile and contract.

These layers depend on canonical operations but do not redefine them.
Historical host mappings supply evidence about possible translations; they do
not themselves constitute an implementation or declaration.

```text
canonical operations
        |
        +--> compatibility profile (capability target)
        |
host evidence --> adapter contract (behavioral obligations)
                         |
                         +--> capability declaration (implementation claim)
```

## Compatibility Profile

A Compatibility Profile is a versioned, implementation-independent capability
target. It describes which canonical operations form a useful interoperability
level and the conditions under which an implementation may claim that level.

A profile SHALL identify:

- the profile and profile version;
- the ODS specification version it targets;
- required canonical operations;
- optional canonical operations;
- canonical operations intentionally outside the profile;
- compatibility expectations that apply across its operations;
- the evidence required for a conformance claim.

The three operation sets SHALL be pairwise disjoint. Every operation named by a
profile SHALL resolve to the targeted canonical operation catalog. A profile
MUST NOT create host-specific aliases or redefine canonical semantics.

The profile-supported operation set is the union of required and optional
operations: these are the capabilities the profile knows how to describe.
Operations intentionally outside the profile are its profile-unsupported set.
This classification describes the profile boundary only; it does not assert
what any particular implementation supports.

### Required operations

An implementation claiming a profile SHALL fully support every required
operation. A partial operation does not satisfy a required operation unless a
future profile definition explicitly permits a named, testable limitation.

### Optional operations

Optional operations belong to the profile's capability vocabulary but are not
required for the base claim. An implementation MAY declare each optional
operation as supported, partial, or intentionally unsupported.

### Operations outside the profile

An outside-profile operation is not required or implied by the profile.
Implementations MAY provide such operations as extensions, but MUST NOT imply
that the profile guarantees them.

### Compatibility expectations

Profile-wide expectations define observable qualities such as deterministic
capability discovery, lifecycle safety, disconnect propagation, text and
identifier normalization, and explicit unsupported-operation behavior.
Profiles describe these outcomes, not implementation techniques.

### Evidence requirements

A profile SHALL state the evidence needed to substantiate a claim. Evidence may
include contract tests, reproducible integration tests, declaration
validation, and—when translating a historical host—reviewed mapping
provenance. A profile MUST NOT treat host identity or an unreviewed similarity
as evidence of support.

### Relationship to existing conformance profiles

The M4.6 `minimal`, `interactive`, and `complete` profiles are the existing
cumulative required-operation baseline in
`catalog/profiles/conformance.json`. M6.3 SHALL preserve their identifiers and
requirements unless a later, explicitly versioned specification change says
otherwise.

M6.3 extends the architecture around that baseline. PR1 does not change the
current profile artifact, conformance report, CLI, or tests. Later schema work
will decide how existing records acquire the additional optional,
outside-profile, expectation, and evidence concepts without silently changing
their meaning.

## Adapter Contract

An Adapter Contract is the language-neutral behavioral boundary between a door
application and a host integration. It is expressed only through canonical
operation identifiers, canonical inputs and results, defined outcomes, and
lifecycle rules.

The contract SHALL NOT prescribe functions, methods, calling conventions,
memory layouts, transport protocols, or language-specific types.

### Operation identity and semantics

Each adapter operation SHALL use the exact canonical operation ID and preserve
the semantic expectation in the targeted ODS operation catalog. An adapter
MUST NOT expose a nearby host behavior as the canonical operation when known
limitations change its meaning.

Host-specific commands, fields, encodings, units, result codes, and structures
SHALL be translated at the adapter boundary. They MAY remain visible in
diagnostic evidence, but MUST NOT replace canonical results.

### Outcomes

Every operation attempt SHALL have one deterministic outcome:

- **success**: the canonical result or terminal lifecycle outcome occurred;
- **unsupported operation**: the implementation does not provide the
  operation;
- **invalid request**: the supplied canonical input violates the operation
  contract;
- **host failure**: the host rejected or could not complete the operation;
- **disconnect**: the caller connection became unusable.

A future schema may assign stable machine-readable outcome identifiers. PR1
defines only their semantic distinction.

An adapter SHALL surface failures and MUST NOT fabricate successful canonical
results. Unsupported behavior SHALL be discoverable from the capability
declaration and SHALL also fail explicitly if invoked. A required profile
operation MUST NOT report unsupported.

### Disconnect semantics

Connection loss SHALL be surfaced by every operation whose canonical
`disconnect_behavior` requires it. Once disconnect is observed:

- blocking interactive work SHALL stop promptly;
- no later terminal operation may report ordinary success;
- the adapter SHALL enter the `lifecycle.disconnect` path;
- cleanup SHALL preserve the disconnect reason where the host exposes one;
- the session MUST NOT subsequently report normal `lifecycle.exit`.

An adapter SHOULD make repeated cleanup requests safe, but it SHALL expose only
one terminal lifecycle outcome for a session.

### Normal exit semantics

`lifecycle.exit` SHALL return control to the host through its documented normal
completion path and SHALL preserve the canonical status when the host contract
can represent it. After normal exit begins, new interactive operations MUST NOT
start. Normal exit MUST NOT be used to hide a known disconnect or host failure.

### Implementation obligations

An implementation claiming an Adapter Contract SHALL:

- publish a Capability Declaration before operations are relied upon;
- keep runtime behavior consistent with that declaration;
- normalize host encodings, units, identifiers, and error states;
- preserve required lifecycle and disconnect behavior;
- provide the evidence required by its claimed profile;
- report partial behavior and limitations explicitly;
- fail deterministically for unsupported operations.

It SHOULD keep host-specific diagnostics available for investigation. It MAY
offer extensions outside ODS, but extensions MUST NOT collide with canonical
operation IDs or alter canonical semantics.

## Capability Declaration

A Capability Declaration is a versioned statement made by one implementation.
It answers which profile and specification are targeted and what the
implementation actually provides. It is a claim suitable for deterministic
validation, not evidence by itself.

A declaration SHALL identify:

- the implementation and declaration version;
- the targeted ODS specification version;
- the claimed Compatibility Profile and profile version;
- each declared canonical operation;
- the status of each operation;
- limitations for every partial operation;
- conformance evidence references required by the profile.

The declaration status vocabulary is:

- **supported**: the implementation fulfills the canonical operation contract;
- **partial**: defined behavior exists, but a stated limitation prevents full
  support;
- **unsupported**: the implementation intentionally does not provide the
  operation.

These are implementation capability statuses. They are distinct from
historical mapping statuses such as `verified`, `partial`, and `unassessed`.

For a profile claim:

- every required operation SHALL be declared supported, except where the
  profile explicitly permits a named partial limitation;
- every optional operation SHALL be declared supported, partial, or
  unsupported;
- duplicate or contradictory operation declarations MUST NOT occur;
- declared operation IDs SHALL resolve to the targeted canonical catalog;
- declaration evidence SHALL satisfy the profile's evidence policy.

An implementation MAY declare extensions outside the profile. Such extensions
SHALL be clearly separated from the profile claim.

## Relationship to M6.2 evidence

M6.2 records what historical primary evidence establishes. M6.3 defines what an
implementation must claim and do. The relationship is intentionally
one-directional:

- a `verified` host mapping provides strong provenance for translating that
  host behavior, but does not prove that an adapter implementation is correct;
- a `partial` host mapping exposes a known evidence or semantic limitation. An
  adapter may declare the operation partial, or may supply and validate the
  missing behavior through another documented mechanism;
- an `unassessed` mapping makes no support claim. It neither establishes nor
  disproves capability;
- the research backlog identifies evidence work that may strengthen future
  host-specific declarations;
- provenance validation ensures that reviewed historical claims remain
  inspectable.

Compatibility Profiles are defined over canonical operations, so unassessed
historical mappings do not prevent profile creation. They only prevent a
host-specific implementation from treating the absent review as evidence.

An implementation targeting a host with an unassessed mapping MAY still
support the operation if it supplies independent, reviewable implementation
and host evidence. It MUST NOT infer support solely from profile membership,
host name, queue priority, or triage confidence.

## Deterministic validation model

Future validation can evaluate a declaration without executing implementation
code:

1. resolve the declared specification and profile versions;
2. verify that all operation IDs are canonical and unique;
3. compare required, optional, and outside-profile sets;
4. reject missing or partial required operations not permitted by the profile;
5. require limitations for every partial declaration;
6. verify evidence references against the profile policy;
7. reject contradictions between profile, declaration, and evidence.

Runtime conformance remains a separate layer that tests whether actual behavior
matches the valid declaration and Adapter Contract.

## Boundaries for later M6.3 PRs

PR1 deliberately does not define:

- JSON schemas or artifact locations;
- new CLI commands or validation behavior;
- profile serialization or inheritance syntax;
- language bindings or runtime APIs;
- implementation-specific packaging;
- new canonical operations or historical mappings.

Those decisions belong to the planned M6.3 schema, CLI, example, and acceptance
PRs.

## Questions for PR2

The Compatibility Profile schema PR must resolve:

- the artifact path, schema identifier, and independent profile/specification
  version fields;
- whether every canonical operation must appear in exactly one profile set or
  whether omitted operations are implicitly outside the profile;
- how the current `minimal`, `interactive`, and `complete` records acquire
  optional and outside-profile sets without breaking existing consumers;
- whether profile extension is represented by inheritance or by fully expanded
  operation sets;
- the controlled vocabulary for evidence requirements and compatibility
  expectations;
- how a profile names an explicitly permitted partial limitation for an
  otherwise required operation.

PR2 SHOULD prefer explicit, deterministic data over implicit defaults while
preserving the current profile identifiers and required-operation semantics.
