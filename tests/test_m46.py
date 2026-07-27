import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "ods-tools" / "src"))

from ods_tools.profiles import build_conformance_report, load_profiles


class M46Tests(unittest.TestCase):
    def test_profiles_are_ordered_and_cumulative(self):
        profiles = load_profiles(ROOT)["profiles"]
        self.assertEqual([item["id"] for item in profiles], ["minimal", "interactive", "complete"])
        self.assertEqual([item["level"] for item in profiles], [1, 2, 3])
        previous = set()
        for profile in profiles:
            current = set(profile["required_operations"])
            self.assertTrue(previous.issubset(current))
            previous = current

    def test_profile_operations_are_canonical(self):
        canonical = {
            item["id"]
            for item in json.loads((ROOT / "catalog/operations/core.json").read_text())["operations"]
        }
        for profile in load_profiles(ROOT)["profiles"]:
            self.assertTrue(set(profile["required_operations"]).issubset(canonical))

    def test_committed_report_is_current(self):
        stored = json.loads((ROOT / "catalog/knowledge/conformance-report.json").read_text())
        self.assertEqual(stored, build_conformance_report(ROOT))

    def test_current_adapters_are_complete(self):
        report = build_conformance_report(ROOT)
        self.assertGreaterEqual(len(report["adapters"]), 2)
        for adapter in report["adapters"]:
            self.assertEqual(adapter["highest_profile"], "complete")
            self.assertFalse(adapter["unknown_operations"])

    def test_cli_evaluates_adapter(self):
        result = subprocess.run(
            [sys.executable, "-m", "ods_tools", "profiles", "daydream"],
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "tools/ods-tools/src")},
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("highest profile = complete", result.stdout)
        self.assertIn("interactive", result.stdout)


if __name__ == "__main__":
    unittest.main()
