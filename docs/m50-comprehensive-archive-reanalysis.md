# M5.0 Comprehensive archive reanalysis

M5.0 repeats the analysis of every archive supplied for this milestone, including byte-identical copies that had already been inspected in earlier work. Previous conclusions were not used as substitutes for re-reading the payloads.

## Method

- Recomputed SHA-256 for every upload.
- Parsed all LHA/LZH headers and ZIP entries.
- Extracted all `-lh0-` and `-lh5-` members.
- Scanned text, C, assembler, Amiga E, AMOS, ARexx, FD and guide material.
- Recorded `-lh1-` members without inventing source-level findings where decompression was unavailable.
- Kept documented, observed, inferred and unavailable evidence separate.

## Coverage

| Archive | Entries | Extracted | Distribution | File census | Observed command numbers | Selected symbols |
|---|---:|---:|---|---|---|---|
| `MAXsGUiDE(1).lha` | 4 | 4/4 | yes | documentation:3, other:1 | — | — |
| `MAXShell101(1).lha` | 15 | 15/15 | yes | c:3, documentation:4, library:1, other:7 | 1, 3, 4, 5, 6, 8, 10, 13, 14, 20, 200, 201, 203 | DoorMsg, DoorControl, DoorExample, DoorReply |
| `mAG-cH_11(2).lha` | 12 | 12/12 | yes | documentation:6, other:6 | — | — |
| `M_Quest_v11(1).lha` | 5 | 5/5 | yes | documentation:1, other:4 | — | — |
| `ax300(1).lzh` | 116 | 5/116 | yes | c:2, other:2 | — | — |
| `acp300(1).lzh` | 34 | 0/34 | yes | not decoded | — | — |
| `MAXs_Coders(1).lha` | 5 | 5/5 | yes | documentation:4, other:1 | — | — |
| `MaxPro2(1).lha` | 36 | 36/36 | yes | documentation:2, other:34 | — | — |
| `MaxRexx(1).lha` | 66 | 66/66 | yes | arexx:15, documentation:2, other:49 | — | DoorStarterr |
| `DayDreamBBSDoo(1).lha` | 9 | 9/9 | yes | documentation:1, other:8 | — | mxK |
| `DayDreamBBS(1).lha` | 193 | 193/193 | yes | arexx:4, documentation:50, library:3, other:136 | 1, 2, 3, 4, 101 | DDCallers, DDDP, DDTop, DDHydra, DDWeekTop, BBSNAME |
| `DayDreamBBSDev(3).lha` | 69 | 69/69 | yes | amiga-e:6, asm:7, c:13, documentation:9, fd:2, other:32 | 0, 10, 13, 27, 250, 251 | DDBase, DDDOOR_BASE_NAME, DDCommand, DDPointers, DDF_SHOWERROR, DDLibBase |
| `ZeusDoors(1).lha` | 136 | 136/136 | yes | arexx:2, c:13, documentation:35, other:86 | — | — |
| `WWBBSDoors(1).lha` | 102 | 102/102 | yes | arexx:21, documentation:9, other:72 | — | BBSIDENTIFY, DDOWN, BBSNAME |
| `MaxsAmosDoors(1).lha` | 15 | 15/15 | yes | amos:15 | — | — |
| `DoorStatus(1).lha` | 5 | 5/5 | yes | documentation:1, other:4 | — | DoorStatusClient, DoorStatusServer |
| `Mdoors5(1).lha` | 6 | 6/6 | yes | other:6 | — | BBSCMD, BBSCmd, AXHLML |
| `Mdoors4(1).lha` | 16 | 16/16 | yes | other:16 | — | BBSCmd |
| `Mdoors3(1).lha` | 12 | 12/12 | yes | other:12 | — | BBSCmd, DDG |
| `preservation-abbs20-master.zip` | 246 | 238/246 | new | arexx:3, asm:51, c:72, documentation:28, other:84 | 0, 1, 2, 3, 4, 5, 6, 7, 13, 20, 21, 27, 32, 65, 66, 113 | ABBS, ABBSUserEditorWnd, ABBSmsg, ABBSUserEditorGadgets, ABBSUserEditorMenus, ABBSAppWindowWnd |

## Main conclusions

### DayDream

The developer archive is the authoritative source in this batch. It contains C headers, FD files, assembler includes, Amiga E modules, examples and the DreamDoor documentation. The analysis confirms `DDCommand`, `InquirePointers`, `DIFace`, `DDPointers`, the `DD_DoorPort` message-port convention and a broad native library ABI. The runtime and door packs corroborate actual deployment and ARexx use.

### MAXs / Paragon

`MAXShell101` provides direct C-source evidence for the DoorMsg layout and commands 1, 6, 8, 10, 13, 14, 20, 200, 201 and 203, plus other internal command values. `MaxRexx`, `MaxPro2`, `mAGNUM cHAT`, `Multi-Quest`, the AMOS sources and Mdoors collections demonstrate a large multi-language ecosystem rather than a single SDK-only interface.

### ABBS

The newly supplied preservation snapshot adds a complete source-tree primary source: 238 files, including 72 C and 51 assembler files. It directly exposes node-local state, serial/carrier handling, transfer logic, user handling and BBS internals. It corroborates the already documented ARexx-facing mappings, but M5.0 deliberately does not redefine internal ABBS routines as a public door ABI.

### Zeus and WWBBS

Both are substantial door collections. Zeus contains C source and extensive door documentation; WWBBS contains a large ARexx-oriented collection. They are valuable implementation corpora, but do not by themselves establish a new common ABI without a separately documented host contract.

### ACP and AX

The archives are byte-identical to the earlier copies. ACP is entirely `-lh1-`; AX is predominantly `-lh1-` with only five members decoded by the current extractor. M5.0 therefore records complete manifests and file-level research targets while refusing to promote guessed API semantics.

## Preservation result

Nineteen LHA/LZH uploads are byte-identical redistributions of previously catalogued archives. They remain listed in the reanalysis report because their contents were independently reprocessed. `preservation-abbs20-master.zip` is the one new canonical source archive and raises the repository catalogue to 30 archives and 1,150 entries.
