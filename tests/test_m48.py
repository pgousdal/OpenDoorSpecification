import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class M48Tests(unittest.TestCase):
    def test_archive_totals(self):
        data = json.loads((ROOT / "catalog/archive-index.json").read_text())
        self.assertEqual((data["archive_count"], data["entry_count"]), (38, 1371))

    def test_new_manifests(self):
        expected = {
            "maxs-coders": ("MAXs_Coders.lha", 5),
            "maxs-guide": ("MAXsGUiDE.lha", 4),
            "maxshell-1.01": ("MAXShell101.lha", 15),
        }
        for stem, (archive, count) in expected.items():
            data = json.loads((ROOT / "catalog/archives" / f"{stem}.json").read_text())
            self.assertEqual(data["source_filename"], archive)
            self.assertEqual(data["entry_count"], count)

    def test_maxshell_primary_source(self):
        data = json.loads((ROOT / "catalog/evidence/m48-maxs-research.json").read_text())
        row = next(item for item in data["archives"] if item["archive"] == "MAXShell101.lha")
        self.assertEqual(row["evidence_status"], "observed")
        self.assertTrue(any("commands 1, 6, 8" in finding for finding in row["findings"]))

    def test_maxshell_joins_corpus(self):
        data = json.loads((ROOT / "catalog/evidence/historical-door-corpus.json").read_text())
        row = next(item for item in data["archives"] if item["archive"] == "MAXShell101.lha")
        self.assertEqual(row["kind"], "maxs-cli-door-source")
        self.assertEqual(row["evidence_status"], "observed")
        self.assertEqual(row["observed_calls"]["lifecycle.exit"], 1)

    def test_duplicate_distribution(self):
        data = json.loads((ROOT / "catalog/evidence/duplicate-archives.json").read_text())
        row = next(item for item in data["duplicates"] if item["uploaded"] == "MAXs_Coders (1).lha")
        self.assertEqual(row["canonical"], "MAXs_Coders.lha")
        self.assertEqual(row["status"], "byte-identical")

    def test_provenance_record(self):
        path = ROOT / "catalog/provenance/prov.paragon.maxshell-source.1.json"
        data = json.loads(path.read_text())
        self.assertEqual(data["status"], "observed")
        self.assertEqual({source["archive"] for source in data["sources"]}, {"MAXShell101.lha"})
