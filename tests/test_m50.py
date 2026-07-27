import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class M50Tests(unittest.TestCase):
    def test_archive_totals(self):
        data=json.loads((ROOT / "catalog/archive-index.json").read_text())
        self.assertEqual((data["archive_count"], data["entry_count"]), (30, 1150))

    def test_reanalysis_covers_every_upload(self):
        data=json.loads((ROOT / "catalog/evidence/m50-comprehensive-archive-reanalysis.json").read_text())
        self.assertEqual(data["archive_count"], 20)
        self.assertEqual(len(data["archives"]), 20)

    def test_duplicate_uploads_are_reprocessed(self):
        data=json.loads((ROOT / "catalog/evidence/m50-comprehensive-archive-reanalysis.json").read_text())
        duplicates=[row for row in data["archives"] if (row.get("duplicate") or {}).get("byte_identical")]
        self.assertEqual(len(duplicates), 19)
        self.assertTrue(all(row["entries"] > 0 for row in duplicates))

    def test_abbs_preservation_manifest(self):
        data=json.loads((ROOT / "catalog/archives/preservation-abbs20-master.json").read_text())
        self.assertEqual(data["source_filename"], "preservation-abbs20-master.zip")
        self.assertEqual(data["entry_count"], 246)
        self.assertEqual(sum(not row["path"].endswith("/") for row in data["entries"]), 238)

    def test_abbs_source_census(self):
        data=json.loads((ROOT / "catalog/evidence/m50-comprehensive-archive-reanalysis.json").read_text())
        row=next(row for row in data["archives"] if row["archive"] == "preservation-abbs20-master.zip")
        self.assertEqual(row["file_types"]["c"], 72)
        self.assertEqual(row["file_types"]["asm"], 51)

    def test_lh1_limit_is_explicit(self):
        data=json.loads((ROOT / "catalog/evidence/m50-comprehensive-archive-reanalysis.json").read_text())
        acp=next(row for row in data["archives"] if row["archive"] == "acp300(1).lzh")
        self.assertEqual(acp["extracted"], 0)
        self.assertEqual(acp["unextracted"], 34)
        self.assertIn("-lh1-", acp["methods"])

    def test_abbs_provenance(self):
        data=json.loads((ROOT / "catalog/provenance/prov.abbs.preservation-source.1.json").read_text())
        self.assertEqual(data["status"], "observed")
        self.assertEqual({s["archive"] for s in data["sources"]}, {"preservation-abbs20-master.zip"})
