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

from ods_tools.compatibility_profiles import (
    load_compatibility_profiles,
    select_compatibility_profile,
    validate_compatibility_profile_document,
)


class M63CompatibilityProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = load_compatibility_profiles(ROOT)

    def test_catalog_contains_only_the_existing_m46_profiles(self) -> None:
        self.assertEqual(
            [profile["id"] for profile in self.document["profiles"]],
            ["minimal", "interactive", "complete"],
        )
        self.assertEqual(validate_compatibility_profile_document(ROOT), 3)

    def test_profile_sets_are_exclusive_and_canonical(self) -> None:
        operation_ids = {
            operation["id"]
            for operation in json.loads(
                (ROOT / "catalog" / "operations" / "core.json").read_text(
                    encoding="utf-8"
                )
            )["operations"]
        }
        for profile in self.document["profiles"]:
            sets = [
                set(profile["required_operations"]),
                set(profile["optional_operations"]),
                set(profile["operations_outside_profile"]),
            ]
            self.assertTrue(sets[0])
            self.assertEqual(set().union(*sets), operation_ids)
            self.assertEqual(sum(map(len, sets)), len(set().union(*sets)))
            self.assertTrue(
                set(profile["required_operations"]).issubset(operation_ids)
            )

    def test_duplicate_profile_id_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.document)
        invalid["profiles"].append(copy.deepcopy(invalid["profiles"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate compatibility profile ID"):
            validate_compatibility_profile_document(ROOT, invalid)

    def test_duplicate_operation_and_overlap_are_rejected(self) -> None:
        duplicate = copy.deepcopy(self.document)
        duplicate["profiles"][0]["required_operations"].append(
            duplicate["profiles"][0]["required_operations"][0]
        )
        with self.assertRaisesRegex(ValueError, "duplicate operation"):
            validate_compatibility_profile_document(ROOT, duplicate)

        overlap = copy.deepcopy(self.document)
        overlap["profiles"][0]["optional_operations"] = [
            overlap["profiles"][0]["required_operations"][0]
        ]
        with self.assertRaisesRegex(ValueError, "appears in both"):
            validate_compatibility_profile_document(ROOT, overlap)

    def test_unknown_operation_and_empty_required_set_are_rejected(self) -> None:
        unknown = copy.deepcopy(self.document)
        unknown["profiles"][0]["optional_operations"] = ["session.unknown"]
        with self.assertRaisesRegex(ValueError, "unknown canonical operation"):
            validate_compatibility_profile_document(ROOT, unknown)

        empty = copy.deepcopy(self.document)
        empty["profiles"][0]["required_operations"] = []
        with self.assertRaisesRegex(ValueError, "required_operations cannot be empty"):
            validate_compatibility_profile_document(ROOT, empty)

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
        listed = self.run_cli("profiles", "list")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn("compatibility profiles:", listed.stdout)
        self.assertIn("minimal", listed.stdout)

        shown = self.run_cli("profiles", "show", "interactive", "--json")
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(json.loads(shown.stdout), select_compatibility_profile(ROOT, "interactive"))

        validated = self.run_cli("profiles", "validate", "--json")
        self.assertEqual(validated.returncode, 0, validated.stderr)
        self.assertEqual(
            json.loads(validated.stdout),
            {"valid": True, "profile_count": 3},
        )

    def test_catalog_is_deterministic_and_is_not_a_host_mapping(self) -> None:
        path = ROOT / "catalog" / "profiles" / "compatibility.json"
        first = path.read_bytes()
        second = json.dumps(
            json.loads(first), indent=2, ensure_ascii=False
        ).encode() + b"\n"
        self.assertEqual(first, second)
        for profile in self.document["profiles"]:
            self.assertNotIn("host", profile)
            self.assertNotIn("evidence", profile)
            self.assertNotIn("mappings", profile)


if __name__ == "__main__":
    unittest.main()
