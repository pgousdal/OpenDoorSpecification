# M4.9 Executable Conformance Suite

M4.9 turns the declarative conformance profiles into executable checks. The
suite invokes every ODS Core operation against each portable reference adapter
and verifies return values, terminal output, status changes, and lifecycle
exceptions.

## Commands

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools conformance
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools conformance daydream
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools conformance host-simulator --profile interactive
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools conformance --json
```

The committed report is generated with:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools conformance \
  --write catalog/knowledge/executable-conformance-report.json
```

## Scope

The executable harness currently covers the portable Python host simulator and
the portable DayDream backend model. Native Amiga execution remains a separate
platform test; the existing native DayDream C tests continue to validate that
binding.

The case definitions in `catalog/conformance/cases.json` are normative test
inputs for this suite. Generated reports must not be edited by hand.
