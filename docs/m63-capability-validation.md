# M6.3 PR5 — Capability and Profile Validation

M6.3 PR5 adds deterministic validation between Capability Declarations and the
existing Compatibility Profile and Adapter Contract catalogs. A declaration may
claim a profile; validation verifies the claim.

No new schemas, catalogs, generators, or crosswalk changes were introduced.

## Validation philosophy

A Capability Declaration describes what an implementation claims. Validation
does not run the implementation or execute conformance tests. It checks that
the claims are internally consistent and refer to existing canonical models.

Validation answers:

- Does every claimed Compatiblity Profile exist?
- Does the implementation declare every operation the profile requires?
- Is every required operation marked `supported` (not `partial`)?
- Does every declared operation have a canonical Adapter Contract?

Validation does not execute code, establish runtime correctness, or replace
conformance testing.

## Profile satisfaction

An implementation satisfies a claimed profile when:

1. the profile exists in the Compatibility Profile catalog;
2. every operation in the profile's `required_operations` list appears in the
   implementation's `capabilities` array;
3. each required operation is declared with status `supported`.

A required operation declared as `partial` does NOT satisfy the profile.
Partial support is reported separately so an implementation can document its
limitations while still making the limitation visible.

## Partial support

A `partial` status means the implementation provides the operation with
documented limitations. For a profile's required operations, partial support
is insufficient to claim the profile. The validation reports both:

- **missing required operations**: operations the profile requires but the
  declaration omits or marks `unsupported`;
- **partial required operations**: operations the profile requires but the
  declaration marks as `partial`.

This distinction lets profile consumers decide whether a known partial
operation is acceptable for their use case.

## Failure reporting

Validation output separates profile-level and contract-level issues.

Text output example:

```
host-simulator
  minimal: satisfies

daydream
  interactive: does not satisfy
    partial:
      session.node
```

JSON output includes structured results per implementation:

```json
{
  "declaration_count": 2,
  "all_satisfied": false,
  "results": [
    {
      "implementation_id": "host-simulator",
      "profiles": {
        "minimal": {
          "exists": true,
          "satisfied": true,
          "missing_required": [],
          "partial_required": []
        }
      },
      "contracts": {
        "all_have_contracts": true,
        "operations_without_contract": [],
        "unknown_canonical_operations": []
      }
    }
  ]
}
```

## Relationship to future conformance testing

Validation checks static claims against the canonical model. Conformance
testing (M4.9 executable conformance suite) runs an implementation against
test cases and observes runtime outcomes. The two are complementary:

- validation ensures the declaration is well-formed and refers to real models;
- conformance testing verifies the implementation actually behaves as declared.

A declaration that passes validation may still fail conformance tests.
A declaration that fails validation cannot be meaningfully tested because
its references are undefined.

## CLI

Installed and repository-local forms are equivalent:

```bash
ods capabilities validate
ods capabilities validate --json
ods capabilities show host-simulator
```

`ods capabilities validate` runs structural validation (field presence,
operation references) and then cross-model validation (profile satisfaction,
contract references).

`ods capabilities show <id>` includes a validation summary after the
declaration details.

## Validation rules implemented

1. **Profile existence**: every profile ID in `supported_profiles` must exist
   in the Compatibility Profile catalog.
2. **Required operations present**: every required operation of a claimed
   profile must appear in the declaration's `capabilities` array.
3. **Required operations supported**: every required operation must be
   declared with status `supported`. `partial` does not satisfy.
4. **Operation contracts**: every declared operation must have a corresponding
   entry in the Adapter Contract catalog.
5. **Canonical operation references**: every declared operation must be in
   the canonical operation catalog (`catalog/operations/core.json`).
6. **Deterministic ordering**: results are sorted by implementation ID;
   profiles within results are sorted by profile ID.
