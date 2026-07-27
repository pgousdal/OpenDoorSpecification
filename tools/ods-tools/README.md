# ods-tools

`ods-tools` is the unified Python 3.11+ CLI for ODS catalog research,
inspection, generation support, simulation, conformance, and repository
validation.

Install it from the repository:

```bash
python3 -m pip install -e tools/ods-tools
ods --help
```

Or run directly:

```bash
PYTHONPATH=tools/ods-tools/src python3 -m ods_tools --help
```

Common commands:

```bash
ods inventory archive.lha
ods list-archives
ods inspect terminal.write
ods compare abbs daydream
ods coverage
ods gaps
ods profiles
ods operations
ods conformance
ods simulate examples/host-simulator/hello.json --transcript
ods crosswalk --coverage
ods crosswalk --work-queue
ods crosswalk --triage
ods crosswalk --completion
ods crosswalk --backlog
ods validate
ods validate --strict
```

Use `ods <command> --help` for command-specific arguments. Crosswalk generation
is performed by the repository scripts in `tools/`; the CLI reads and validates
their committed artifacts.
