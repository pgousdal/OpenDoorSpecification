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

