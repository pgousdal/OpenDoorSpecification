# M2.3 Historical Door Corpus

M2.3 adds five unique historical archives and one byte-identical duplicate. The catalog now separates three evidence classes:

- **documented** — stated by an SDK, guide, header, or autodoc;
- **observed** — present in historical source code;
- **inferred** — a conservative interpretation not directly stated by a source.

## Key findings

`ucdoor10.lha` contains a MAXs/Paragon-compatible C SDK, HTML reference, header, libraries, and a compiled/example door. Its `MDDOOR` structure independently confirms the 80-byte message string and carrier field.

`CDoorExample.lha` is a compact C implementation of the Paragon message protocol. It demonstrates the required command 20 shutdown handshake and actual use of commands 1, 6, 7, 10, 12, 14, 15, and 17.

`ArisDoors4MAXs.lha` contributes a large practical corpus: dozens of C door programs, a shared MAXs door header, AMOS bindings, and command implementations. This is treated as observed usage, not as a normative SDK by itself.

`MCesrc.lha` contains an Amiga E MAXs/Paragon door and demonstrates both classic commands and extended MAXs commands.

`runraw.lha` documents a door-launch utility. It is cataloged as launcher evidence but does not provide source-level BBS API calls.

The original archives are not redistributed by this repository. Only hashes, inventories, normalized observations, and source paths are recorded.
