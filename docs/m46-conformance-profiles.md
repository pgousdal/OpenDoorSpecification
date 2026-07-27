# M4.6 — Conformance profiles

ODS conformance profiles provide stable, cumulative capability targets for adapter implementations. They describe adapter behavior, not the historical completeness of an API family.

## Profiles

### Minimal

The minimal profile is suitable for lifecycle-safe, output-oriented doors. It requires terminal output, connection-state reporting, normal exit, and disconnect termination.

### Interactive

The interactive profile extends minimal with key input and basic caller context. It is the baseline for ordinary interactive doors.

### Complete

The complete profile requires every operation in the current ODS Core catalog, including operations whose stability is currently marked optional.

Profiles are cumulative: every operation required by a lower level must remain required by all higher levels.

## Source of truth

`catalog/profiles/conformance.json` is the maintained profile definition. `catalog/knowledge/conformance-report.json` is generated from the profile definition and adapter manifests and must not be edited manually.

## CLI

```sh
ods profiles
ods profiles minimal
ods profiles daydream
ods profiles --json
ods profiles --write catalog/knowledge/conformance-report.json
```

`ods validate --strict` rejects unknown profile operations, non-cumulative profiles, invalid adapter operations, and a stale generated conformance report.

## Relationship to M6.3

M6.3 treats these profiles as the existing cumulative required-operation
baseline. The [M6.3 architecture](m63-compatibility-profile-architecture.md)
adds language-neutral concepts for optional and outside-profile operations,
evidence expectations, adapter behavior, and implementation capability
declarations. PR1 does not change this artifact or its CLI behavior.
