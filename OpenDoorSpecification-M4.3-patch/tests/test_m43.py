from __future__ import annotations

import json
import unittest
from pathlib import Path

from ods_tools.coverage import build_coverage

ROOT = Path(__file__).resolve().parents[1]


class ProvenanceCoverageTests(unittest.TestCase):
    def test_report_matches_canonical_generation(self):
        stored = json.loads(
            (ROOT / "catalog" / "knowledge" / "provenance-coverage.json").read_text(encoding="utf-8")
        )
        self.assertEqual(stored, build_coverage(ROOT))

    def test_every_verified_mapping_has_provenance(self):
        report = build_coverage(ROOT)
        self.assertEqual(report["summary"]["verified_without_provenance"], 0)

    def test_report_exposes_uncovered_non_verified_mappings(self):
        report = build_coverage(ROOT)
        uncovered = [row for row in report["mappings"] if not row["covered"]]
        self.assertTrue(uncovered)
        self.assertTrue(all(row["mapping_status"] != "verified" for row in uncovered))

    def test_coverage_uses_machine_readable_evidence_classes(self):
        report = build_coverage(ROOT)
        allowed = {"documented", "observed", "inferred", "unknown"}
        for row in report["mappings"]:
            self.assertTrue(set(row["evidence_statuses"]).issubset(allowed))


if __name__ == "__main__":
    unittest.main()
