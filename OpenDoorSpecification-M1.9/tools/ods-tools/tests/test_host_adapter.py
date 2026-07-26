import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/ods-tools/src"))

from ods_tools.adapters.host import HostAdapter
from ods_tools.simulator import run_scenario


class HostSimulatorToolTests(unittest.TestCase):
    def test_json_style_scenario(self):
        result = run_scenario({
            "inputs": {"keys": ["Y"]},
            "actions": [
                {"operation": "terminal.read_key"},
                {"operation": "terminal.write", "arguments": {"data": "done"}},
            ],
        })
        self.assertEqual(result["output"], "done")
        self.assertEqual(result["transcript"][0]["result"], "Y")


if __name__ == "__main__":
    unittest.main()
