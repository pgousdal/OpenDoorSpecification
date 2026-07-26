# Open Door Specification 0.1 — Core Working Draft

ODS defines a portable door-session contract between a door application and a host adapter.
The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

## Conformance

An **ODS Core adapter** MUST implement every operation marked `core` in
`catalog/operations/core.json`. Optional operations MUST be discoverable before use.
A door MUST NOT infer support from a historical host name alone.

## Errors and disconnects

Terminal and host-command operations MUST surface carrier loss or equivalent connection
failure. After a disconnect is observed, a door MUST stop interactive work and invoke the
`lifecycle.disconnect` path without further blocking terminal I/O.

Historical return codes remain adapter concerns. For ABBS, return code 20 is preserved as a
verified disconnect invariant; ODS represents the event semantically rather than assigning
that numeric value globally.

## Data model

Text is Unicode at the ODS boundary. An adapter is responsible for conversion to the host
encoding. Node identifiers and user identifiers are opaque values and MUST NOT be
renumbered by the portable door layer.
