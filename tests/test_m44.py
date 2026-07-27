from __future__ import annotations

import json
import unittest
from pathlib import Path

from ods_tools.operations import build_operation_records

ROOT = Path(__file__).resolve().parents[1]


class CanonicalOperationRecordTests(unittest.TestCase):
    def test_every_operation_has_a_generated_record(self):
        generated = build_operation_records(ROOT)
        stored = ROOT / "catalog" / "knowledge" / "operations"
        for record in generated["operations"]:
            path = stored / (record["id"].replace(".", "-") + ".json")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), record)

    def test_index_preserves_canonical_operation_order(self):
        generated = build_operation_records(ROOT)
        index = json.loads((ROOT / "catalog" / "knowledge" / "operations" / "index.json").read_text(encoding="utf-8"))
        self.assertEqual([item["id"] for item in index["operations"]], [item["id"] for item in generated["operations"]])

    def test_historical_implementations_include_provenance_coverage(self):
        for record in build_operation_records(ROOT)["operations"]:
            for implementation in record["historical_implementations"]:
                self.assertIn("provenance_ids", implementation)
                self.assertIn("evidence_statuses", implementation)
                if implementation["status"] == "verified":
                    self.assertTrue(implementation["covered"])

    def test_adapter_status_is_complete_for_every_record(self):
        records = build_operation_records(ROOT)["operations"]
        adapter_sets = [{item["adapter"] for item in record["adapter_status"]} for record in records]
        self.assertTrue(adapter_sets)
        self.assertTrue(all(items == adapter_sets[0] for items in adapter_sets))


if __name__ == "__main__":
    unittest.main()
