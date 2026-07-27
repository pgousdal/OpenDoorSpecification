import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"
sys.path.insert(0, str(TOOLS_SRC))

from ods_tools.crosswalk import format_crosswalk, select_crosswalk, validate_crosswalk


class M61CrosswalkCliTests(unittest.TestCase):
    def test_crosswalk_validation(self):
        hosts, operations, mappings = validate_crosswalk(ROOT)
        index = json.loads((ROOT / "catalog/crosswalk/index.json").read_text(encoding="utf-8"))
        self.assertEqual((hosts, operations, mappings), (index["host_count"], index["operation_count"], index["mapped_cell_count"]))

    def test_host_lookup(self):
        record = select_crosswalk(ROOT, "paragon")
        self.assertEqual(record["host"]["id"], "paragon")
        rendered = format_crosswalk(record)
        self.assertIn("terminal.write", rendered)
        self.assertNotIn("unassessed", rendered)

    def test_operation_lookup(self):
        record = select_crosswalk(ROOT, "terminal.write")
        self.assertEqual(record["id"], "terminal.write")
        self.assertIn("paragon", record["hosts"])

    def test_explicit_lookup_prefixes(self):
        self.assertEqual(select_crosswalk(ROOT, "host:paragon")["host"]["id"], "paragon")
        self.assertEqual(select_crosswalk(ROOT, "operation:terminal.write")["id"], "terminal.write")

    def test_unknown_lookup(self):
        with self.assertRaises(KeyError):
            select_crosswalk(ROOT, "not-a-real-target")

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "ods_tools", *args], cwd=ROOT, env={"PYTHONPATH": str(TOOLS_SRC)}, text=True, capture_output=True, check=False)

    def test_cli_host_text(self):
        result = self.run_cli("crosswalk", "paragon")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MAXs/Paragon", result.stdout)
        self.assertIn("terminal.write", result.stdout)

    def test_cli_operation_json(self):
        result = self.run_cli("crosswalk", "terminal.write", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["id"], "terminal.write")

    def test_validate_reports_crosswalk(self):
        result = self.run_cli("validate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("crosswalk hosts", result.stdout)


if __name__ == "__main__":
    unittest.main()
