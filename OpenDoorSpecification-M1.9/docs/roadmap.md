# Roadmap

## M0 — Repository foundation

- project structure
- contribution and evidence rules
- initial schemas and validation
- unified `ods` CLI

## M1.6 — API extraction

- archive inventories
- `.fd` parser
- C header declaration parser
- Amiga E and assembler symbol extraction
- guide/document indexer
- evidence manifests

## M1.7 — API comparison

- normalized capability mappings
- generated comparison matrix
- equivalent and unique operations

## M1.8 — ODS Core 0.1

- session
- terminal
- lifecycle
- status
- optional file/message/storage services

## M1.9 — Adapter contracts

- ABBS
- Paragon/StarNet
- DayDream
- AmiExpress/AEDoor
- AmBoS
- door_io.library
- FAME DoorPort
- generic CLI/stdio

## M1.9 — Reference adapter

Status: complete.

- Deterministic host/simulator adapter for all ODS Core 0.1 operations.
- Machine-readable execution transcripts.
- Disconnect and normal-exit conformance behavior.

## M2.0 — First historical adapter

Next: implement one verified historical adapter, beginning with ABBS or DayDream,
and execute shared conformance cases against both it and the host adapter.
