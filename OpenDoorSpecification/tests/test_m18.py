import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class M18Tests(unittest.TestCase):
    def test_core_operations_are_unique(self):
        data = json.loads((ROOT / "catalog/operations/core.json").read_text())
        ids = [item["id"] for item in data["operations"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("lifecycle.disconnect", ids)

    def test_mappings_reference_known_operations(self):
        known = {item["id"] for item in json.loads((ROOT / "catalog/operations/core.json").read_text())["operations"]}
        for path in (ROOT / "catalog/mappings").glob("*.json"):
            data = json.loads(path.read_text())
            for mapping in data["mappings"]:
                self.assertIn(mapping["operation"], known)
                self.assertTrue(mapping["symbols"])

    def test_required_core_is_stable(self):
        data = json.loads((ROOT / "catalog/operations/core.json").read_text())
        core = {item["id"] for item in data["operations"] if item["stability"] == "core"}
        self.assertEqual(core, {"terminal.write", "terminal.read_key", "session.identity", "session.node", "session.connection_state", "lifecycle.exit", "lifecycle.disconnect"})

if __name__ == "__main__":
    unittest.main()
