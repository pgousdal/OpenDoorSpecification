import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "ods-tools" / "src"))

from ods_tools.conformance import build_executable_conformance_report, load_cases


class M49Tests(unittest.TestCase):
    def test_suite_covers_every_core_operation_once(self):
        operations = [item["id"] for item in json.loads((ROOT / "catalog/operations/core.json").read_text())["operations"]]
        cases = load_cases(ROOT)["cases"]
        covered = [item["operation"] for item in cases]
        self.assertEqual(set(covered), set(operations))
        self.assertEqual(len(covered), len(set(covered)))

    def test_all_portable_adapters_pass_complete(self):
        report = build_executable_conformance_report(ROOT)
        self.assertEqual(report["case_count"], 11)
        self.assertEqual({item["id"] for item in report["adapters"]}, {"daydream", "host-simulator"})
        for adapter in report["adapters"]:
            self.assertEqual(adapter["highest_executed_profile"], "complete")
            self.assertEqual(adapter["passed_cases"], adapter["total_cases"])
            self.assertTrue(all(item["passed"] for item in adapter["cases"]))

    def test_committed_report_is_current(self):
        stored = json.loads((ROOT / "catalog/knowledge/executable-conformance-report.json").read_text())
        self.assertEqual(stored, build_executable_conformance_report(ROOT))

    def test_cli_reports_adapter_and_profile(self):
        result = subprocess.run(
            [sys.executable, "-m", "ods_tools", "conformance", "daydream", "--profile", "complete"],
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "tools/ods-tools/src")},
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("daydream: 11/11 cases", result.stdout)
        self.assertIn("complete", result.stdout)
        self.assertIn("PASS", result.stdout)

    def test_lifecycle_cases_validate_exception_payloads(self):
        report = build_executable_conformance_report(ROOT)
        for adapter in report["adapters"]:
            lifecycle = {item["operation"]: item for item in adapter["cases"] if item["operation"].startswith("lifecycle.")}
            self.assertTrue(lifecycle["lifecycle.exit"]["passed"])
            self.assertTrue(lifecycle["lifecycle.disconnect"]["passed"])


if __name__ == "__main__":
    unittest.main()
