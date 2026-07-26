# Paragon/StarNet compatibility — current findings

## Verified from DoorRunner 1.30

- DoorRunner targets MAX's BBS and Paragon/StarNet-compatible BBS systems.
- It permits doors written in languages without native Amiga message-port support.
- `DoorRunner` must reside in `C:` and `T:` must be assigned.
- Doors are launched as normal BBS doors; the documented MAX's example uses function 34 and the compiled door pathname.
- Version 1.20 claims support for all MAX's/Paragon/StarNet door commands in the Amiga E source.
- New BBS commands can be exposed by adding a language-side procedure without changing DoorRunner itself.

## Interpretation

This strongly indicates that DoorRunner is a bridge from language-friendly procedures to the BBS door message-port command set. Exact message layouts and every command signature remain subject to extraction from the included E and Blitz examples.

## Compatibility status

`research`: launch behavior and bridge purpose are verified; binary ABI compatibility has not yet been runtime-tested.
