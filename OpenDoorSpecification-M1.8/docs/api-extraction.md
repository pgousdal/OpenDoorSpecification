# API extraction — M1.7

This milestone performs conservative symbol extraction from the uploaded historical SDKs. Generated records retain source archive, path and line where available. `verified-from-example` symbols are not treated as normative ABI declarations.

## Extracted symbols

- **abbs:** 16
- **aedoor:** 14
- **ambos:** 45
- **daydream:** 91
- **door-io:** 6
- **paragon:** 32

## Limitations

C prototypes, Amiga E modules and assembler includes vary considerably. M1.7 favors false negatives over invented signatures. Documentation prose still requires manual semantic review.
