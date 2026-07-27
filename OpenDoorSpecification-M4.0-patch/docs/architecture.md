# Architecture

The authoritative architecture and project boundaries are defined in the
repository-root [`ARCHITECTURE.md`](../ARCHITECTURE.md).

ODS has six logical layers:

1. normative specification in `spec/`;
2. historical catalog and evidence in `catalog/`;
3. schemas in `schemas/`;
4. research and validation tooling in `tools/ods-tools/`;
5. reference implementations in `reference/`, `native/`, and `examples/`;
6. repository and conformance checks in `tests/` and `scripts/`.

See [Project structure and migration target](project-structure.md) for the
incremental M4 migration plan.
