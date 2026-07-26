# M2.2 forensic archive analysis

M2.2 adds six unique historical archives and records two uploaded byte-identical duplicates without duplicating the catalog.

## Strongest new evidence

`max_e.lha` contains Amiga E source for a MAXs door and exposes the concrete message-passing contract used by MAXs-compatible doors. It verifies the `DoorControl<N>` and `DoorReply<N>` port naming convention, the message layout, commands 1, 6, 8, 9, 10, 11, 13, 14 and 20, and carrier propagation after each reply.

`parod123.lha` documents a DLG-hosted Paragon interpreter. It confirms that Paragon doors are message-passing programs, that ParoD supports commands through 21, and that some features are deliberately unsupported or approximated.

`DoorRunner(1).lha` is byte-identical to the already cataloged `DoorRunner.lha`. `door_io12(1).lha` is likewise byte-identical to `door_io12.lha`; neither is added twice.

## Supporting archives

- `Life1_2.lha` documents a utility for recovering hung MAXs/Paragon doors.
- `HydraBBSdc.lha` is descriptive material for Hydra BBS door coding, not a complete SDK.
- `fprun11.lha` contains an ARexx door runner and demonstrates a separate script-driven integration style.
- `par2dlg.lha` is a migration utility bundle; it is relevant historically but does not expose the Paragon door ABI.

## Result

The Paragon mapping is upgraded from two provisional capabilities to seven reviewed mappings. Unknown command semantics remain unknown; ODS does not infer commands 2–5, 7, 12, 15–19 or 21 solely from numbering.
