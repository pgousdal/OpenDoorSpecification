# M5.2 — Comprehensive AmiExpress, AmiX and MAXs reanalysis

M5.2 reanalyses all twelve uploaded archives from raw bytes, including archives previously reviewed.

## Scope and totals

- 12 uploaded archives reanalysed
- 10 LHA redistributions verified against canonical bytes
- 2 new GitHub source snapshots
- 8 canonical archives newly promoted to archive manifests
- canonical inventory: **38 archives / 1371 entries**

## Principal conclusions

### AmiExpress host source

`AmiExpress-master.zip` is complete host implementation source, mostly Amiga E. It materially strengthens understanding of session, node, command, transfer and service behavior. Host internals are not automatically treated as public AEDoor contract semantics.

### AmiX practical door source

`AmiXDoors-master.zip` is a behavior corpus of real doors and related network services. It demonstrates modern AmiExpress door use, BBSLink integration, global walls and last-caller services. Web backend C# code is classified separately from Amiga door-side code.

### MDoors volumes 1–5

The complete five-volume collection is now represented by archive manifests. The corpus is excellent evidence for ecosystem breadth, packaging and deployment practice, but compiled doors and user documentation are weaker semantic evidence than headers or source.

### Numeric command isolation

M5.2 preserves the boundary between MAXs, AEDoor, DayDream and other numeric command spaces. Matching integers are not evidence of equivalent meaning.

### Redistributions

DoorStatus, MDoors 3–5, UCDoor, RunRaw, MCE source and C Door Example were fully re-read despite byte identity. Duplicate uploads improve reproducibility but do not count as independent primary sources.

## Evidence products

- `catalog/evidence/m52-comprehensive-amiexpress-reanalysis.json`
- new archive manifests for AmiExpress, AmiXDoors, DoorStatus and MDoors 1–5
- source-corpus provenance records for AmiExpress and AmiXDoors
