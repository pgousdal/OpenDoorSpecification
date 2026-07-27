# M4.8 — MAXs documentation and source expansion

M4.8 adds three primary-source archives to the historical catalog and records only claims that were verified from extracted archive contents.

## Archives

### MAXs_Coders.lha

A 1998 AmigaGuide directory of MAXs door coders and contributors. It is useful ecosystem context, but it is not an ABI or SDK and therefore adds no semantic mappings.

The uploaded `MAXs_Coders (1).lha` is byte-identical to the previously supplied `MAXs_Coders.lha` and is recorded as a duplicate distribution.

### MAXsGUiDE.lha

Contains a large MaxsBBS operator guide. It documents BBS configuration and operation, including AutoInsert material, but the focused source/API review did not find a source-level door contract suitable for a new mapping.

### MAXShell101.lha

Contains full C source and documentation for MAXShell 1.01, a MAXs BBS Function 34 door that runs CLI applications through `fifo.library`.

`MAXShell.c` directly declares the historical message layout:

```c
struct DoorMsg {
    struct Message Door_Msg;
    short command;
    short data;
    char string[80];
    short carrier;
};
```

The source observes these protocol commands:

| Command | Observed use |
|---:|---|
| 1 | terminal output |
| 6 | line prompt/input |
| 8 | hotkey input |
| 10 | show file |
| 13 | read numeric user field |
| 14 | read string user field |
| 20 | orderly door termination |
| 100+ | invoke BBS menu functions |
| 200 | change numeric user field |
| 201 | key/check operation |
| 203 | additional BBS operation |

The accompanying documentation also confirms Function 34 invocation, AutoInsert substitution, remaining-time adjustment, FIFO-based remote CLI operation, and lost-carrier handling.

## Evidence boundary

M4.8 does not introduce a new API family or alter existing semantic mappings. MAXShell strengthens the existing Paragon/MAXs evidence base with another independent, complete source implementation.
