from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"
sys.path.insert(0, str(TOOLS_SRC))

from ods_tools.adapter_contracts import OUTCOMES as CONTRACT_OUTCOMES
from ods_tools.capability_declarations import (
    CAPABILITY_STATUSES,
    load_capability_declarations,
    select_capability_declaration,
    validate_capability_declaration_document,
)


class M63CapabilityDeclarationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.declarations = load_capability_declarations(ROOT)
        cls.canonical = json.loads(
            (ROOT / "catalog" / "operations" / "core.json").read_text(
                encoding="utf-8"
            )
        )

    def test_catalog_exists_with_expected_declarations(self) -> None:
        self.assertIn("host-simulator", self.declarations)
        self.assertIn("daydream", self.declarations)
        self.assertEqual(
            validate_capability_declaration_document(ROOT),
            len(self.declarations),
        )

    def test_every_capability_uses_valid_status(self) -> None:
        for decl_id, data in self.declarations.items():
            for cap in data["capabilities"]:
                self.assertIn(
                    cap["status"],
                    CAPABILITY_STATUSES,
                    f"{decl_id}: invalid status {cap['status']} for {cap['operation']}",
                )

    def test_every_capability_references_canonical_operation(self) -> None:
        operation_ids = {
            op["id"] for op in self.canonical["operations"]
        }
        for decl_id, data in self.declarations.items():
            seen: set[str] = set()
            for cap in data["capabilities"]:
                self.assertIn(
                    cap["operation"],
                    operation_ids,
                    f"{decl_id}: unknown operation {cap['operation']}",
                )
                self.assertNotIn(
                    cap["operation"],
                    seen,
                    f"{decl_id}: duplicate operation {cap['operation']}",
                )
                seen.add(cap["operation"])

    def test_each_declaration_has_unique_implementation_id(self) -> None:
        ids = [d["implementation_id"] for d in self.declarations.values()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_duplicate_implementation_id_is_rejected(self) -> None:
        dup = copy.deepcopy(
            self.declarations[list(self.declarations.keys())[0]]
        )
        with self.assertRaisesRegex(ValueError, "duplicate implementation_id"):
            validate_capability_declaration_document(
                ROOT,
                declarations={
                    "dup-a": dup,
                    "dup-b": dup,
                },
            )

    def test_invalid_capability_status_is_rejected(self) -> None:
        invalid = copy.deepcopy(
            self.declarations[list(self.declarations.keys())[0]]
        )
        invalid["capabilities"][0]["status"] = "unknown-status"
        invalid["implementation_id"] = "test-impl"
        with self.assertRaisesRegex(ValueError, "invalid capability status"):
            validate_capability_declaration_document(
                ROOT, invalid
            )

    def test_unknown_operation_is_rejected(self) -> None:
        invalid = copy.deepcopy(
            self.declarations[list(self.declarations.keys())[0]]
        )
        invalid["capabilities"][0]["operation"] = "terminal.unknown"
        invalid["implementation_id"] = "test-impl"
        with self.assertRaisesRegex(ValueError, "unknown canonical operation"):
            validate_capability_declaration_document(
                ROOT, invalid
            )

    def test_duplicate_operation_within_one_declaration_is_rejected(self) -> None:
        invalid = copy.deepcopy(
            self.declarations[list(self.declarations.keys())[0]]
        )
        invalid["capabilities"].append(
            copy.deepcopy(invalid["capabilities"][0])
        )
        invalid["implementation_id"] = "test-impl"
        with self.assertRaisesRegex(ValueError, "duplicate operation declaration"):
            validate_capability_declaration_document(
                ROOT, invalid
            )

    def test_unknown_fields_are_rejected(self) -> None:
        invalid = copy.deepcopy(
            self.declarations[list(self.declarations.keys())[0]]
        )
        invalid["unknown_field"] = "value"
        invalid["implementation_id"] = "test-impl"
        with self.assertRaisesRegex(ValueError, "unknown declaration fields"):
            validate_capability_declaration_document(
                ROOT, invalid
            )

        unknown_cap = copy.deepcopy(
            self.declarations[list(self.declarations.keys())[0]]
        )
        unknown_cap["capabilities"][0]["unknown_cap_field"] = "value"
        unknown_cap["implementation_id"] = "test-impl"
        with self.assertRaisesRegex(ValueError, "unknown capability fields"):
            validate_capability_declaration_document(
                ROOT, unknown_cap
            )

    def test_invalid_implementation_id_is_rejected(self) -> None:
        invalid = copy.deepcopy(
            self.declarations[list(self.declarations.keys())[0]]
        )
        invalid["implementation_id"] = "Has Upper Case"
        with self.assertRaisesRegex(ValueError, "invalid implementation_id"):
            validate_capability_declaration_document(
                ROOT, invalid
            )

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(TOOLS_SRC)
        return subprocess.run(
            [sys.executable, "-m", "ods_tools", *args],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_list_show_and_validate(self) -> None:
        listed = self.run_cli("capabilities", "list")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn("capability declarations", listed.stdout)
        self.assertIn("host-simulator", listed.stdout)
        self.assertIn("daydream", listed.stdout)

        shown = self.run_cli("capabilities", "show", "host-simulator", "--json")
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(
            json.loads(shown.stdout),
            select_capability_declaration(ROOT, "host-simulator"),
        )

        validated = self.run_cli("capabilities", "validate", "--json")
        self.assertEqual(validated.returncode, 0, validated.stderr)
        self.assertEqual(
            json.loads(validated.stdout),
            {"valid": True, "declaration_count": 2},
        )

    def test_capability_statuses_are_separate_from_contract_outcomes(self) -> None:
        self.assertEqual(
            CAPABILITY_STATUSES,
            frozenset({"supported", "partial", "unsupported"}),
        )
        self.assertEqual(
            set(CONTRACT_OUTCOMES),
            {"success", "unsupported", "invalid-request", "host-failure", "disconnected"},
        )
        self.assertNotEqual(
            CAPABILITY_STATUSES,
            set(CONTRACT_OUTCOMES),
            "capability statuses must differ from contract outcome values",
        )

    def test_capability_declarations_do_not_contain_adapter_contract_fields(self) -> None:
        contract_fields = {
            "normative_behavior", "inputs", "output", "outcomes",
            "unsupported_behavior", "lifecycle",
            "implementation_obligations", "compatibility_notes",
            "outcome_vocabulary", "contracts",
        }
        profile_fields = {
            "maturity", "required_operations", "optional_operations",
            "operations_outside_profile", "compatibility_expectations",
            "conformance_evidence_expectations",
        }
        for data in self.declarations.values():
            for field in contract_fields | profile_fields:
                self.assertNotIn(field, data)
            for cap in data["capabilities"]:
                for field in contract_fields | profile_fields:
                    self.assertNotIn(field, cap)

    def test_cli_validate_shows_count_in_ods_validate(self) -> None:
        result = self.run_cli("validate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("capability declarations", result.stdout)

    def test_catalog_is_deterministic(self) -> None:
        for decl_id, data in self.declarations.items():
            path = ROOT / "catalog" / "capabilities" / f"{decl_id}.json"
            first = path.read_bytes()
            second = json.dumps(
                json.loads(first), indent=2, ensure_ascii=False
            ).encode() + b"\n"
            self.assertEqual(
                first, second,
                f"{decl_id}.json is not deterministically formatted",
            )

    def test_capabilities_are_in_consistent_order(self) -> None:
        canonical_ids = [op["id"] for op in self.canonical["operations"]]
        for decl_id, data in self.declarations.items():
            cap_ops = [cap["operation"] for cap in data["capabilities"]]
            self.assertEqual(
                cap_ops,
                sorted(cap_ops, key=lambda op: canonical_ids.index(op)),
                f"{decl_id}: capabilities not in canonical operation order",
            )


if __name__ == "__main__":
    unittest.main()
