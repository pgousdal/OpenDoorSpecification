import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"
sys.path.insert(0, str(TOOLS_SRC))

from ods_tools.crosswalk_coverage import (
    build_crosswalk_coverage,
    format_crosswalk_coverage,
)


class M61CrosswalkCoverageTests(unittest.TestCase):
    def test_summary_totals(self):
        report = build_crosswalk_coverage(ROOT)
        summary = report["summary"]
        self.assertEqual(summary["total"], 90)
        self.assertEqual(summary["reviewed"], 56)
        self.assertEqual(summary["verified"] + summary["partial"], 56)
        self.assertEqual(summary["unassessed"], 34)

    def test_dimensions(self):
        report = build_crosswalk_coverage(ROOT)
        self.assertEqual(len(report["hosts"]), 10)
        self.assertEqual(len(report["operations"]), 9)
        self.assertTrue(all(x["summary"]["total"] == 9 for x in report["hosts"]))
        self.assertTrue(all(x["summary"]["total"] == 10 for x in report["operations"]))

    def test_semantics(self):
        report = build_crosswalk_coverage(ROOT)
        self.assertIn("does not mean unsupported", report["semantics"]["unassessed"])

    def test_gap_text(self):
        report = build_crosswalk_coverage(ROOT)
        rendered = format_crosswalk_coverage(report, gaps_only=True)
        self.assertIn("unassessed=", rendered)
        self.assertNotIn("unsupported", rendered)

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "ods_tools", *args],
            cwd=ROOT,
            env={"PYTHONPATH": str(TOOLS_SRC)},
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_coverage(self):
        result = self.run_cli("crosswalk", "--coverage")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("56/90", result.stdout)

    def test_cli_host_gaps(self):
        result = self.run_cli("crosswalk", "paragon", "--gaps")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("unassessed:", result.stdout)

    def test_generator_check(self):
        result = subprocess.run(
            [sys.executable, "tools/generate_crosswalk_coverage.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
