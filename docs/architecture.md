# Architecture

ODS has four layers:

1. **Normative specification** in `spec/`.
2. **Historical catalog** in `catalog/`.
3. **Schemas and validation** in `schemas/`.
4. **Research tooling** in `tools/ods-tools/`.

Historical symbols are preserved separately from normalized ODS capabilities. An adapter may map several historical functions to one ODS capability or expose an extension where no portable equivalent exists.
