# Roadmap

## Current state

M6.2 is complete. The generated
`catalog/crosswalk/m62-completion.json` report has no completion blockers and
classifies every remaining unassessed cell as deferred research or archival
source discovery.

The repository is ready to scope M6.3. No M6.3 evidence target is selected by
this maintenance refresh; future work should start from
`ods crosswalk --backlog`.

## Next milestone — M6.3

Status: planning.

M6.3 should consume stable backlog IDs rather than reopening completed
milestones. Candidate work falls into two generated classes:

- deferred semantic or historical research;
- archival and primary-source discovery.

Selection must continue to prioritize primary evidence. An unassessed mapping
is not unsupported, and backlog priority or confidence is not a support claim.

## Research backlog

The source of truth is `catalog/crosswalk/m62-completion.json`, inspected with:

```bash
ods crosswalk --completion
ods crosswalk --backlog
ods crosswalk --backlog --json
```

Backlog grouping, expected value, affected hosts and operations, research
effort, and recommended future milestone are generated from the queue and
triage. The roadmap intentionally does not duplicate those changing totals.

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
the M6.3 research backlog.
