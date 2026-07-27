# Open Door Specification

Open Door Specification (ODS) is an implementation-neutral specification and evidence-backed catalog for BBS door interfaces. The initial research corpus focuses on Amiga BBS systems.

## Current status

The repository is in the M4 architecture-baseline phase. It contains an evidence-backed historical catalog, ODS Core 0.1, host and DayDream reference adapters, and repository validation. It does not claim binary compatibility where ABI evidence remains incomplete.

## Quick start

```bash
python -m pip install -e tools/ods-tools
ods inventory path/to/sdk.lha
ods validate
ods list-archives
```

## Architecture

The normative specification is the primary product. Historical catalogs, the toolkit, and reference adapters support it without silently redefining it. See [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Principles

- specification-first
- implementation-neutral
- evidence-backed
- machine-readable
- testable
- preservation-oriented

DoorForge is planned as a reference implementation, but ODS is independent of DoorForge.

## Semantic inspection

```sh
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools inspect terminal.write
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools compare abbs daydream ambos
```

Canonical knowledge model: [`docs/canonical-knowledge-model.md`](docs/canonical-knowledge-model.md)

## Provenance coverage

```sh
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools coverage
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools validate --strict
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools operations
```

See [`docs/provenance-coverage.md`](docs/provenance-coverage.md).

### Adapter and historical API gaps

```sh
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools gaps
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools gaps api:daydream
```

## Adapter conformance profiles

ODS defines cumulative `minimal`, `interactive`, and `complete` adapter profiles. Inspect them with:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools profiles
```

See [docs/m46-conformance-profiles.md](docs/m46-conformance-profiles.md).


### Executable conformance

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools conformance
```


## Complete API census

The machine-readable historical API census starts at `catalog/census/index.json`.

<!-- m61-api-crosswalk -->
## API crosswalk

The M6.1 crosswalk records reviewed evidence between historical door/BBS host
APIs and nine canonical ODS operations.

```bash
ods crosswalk
ods crosswalk paragon
ods crosswalk terminal.write
ods crosswalk --coverage
ods crosswalk --gaps
ods crosswalk --work-queue
ods crosswalk --work-queue --priority high
ods crosswalk --completion
ods crosswalk --backlog
ods crosswalk ucdoor terminal.write --evidence
ods crosswalk --validate-evidence
ods validate
```

`unassessed` means that no reviewed mapping is currently recorded; it does not
mean unsupported. See [M6.1 API crosswalk](docs/m61-api-crosswalk.md).
The [M6.2 evidence work queue](docs/m62-crosswalk-work-queue.md) prioritizes
future research; priority is not a support claim.
Reviewed mappings must satisfy the
[M6.2 provenance requirements](docs/m62-evidence-provenance-validation.md).
The [M6.2 completion report](docs/m62-completion.md) separates completed
milestone work from deferred research and archival source discovery.
