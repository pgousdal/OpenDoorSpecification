# Open Door Specification

Open Door Specification (ODS) is an implementation-neutral specification and
evidence-backed catalog for BBS door interfaces. The historical corpus
currently focuses on Amiga BBS systems. ODS specifies and catalogs interfaces;
it does not implement a BBS, and DoorForge remains a separate reference
implementation.

## Current status

M6.3 is complete. PR1 defined the language-neutral architecture for
Compatibility Profiles, Adapter Contracts, and Capability Declarations. PR2
added the Compatibility Profile schema and catalog. PR3 added the Adapter
Contract schema and canonical contract catalog. PR4 added the Capability
Declaration schema, reference catalog, and CLI commands. PR5 added
deterministic cross-model validation between declarations, profiles, and
contracts. PR6 performed the final milestone review and documentation
consistency update.

M6.2 is complete. The repository contains ODS Core 0.1, deterministic archive
and API catalogs, reference adapters, executable conformance checks, a complete
host-operation crosswalk, strict evidence provenance validation, and a
classified research backlog for future evidence milestones.

The current generated completion state is
`catalog/crosswalk/m62-completion.json`. Remaining `unassessed` cells are
research backlog items, not claims of unsupported behavior.

## Principles

- specification-first and implementation-neutral;
- evidence-backed and machine-readable;
- deterministic and testable;
- preservation-oriented;
- conservative about incomplete historical evidence.

The normative specification is the primary product. Catalogs, research tools,
and adapters support it without silently redefining it. See
[Architecture](docs/architecture.md) and the
[research methodology](docs/research-methodology.md).

## Repository structure

| Path | Purpose |
| --- | --- |
| `spec/` | Normative ODS specification text |
| `catalog/` | Archives, APIs, mappings, provenance, census, and generated reports |
| `schemas/` | JSON schemas for machine-readable repository data |
| `tools/ods-tools/` | Installable Python CLI package |
| `tools/generate_*.py` | Deterministic crosswalk generators |
| `native/` | Native adapter sources |
| `examples/` | Host-simulator scenarios |
| `docs/` | Architecture, milestone, evidence, and contributor documentation |
| `tests/` | Repository-wide regression and acceptance tests |

Directories named `OpenDoorSpecification-*` are preserved historical
snapshots. Current development uses the top-level paths above.

See the [documentation index](docs/README.md) for current guidance and
historical milestone records.

## Installation

Python 3.11 or newer is required.

```bash
python3 -m pip install -e tools/ods-tools
ods validate
```

Commands can also run directly from a checkout without installation:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate
```

## CLI overview

```bash
ods list-archives
ods inventory path/to/sdk.lha
ods inspect terminal.write
ods compare abbs daydream ambos
ods coverage
ods operations
ods gaps
ods profiles
ods contracts list
ods contracts validate
ods capabilities list
ods capabilities show host-simulator
ods capabilities validate
ods conformance
ods simulate examples/host-simulator/hello.json --transcript
ods validate
ods validate --strict
```

Use `ods --help` and `ods <command> --help` for the complete option set.

## Crosswalk and evidence workflow

The M6.1 crosswalk relates ten historical hosts to nine canonical operations.
M6.2 adds research ordering, evidence validation, triage, and milestone
completion semantics.

```bash
ods crosswalk
ods crosswalk paragon
ods crosswalk terminal.write
ods crosswalk --coverage
ods crosswalk --gaps
ods crosswalk --work-queue
ods crosswalk --work-queue --priority high
ods crosswalk --triage
ods crosswalk --triage --host ambos
ods crosswalk ucdoor terminal.write --evidence
ods crosswalk --validate-evidence
ods crosswalk --completion
ods crosswalk --backlog
ods crosswalk --backlog --json
```

Crosswalk terminology is deliberately strict:

- `verified`: direct evidence fully supports the canonical operation;
- `partial`: reviewed evidence supports only part of the operation or has a
  documented limitation;
- `unassessed`: no reviewed mapping is recorded;
- work-queue priority recommends research order, not support likelihood;
- triage confidence estimates whether sufficient evidence can be found, not
  whether support exists.

See the [M6.1 crosswalk](docs/m61-api-crosswalk.md),
[work queue](docs/m62-crosswalk-work-queue.md),
[provenance requirements](docs/m62-evidence-provenance-validation.md),
[triage methodology](docs/m62-evidence-triage.md), and
[completion and backlog workflow](docs/m62-completion.md).

## Compatibility architecture

M6.3 defines how future implementations can consume canonical ODS operations
without making ODS language- or runtime-specific:

- a Compatibility Profile defines an implementation-independent capability
  target;
- an Adapter Contract defines canonical behavioral and lifecycle obligations;
- a Capability Declaration states what one implementation supports, partially
  supports, or intentionally leaves unsupported.

PR1 provides the architecture, PR2 provides the profile catalog and
validation, PR3 provides the Adapter Contract catalog, PR4 provides the
Capability Declaration schema, PR5 adds deterministic cross-model
validation between declarations, profiles, and contracts, and PR6 completes
the milestone with a formal review and consistency update. See
[M6.3 compatibility profile architecture](docs/m63-compatibility-profile-architecture.md).
The [M6.3 profile schema and catalog](docs/m63-compatibility-profile-schema.md)
documents the current machine-readable profile model.
The [M6.3 Adapter Contract schema](docs/m63-adapter-contract-schema.md)
defines canonical operation behavior and outcomes.
The [M6.3 Capability Declaration schema](docs/m63-capability-declarations.md)
documents implementation capability declarations.
The [M6.3 capability validation](docs/m63-capability-validation.md)
documents cross-model validation between declarations, profiles, and contracts.
The [M6.3 milestone completion](docs/m63-completion.md)
summarizes the deliverables, architectural layering, and deferred work.

## Generators

Crosswalk JSON under `catalog/crosswalk/` is derived data. Edit the census or
classification source, then regenerate; do not hand-edit generated reports.

```bash
python3 tools/generate_crosswalk.py
python3 tools/generate_crosswalk_coverage.py
python3 tools/generate_crosswalk_work_queue.py
python3 tools/generate_crosswalk_triage.py
python3 tools/generate_crosswalk_completion.py
```

Every generator supports `--check`, which fails when its committed artifact is
missing or stale.

## Validation

Before submitting changes, run:

```bash
python3 tools/generate_crosswalk.py --check
python3 tools/generate_crosswalk_coverage.py --check
python3 tools/generate_crosswalk_work_queue.py --check
python3 tools/generate_crosswalk_triage.py --check
python3 tools/generate_crosswalk_completion.py --check

PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
python3 scripts/check-repository.py
```

Strict validation checks archive and provenance cross-references, generated
reports, conformance data, crosswalk evidence, queue/triage consistency, and
the M6.2 completion report.

## Contributing evidence

Record archive identity, SHA-256, exact internal path, concrete symbol or
protocol element, a concise rationale, and limitations for partial mappings.
Do not commit proprietary archives or full third-party documentation.

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Future evidence work should
select stable IDs from `ods crosswalk --backlog`, acquire or inspect primary
sources, update source data, regenerate all affected artifacts, and run normal
and strict validation.

## Roadmap

Completed milestones and milestone sequences are tracked in
[docs/roadmap.md](docs/roadmap.md).
