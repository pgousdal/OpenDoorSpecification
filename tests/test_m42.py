from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProvenancePopulationTests(unittest.TestCase):
    def records(self):
        return [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "catalog" / "provenance").glob("*.json"))
        ]

    def test_primary_source_records_are_populated(self):
        records = self.records()
        self.assertGreaterEqual(len(records), 16)
        self.assertEqual(len(records), len({record["id"] for record in records}))
        self.assertTrue(all(record["sources"] for record in records))

    def test_daydream_and_paragon_have_operation_provenance(self):
        records = self.records()
        pairs = {(record.get("api"), record.get("operation")) for record in records}
        self.assertIn(("daydream", "terminal.write"), pairs)
        self.assertIn(("daydream", "bbs.command"), pairs)
        self.assertIn(("paragon", "terminal.write"), pairs)
        self.assertIn(("paragon", "lifecycle.exit"), pairs)

    def test_records_use_real_archive_paths(self):
        manifests = {}
        for path in (ROOT / "catalog" / "archives").glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            manifests[data["source_filename"]] = {entry["path"] for entry in data["entries"]}
        for record in self.records():
            self.assertEqual(ROOT.joinpath("catalog", "provenance", record["id"] + ".json").name, record["id"] + ".json")
            for source in record["sources"]:
                self.assertIn(source["archive"], manifests)
                self.assertIn(source["path"], manifests[source["archive"]])

    def test_status_vocabulary_is_used(self):
        statuses = {record["status"] for record in self.records()}
        self.assertTrue(statuses.issubset({"documented", "observed", "inferred", "unknown"}))
        self.assertIn("documented", statuses)
        self.assertIn("observed", statuses)


if __name__ == "__main__":
    unittest.main()
