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
    validate_all_capability_declarations,
    validate_capability_declaration,
    validate_capability_declaration_document,
    validate_contract_references,
    validate_profile_satisfaction,
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
        parsed = json.loads(shown.stdout)
        self.assertIn("declaration", parsed)
        self.assertIn("validation", parsed)
        self.assertEqual(
            parsed["declaration"],
            select_capability_declaration(ROOT, "host-simulator"),
        )

        validated = self.run_cli("capabilities", "validate", "--json")
        self.assertEqual(validated.returncode, 0, validated.stderr)
        parsed_v = json.loads(validated.stdout)
        self.assertIn("declaration_count", parsed_v)
        self.assertIn("results", parsed_v)
        self.assertEqual(parsed_v["declaration_count"], 2)

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


    def test_profile_satisfaction_host_simulator_satisfies_minimal(self) -> None:
        decl = self.declarations["host-simulator"]
        result = validate_capability_declaration(ROOT, decl)
        profiles = result["profiles"]
        self.assertIn("minimal", profiles)
        self.assertTrue(profiles["minimal"]["exists"])
        self.assertTrue(profiles["minimal"]["satisfied"])
        self.assertEqual(profiles["minimal"]["missing_required"], [])
        self.assertEqual(profiles["minimal"]["partial_required"], [])
        self.assertEqual(result["profile_count"]["satisfied"], 1)

    def test_profile_satisfaction_daydream_fails_interactive(self) -> None:
        decl = self.declarations["daydream"]
        result = validate_capability_declaration(ROOT, decl)
        profiles = result["profiles"]
        self.assertIn("interactive", profiles)
        self.assertTrue(profiles["interactive"]["exists"])
        self.assertFalse(profiles["interactive"]["satisfied"])
        self.assertNotIn("session.node", profiles["interactive"]["missing_required"])
        self.assertIn("session.node", profiles["interactive"]["partial_required"])

    def test_missing_required_operation_is_detected(self) -> None:
        decl = copy.deepcopy(self.declarations["host-simulator"])
        required = json.loads(
            (ROOT / "catalog" / "profiles" / "compatibility.json").read_text()
        )["profiles"][0]["required_operations"]
        decl["capabilities"] = [
            c for c in decl["capabilities"]
            if c["operation"] not in required
        ]
        result = validate_profile_satisfaction(ROOT, decl)
        min_profile = result.get("minimal", {})
        self.assertFalse(min_profile.get("satisfied", True))
        for op in required:
            self.assertIn(op, min_profile.get("missing_required", []))

    def test_partial_required_is_not_satisfied(self) -> None:
        decl = self.declarations["daydream"]
        interactive_profiles = json.loads(
            (ROOT / "catalog" / "profiles" / "compatibility.json").read_text()
        )["profiles"][1]
        required = interactive_profiles["required_operations"]
        result = validate_profile_satisfaction(ROOT, decl)
        for op in required:
            cap_status = next(
                (c["status"] for c in decl["capabilities"] if c["operation"] == op),
                None,
            )
            if cap_status == "partial":
                self.assertIn(
                    op,
                    result.get("interactive", {}).get("partial_required", []),
                )

    def test_unknown_profile_is_reported(self) -> None:
        decl = self.declarations["host-simulator"]
        decl["supported_profiles"] = ["nonexistent-profile"]
        result = validate_profile_satisfaction(ROOT, decl)
        self.assertIn("nonexistent-profile", result)
        self.assertFalse(result["nonexistent-profile"]["exists"])
        self.assertFalse(result["nonexistent-profile"]["satisfied"])

    def test_contract_references_all_operations_have_contracts(self) -> None:
        contracts = json.loads(
            (ROOT / "catalog" / "contracts" / "adapter-contracts.json").read_text()
        )
        for decl_id, data in self.declarations.items():
            result = validate_contract_references(ROOT, data, contracts)
            self.assertTrue(
                result["all_have_contracts"],
                f"{decl_id}: missing contracts for {result['operations_without_contract']}",
            )
            self.assertEqual(result["operations_without_contract"], [])
            self.assertEqual(result["unknown_canonical_operations"], [])

    def test_validate_json_output_includes_structured_results(self) -> None:
        result = self.run_cli("capabilities", "validate", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = json.loads(result.stdout)
        self.assertIn("results", parsed)
        for entry in parsed["results"]:
            self.assertIn("implementation_id", entry)
            self.assertIn("profiles", entry)
            self.assertIn("contracts", entry)

    def test_validate_text_output_includes_host_simulator(self) -> None:
        result = self.run_cli("capabilities", "validate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("host-simulator", result.stdout)
        self.assertIn("daydream", result.stdout)

    def test_validate_text_shows_satisfies_for_minimal(self) -> None:
        result = self.run_cli("capabilities", "validate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("minimal", result.stdout)
        self.assertIn("satisfies", result.stdout)

    def test_validation_is_deterministic(self) -> None:
        first = validate_all_capability_declarations(ROOT)
        second = validate_all_capability_declarations(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(
            [r["implementation_id"] for r in first["results"]],
            sorted(r["implementation_id"] for r in first["results"]),
        )

    def test_show_text_includes_validation(self) -> None:
        result = self.run_cli("capabilities", "show", "host-simulator")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("validation", result.stdout)
        self.assertIn("minimal", result.stdout)

    def test_validate_contract_references_detects_missing_contract(self) -> None:
        decl = self.declarations["host-simulator"]
        contracts = json.loads(
            (ROOT / "catalog" / "contracts" / "adapter-contracts.json").read_text()
        )
        contracts["contracts"] = [
            c for c in contracts["contracts"]
            if c["operation"] != "terminal.write"
        ]
        result = validate_contract_references(ROOT, decl, contracts)
        self.assertFalse(result["all_have_contracts"])
        self.assertIn("terminal.write", result["operations_without_contract"])


if __name__ == "__main__":
    unittest.main()
