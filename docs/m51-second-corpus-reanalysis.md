# M5.1 — Second comprehensive archive reanalysis

M5.1 reprocesses a second batch of 20 supplied LHA archives from raw bytes. Every
upload is byte-identical to a canonical archive already present in the research
set, but each payload was unpacked and inspected again rather than being skipped
because of its duplicate status.

## Method

For every archive the analysis recomputed SHA-256, parsed all LHA headers,
unpacked every supported `-lh0-` and `-lh5-` payload, classified files, and
scanned readable source and documentation for API symbols, message commands,
structures, includes and lifecycle terminology. Claims are bounded by the
available source: command numbers are reported as observed unless their semantic
meaning is independently documented.

## Corpus result

- 20 uploads reprocessed.
- 20 byte-identical redistributions confirmed.
- 594 archive entries inspected.
- 590 payload files extracted; the difference consists of directory entries.
- No new canonical archive IDs were introduced.
- No semantic mapping was promoted solely from duplicate evidence.

## MAXs and Paragon

The strongest source corpus consists of `ArisDoors4MAXs`, `MCesrc`,
`CDoorExample`, and `max_e`.

`CDoorExample` gives a compact C example of the `DoorMsg` message layout and
commands 1, 6, 8, 10, 14, 20 and 200. `MAXDoor.e` independently implements
DoorControl/DoorReply IPC and wrappers for commands 1, 6, 8, 9, 10, 11, 13, 14,
20 and 200. `MagnumChat.e` contains a significantly broader wrapper set,
including commands 1–21, many 101–138 values and 200–202.

The 206-entry Aris corpus is especially valuable because it contains 63 C files
and repeated real-world use of DoorMsg-based terminal, input, user-data, BBS
command and exit behavior. Numeric values found in application source are not
all promoted to normative semantics: observed usage and documented meaning
remain separate evidence categories.

## FAME

`fcomm` and `fcomm130` are substantial command-reference distributions. They
corroborate a FAME-specific `FAMEDoorMsg`/`FAMEDoorPort` model and document
structured operations for conferences, mail, users and external editors.
`fame_dh` provides the related door-header integration material, while `fprun11`
shows an ARexx-oriented launcher path.

This confirms that FAME is not merely another spelling of the MAXs protocol. It
has its own command and data model and should remain a distinct historical API
family.

## AmBoS

The three AmBoS packages provide mutually reinforcing bindings:

- `AmBoS_doc_dev` contains the developer guide, C headers and FD file.
- `BBSLib-Asm` exposes assembler offsets and BBSBase/BBSMenu symbols.
- `AmBoS_mod_E` exposes Amiga E structures for users, transfers, files, boards
  and menus.

Together these are strong primary evidence for a typed `BBS.library` interface.
They also demonstrate why ODS must distinguish callable-library APIs from
message-port protocols.

## AmiExpress/AEDoor and door_io.library

`aedoor28` is a multi-language SDK with C, assembler and Amiga E material and an
extensive numeric command table. Those command numbers belong to AEDoor's own
protocol namespace and must not be interpreted using MAXs meanings.

`door_io12` contains a library binary, FD declarations, C bindings and
reference documentation. It confirms a narrow Amiga shared-library API rather
than a DoorControl/DoorReply message protocol.

## ABBS

`ABBS320_999` is a 222-entry ABBS 3.20 distribution with documentation, C,
Amiga E, ARexx and library components. It confirms a broad extension ecosystem,
but it is not the same evidence object as the complete preserved ABBS 2.0 source
snapshot introduced in M5.0. Distribution documentation and internal source
must remain separately cited.

## Documentation-only and launcher material

`runraw`, `HydraBBSdc`, `parod123`, `par2dlg`, `Life1_2`, and `DoorRunner` are
useful for deployment, compatibility and lifecycle context. They do not all
contain source-level host API implementations, so M5.1 does not manufacture new
mappings from them.

## Evidence decision

The reanalysis strengthens confidence through independent reprocessing and
cross-language corroboration, but byte-identical copies do not count as
independent primary sources. Consequently, archive totals and provenance totals
remain unchanged. The main deliverable is a reproducible, machine-readable
research record and a clearer separation between documented semantics,
observed command values and contextual ecosystem evidence.
