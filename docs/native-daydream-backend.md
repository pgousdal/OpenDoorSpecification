# Native DayDream backend

M2.1 introduces the first C implementation of a historical ODS adapter. It is
split into two layers:

1. `ods_daydream.c` implements ODS lifecycle, carrier checks, argument checks,
   buffer termination, and result normalization.
2. `ods_dd_bindings` is an ABI boundary populated by a compiler-specific file
   that calls the historical DreamDoor symbols.

This split is deliberate. The archive census verifies symbol names such as
`DDPutStr`, `DDGetKey`, `Prompt`, `GetAccount`, `TimeLeft`, `Carrier`,
`ChangeActivity`, `InternalCommand`, and `CloseDoor`, but the repository does
not yet have enough normalized evidence to publish one universal C prototype
for every supported historical compiler.

## Conformance rules

- Terminal reads, writes, and BBS commands check carrier first.
- Carrier loss becomes `ODS_DD_DISCONNECTED` and suppresses the requested I/O.
- Caller-provided line buffers are always NUL-terminated when capacity is
  non-zero.
- `session.node` remains launch context, not a guessed DreamDoor call.
- `lifecycle.exit` invokes the backend close operation exactly once per call.

The host test compiles the same adapter implementation against a fake binding
table. It verifies behavior but does not claim to emulate DayDream or AmigaOS.
