# Open Door Specification

Open Door Specification (ODS) is an implementation-neutral specification and evidence-backed catalog for BBS door interfaces. The initial research corpus focuses on Amiga BBS systems.

## Current status

This repository foundation contains the M0 structure and the first M1.6 archive inventory. It does not yet claim binary compatibility with any historical API.

## Quick start

```bash
python -m pip install -e tools/ods-tools
ods inventory path/to/sdk.lha
ods validate
ods list-archives
```

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
