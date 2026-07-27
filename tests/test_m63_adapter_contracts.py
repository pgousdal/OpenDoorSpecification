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

from ods_tools.adapter_contracts import (
    OUTCOMES,
    load_adapter_contracts,
    select_adapter_contract,
    validate_adapter_contract_document,
)


class M63AdapterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = load_adapter_contracts(ROOT)
        cls.canonical = json.loads(
            (ROOT / "catalog" / "operations" / "core.json").read_text(
                encoding="utf-8"
            )
        )

    def test_one_contract_exists_for_every_canonical_operation(self) -> None:
        canonical_ids = [item["id"] for item in self.canonical["operations"]]
        contracts = self.document["contracts"]
        self.assertTrue(all("operation" in item for item in contracts))
        self.assertTrue(all("operation_id" not in item for item in contracts))
        self.assertEqual([item["operation"] for item in contracts], canonical_ids)
        self.assertEqual(len(contracts), len(set(item["operation"] for item in contracts)))
        self.assertEqual(validate_adapter_contract_document(ROOT), len(canonical_ids))

    def test_closed_outcome_vocabulary(self) -> None:
        self.assertEqual(
            [item["id"] for item in self.document["outcome_vocabulary"]],
            list(OUTCOMES),
        )
        for contract in self.document["contracts"]:
            self.assertTrue(set(contract["outcomes"]).issubset(set(OUTCOMES)))
            self.assertEqual(
                len(contract["outcomes"]), len(set(contract["outcomes"]))
            )

    def test_contract_inputs_and_outputs_match_canonical_operations(self) -> None:
        for operation, contract in zip(
            self.canonical["operations"], self.document["contracts"]
        ):
            self.assertEqual(contract["operation"], operation["id"])
            self.assertEqual(
                [item["name"] for item in contract["inputs"]],
                operation["inputs"],
            )
            self.assertEqual(contract["output"]["result"], operation["result"])
            self.assertTrue(contract["normative_behavior"])
            self.assertTrue(contract["implementation_obligations"])
            self.assertEqual(
                set(contract["lifecycle"]),
                {
                    "normal_completion",
                    "disconnect",
                    "carrier_loss",
                    "implementation_shutdown",
                },
            )

    def test_duplicate_contract_and_invalid_outcome_are_rejected(self) -> None:
        duplicate = copy.deepcopy(self.document)
        duplicate["contracts"].insert(1, copy.deepcopy(duplicate["contracts"][0]))
        with self.assertRaisesRegex(ValueError, "exactly 11 contracts"):
            validate_adapter_contract_document(ROOT, duplicate)

        invalid = copy.deepcopy(self.document)
        invalid["contracts"][0]["outcomes"].append("timeout")
        with self.assertRaisesRegex(ValueError, "duplicate outcome|invalid outcome"):
            validate_adapter_contract_document(ROOT, invalid)

    def test_unknown_operation_and_invalid_fields_are_rejected(self) -> None:
        unknown = copy.deepcopy(self.document)
        unknown["contracts"][0]["operation"] = "terminal.unknown"
        with self.assertRaisesRegex(ValueError, "canonical operation ordering"):
            validate_adapter_contract_document(ROOT, unknown)

        extra = copy.deepcopy(self.document)
        extra["contracts"][0]["implementation_language"] = "python"
        with self.assertRaisesRegex(ValueError, "unknown contract fields"):
            validate_adapter_contract_document(ROOT, extra)

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
        listed = self.run_cli("contracts", "list")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn("adapter contracts:", listed.stdout)
        self.assertIn("terminal.write", listed.stdout)
        self.assertIn("lifecycle.disconnect", listed.stdout)

        shown = self.run_cli("contracts", "show", "terminal.write", "--json")
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(
            json.loads(shown.stdout),
            select_adapter_contract(ROOT, "terminal.write"),
        )

        validated = self.run_cli("contracts", "validate", "--json")
        self.assertEqual(validated.returncode, 0, validated.stderr)
        self.assertEqual(
            json.loads(validated.stdout),
            {"valid": True, "contract_count": 11},
        )

    def test_validation_summary_distinguishes_operation_concepts(self) -> None:
        validated = self.run_cli("validate")
        self.assertEqual(validated.returncode, 0, validated.stderr)
        self.assertIn("crosswalk operations", validated.stdout)
        self.assertIn("canonical operations", validated.stdout)
        self.assertIn("adapter contracts", validated.stdout)

    def test_catalog_order_and_json_are_deterministic(self) -> None:
        path = ROOT / "catalog" / "contracts" / "adapter-contracts.json"
        first = path.read_bytes()
        self.assertEqual(first, path.read_bytes())
        self.assertEqual(
            [item["operation"] for item in self.document["contracts"]],
            [item["id"] for item in self.canonical["operations"]],
        )

    def test_lifecycle_contracts_distinguish_terminal_events(self) -> None:
        exit_contract = select_adapter_contract(ROOT, "lifecycle.exit")
        disconnect_contract = select_adapter_contract(ROOT, "lifecycle.disconnect")
        self.assertIn("normal completion", exit_contract["lifecycle"]["normal_completion"])
        self.assertIn("not normal completion", disconnect_contract["lifecycle"]["normal_completion"])
        self.assertIn("Carrier loss", disconnect_contract["lifecycle"]["carrier_loss"])
        self.assertIn("Implementation shutdown", disconnect_contract["lifecycle"]["implementation_shutdown"])


if __name__ == "__main__":
    unittest.main()
