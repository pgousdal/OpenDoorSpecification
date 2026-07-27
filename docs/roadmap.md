# Roadmap

## Current state

M6.3 is in progress. PR1 established the language-neutral architecture for
Compatibility Profiles, Adapter Contracts, and Capability Declarations. PR2
added the Compatibility Profile schema, source catalog, and validation CLI.
PR3 adds the Adapter Contract schema and canonical catalog. Capability
Declaration schemas, examples, and acceptance criteria remain future M6.3
work.

M6.2 remains complete. Its generated research backlog is preserved for future
evidence milestones and is not modified by M6.3 architecture work.

## Active milestone — M6.3

Status: in progress.

M6.3 defines deterministic, implementation-independent contracts that future
runtimes can consume and validate. ODS remains a specification project; M6.3
does not introduce adapter runtime code.

Planned sequence:

- PR1: Compatibility Profile, Adapter Contract, and Capability Declaration
  architecture;
- PR2: Compatibility Profile schema and source catalog;
- PR3: Adapter Contract schema and canonical catalog;
- PR4: Capability Declaration schema;
- PR5: CLI validation;
- PR6: reference examples;
- PR7: acceptance criteria and M6.3 completion.

See [M6.3 compatibility architecture](m63-compatibility-profile-architecture.md).

## M6.2 research backlog

The source of truth is `catalog/crosswalk/m62-completion.json`, inspected with:

```bash
ods crosswalk --completion
ods crosswalk --backlog
ods crosswalk --backlog --json
```

Backlog grouping, expected value, affected hosts and operations, research
effort, and recommended future milestone are generated from the queue and
triage. The roadmap intentionally does not duplicate those changing totals or
fold evidence expansion into M6.3.

## Completed milestones

### M6.2 — Crosswalk evidence expansion

Status: complete.

- deterministic research work queue and priority explanations;
- evidence expansion batches using cataloged primary sources;
- strict provenance validation and CLI evidence inspection;
- deterministic triage by reason, effort, and confidence;
- machine-readable completion criteria and classified research backlog.

See [M6.2 completion criteria](m62-completion.md).

### M6.1 — API crosswalk

Status: complete.

- deterministic host and canonical-operation crosswalk;
- host and operation CLI lookup;
- evidence coverage and gap reporting;
- stale generated-data validation.

See [M6.1 API crosswalk](m61-api-crosswalk.md).

### M6.0 — Complete API census

Status: complete. See [M6.0 complete API census](m60-complete-api-census.md).

### M5.0–M5.2 — Archive reanalysis

Status: complete.

- comprehensive archive and source reanalysis;
- duplicate-distribution identification;
- AmiExpress, AmiX, MAXs, ABBS, and related corpus expansion.

See [M5.0](m50-comprehensive-archive-reanalysis.md),
[M5.1](m51-second-corpus-reanalysis.md), and
[M5.2](m52-comprehensive-amiexpress-reanalysis.md).

### M4.0–M4.9 — Architecture and conformance

Status: complete.

- specification/toolkit/catalog boundaries;
- canonical knowledge and provenance model;
- provenance coverage and canonical operation records;
- adapter gap reporting;
- cumulative and executable conformance profiles;
- historical corpus and MAXs source expansion.

See [architecture](architecture.md),
[canonical knowledge model](canonical-knowledge-model.md),
[conformance profiles](m46-conformance-profiles.md), and
[executable conformance](m49-executable-conformance-suite.md).

### M0–M2.3 — Foundation, core, and adapters

Status: complete.

- repository foundation and archive/API extraction;
- ODS Core 0.1 and historical adapter contracts;
- deterministic reference host adapter;
- DayDream portable and native adapter work;
- forensic analysis and historical door corpus.

See [ODS Core 0.1](ods-core-0.1.md),
[reference host adapter](reference-host-adapter.md),
[DayDream adapter](daydream-adapter.md), and
[historical door corpus](m23-historical-door-corpus.md).

## Future publication work

Generated reference documentation, public-site publication, and an ODS 1.0
release-candidate checklist remain future release work. They are separate from
the M6.2 evidence backlog and M6.3 compatibility-contract work.
