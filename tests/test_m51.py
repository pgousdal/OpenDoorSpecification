import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class M51Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(
            (ROOT / "catalog/evidence/m51-comprehensive-archive-reanalysis.json").read_text()
        )
        cls.rows = {row["archive"]: row for row in cls.data["archives"]}

    def test_all_twenty_uploads_reprocessed(self):
        self.assertEqual(self.data["archive_count"], 20)
        self.assertEqual(len(self.rows), 20)
        self.assertTrue(all(row["extracted"] > 0 for row in self.rows.values()))

    def test_all_are_byte_identical_redistributions(self):
        self.assertTrue(
            all(row["duplicate"]["byte_identical"] for row in self.rows.values())
        )
        duplicates = json.loads(
            (ROOT / "catalog/evidence/duplicate-archives.json").read_text()
        )["duplicates"]
        uploaded = {row["uploaded"] for row in duplicates}
        self.assertTrue(set(self.rows) <= uploaded)

    def test_maxs_source_corpus_is_present(self):
        aris = self.rows["ArisDoors4MAXs(1).lha"]
        self.assertEqual(aris["file_types"]["c"], 63)
        self.assertGreaterEqual(aris["entries"], 200)
        commands = {row["command"] for row in aris["observed_command_numbers"]}
        self.assertTrue({1, 6, 8, 13, 14, 20, 200, 201} <= commands)

    def test_minimal_c_example_commands(self):
        row = self.rows["CDoorExample(1).lha"]
        commands = {item["command"] for item in row["observed_command_numbers"]}
        self.assertTrue({1, 6, 8, 10, 14, 20, 200} <= commands)
        self.assertTrue(any(x["name"] == "DoorMsg" for x in row["top_structures"]))

    def test_amiga_e_maxs_wrappers(self):
        row = self.rows["max_e(1).lha"]
        symbols = {
            item["symbol"]
            for item in row["api_symbols"]["paragon_maxs"]
        }
        self.assertTrue({"mxPrint", "mxInput", "mxHotKey"} <= symbols)

    def test_fame_and_ambos_are_distinct_interfaces(self):
        fame = self.rows["fcomm130(1).lha"]
        ambos = self.rows["AmBoS_doc_dev(1).lha"]
        fame_symbols = {
            item["symbol"] for item in fame["api_symbols"]["fame"]
        }
        ambos_symbols = {
            item["symbol"] for item in ambos["api_symbols"]["ambos"]
        }
        self.assertIn("FAMEDoorMsg", fame_symbols)
        self.assertIn("BBSBase", ambos_symbols)
        self.assertEqual(ambos["file_types"]["fd"], 1)

    def test_canonical_totals_do_not_change(self):
        index = json.loads((ROOT / "catalog/archive-index.json").read_text())
        self.assertEqual((index["archive_count"], index["entry_count"]), (38, 1371))
