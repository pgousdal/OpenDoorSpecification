from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"
sys.path.insert(0, str(TOOLS_SRC))

from ods_tools.crosswalk import load_crosswalk
from ods_tools.crosswalk_coverage import build_crosswalk_coverage
from ods_tools.crosswalk_work_queue import build_crosswalk_work_queue


BATCH = {
    ("abbs", "lifecycle.disconnect"): "partial",
    ("ambos", "terminal.read_key"): "partial",
    ("ambos", "terminal.read_line"): "partial",
    ("daydream", "lifecycle.exit"): "verified",
    ("ucdoor", "terminal.write"): "verified",
    ("ucdoor", "terminal.read_line"): "partial",
    ("ucdoor", "session.time_left"): "partial",
    ("ucdoor", "lifecycle.disconnect"): "verified",
}
BASELINE = {
    "coverage": {
        "total": 90,
        "reviewed": 26,
        "verified": 20,
        "partial": 6,
        "unassessed": 64,
    },
    "queue": {"total": 64, "high": 52, "medium": 6, "low": 6},
}

GENERATOR_PATH = ROOT / "tools" / "generate_crosswalk.py"
spec = importlib.util.spec_from_file_location("generate_crosswalk", GENERATOR_PATH)
generator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(generator)


class M62EvidenceBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.crosswalk = load_crosswalk(ROOT)
        cls.coverage = build_crosswalk_coverage(ROOT)
        cls.queue = build_crosswalk_work_queue(ROOT)

    def test_batch_cells_have_reviewed_status_and_concrete_evidence(self) -> None:
        for (host_id, operation_id), status in BATCH.items():
            cell = next(
                row
                for row in self.crosswalk["hosts"][host_id]["operations"]
                if row["operation"] == operation_id
            )
            self.assertEqual(cell["status"], status)
            self.assertEqual(cell["semantic_review"], "reviewed")
            self.assertTrue(cell["symbols"])
            self.assertTrue(cell["evidence"])
            self.assertTrue(cell["rationale"])
            self.assertIn("limitations", cell)

    def test_evidence_references_resolve_to_cataloged_archive_entries(self) -> None:
        manifests = {}
        for path in (ROOT / "catalog" / "archives").glob("*.json"):
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifests[manifest["source_filename"]] = {
                entry["path"] for entry in manifest["entries"]
            }
        for host_id, operation_id in BATCH:
            cell = next(
                row
                for row in self.crosswalk["hosts"][host_id]["operations"]
                if row["operation"] == operation_id
            )
            for source in cell["evidence"]:
                self.assertIn(source["archive"], manifests)
                self.assertIn(
                    source["path"],
                    manifests[source["archive"]],
                    f"{host_id}:{operation_id}",
                )

    def test_batch_is_absent_from_regenerated_work_queue(self) -> None:
        queued = {item["id"] for item in self.queue["items"]}
        for host_id, operation_id in BATCH:
            self.assertNotIn(f"{host_id}:{operation_id}", queued)

    def test_coverage_and_queue_change_consistently_from_pr1_baseline(self) -> None:
        summary = self.coverage["summary"]
        self.assertEqual(summary["total"], BASELINE["coverage"]["total"])
        self.assertGreaterEqual(
            summary["reviewed"],
            BASELINE["coverage"]["reviewed"] + len(BATCH),
        )
        self.assertLessEqual(
            summary["unassessed"],
            BASELINE["coverage"]["unassessed"] - len(BATCH),
        )
        self.assertEqual(summary["reviewed"], summary["verified"] + summary["partial"])
        self.assertLessEqual(
            self.queue["summary"]["total"],
            BASELINE["queue"]["total"] - len(BATCH),
        )

    def test_no_unrelated_reviewed_mapping_changed(self) -> None:
        baseline_reviewed = set()
        for path in (ROOT / "catalog" / "mappings").glob("*.json"):
            record = json.loads(path.read_text(encoding="utf-8"))
            baseline_reviewed.update(
                (record["api"], mapping["operation"])
                for mapping in record["mappings"]
            )
        current_reviewed = {
            (host_id, row["operation"])
            for host_id, host in self.crosswalk["hosts"].items()
            for row in host["operations"]
            if row["status"] != "unassessed"
        }
        self.assertTrue((baseline_reviewed | set(BATCH)) <= current_reviewed)

    def test_all_cells_use_documented_statuses_and_dimensions_are_stable(self) -> None:
        operation_count = len(self.crosswalk["operations"]["operations"])
        self.assertEqual(
            self.coverage["summary"]["total"],
            len(self.crosswalk["hosts"]) * operation_count,
        )
        for host in self.crosswalk["hosts"].values():
            self.assertEqual(len(host["operations"]), operation_count)
            self.assertTrue(
                all(
                    row["status"] in {"verified", "partial", "unassessed"}
                    for row in host["operations"]
                )
            )

    def test_crosswalk_generation_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            self.assertEqual(
                generator.generate(ROOT / "catalog" / "census", first),
                0,
            )
            self.assertEqual(
                generator.generate(ROOT / "catalog" / "census", second),
                0,
            )
            for path in sorted(first.glob("*.json")):
                self.assertEqual(path.read_bytes(), (second / path.name).read_bytes())
                self.assertEqual(
                    path.read_bytes(),
                    (ROOT / "catalog" / "crosswalk" / path.name).read_bytes(),
                )

    def test_strict_validation_accepts_regenerated_artifacts(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(TOOLS_SRC)
        result = subprocess.run(
            [sys.executable, "-m", "ods_tools", "validate", "--strict"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
