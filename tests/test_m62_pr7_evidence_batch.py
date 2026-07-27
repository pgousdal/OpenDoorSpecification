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
from ods_tools.crosswalk_evidence import validate_crosswalk_evidence
from ods_tools.crosswalk_work_queue import build_crosswalk_work_queue


BATCH = {
    ("door-io", "lifecycle.disconnect"): "verified",
    ("door-io", "lifecycle.exit"): "partial",
}
PR6_BASELINE = {
    "coverage": {
        "total": 90,
        "reviewed": 54,
        "verified": 42,
        "partial": 12,
        "unassessed": 36,
    },
    "queue": {"total": 36, "high": 29, "medium": 5, "low": 2},
}


def load_generator(name: str):
    path = ROOT / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


GENERATORS = {
    "crosswalk": load_generator("generate_crosswalk"),
    "coverage": load_generator("generate_crosswalk_coverage"),
    "queue": load_generator("generate_crosswalk_work_queue"),
}


class M62PR7EvidenceBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.crosswalk = load_crosswalk(ROOT)
        cls.coverage = build_crosswalk_coverage(ROOT)
        cls.queue = build_crosswalk_work_queue(ROOT)

    def cell(self, host: str, operation: str) -> dict:
        return next(
            row
            for row in self.crosswalk["hosts"][host]["operations"]
            if row["operation"] == operation
        )

    def test_manifest_cells_have_complete_validated_provenance(self) -> None:
        self.assertEqual(validate_crosswalk_evidence(ROOT), 56)
        for (host, operation), status in BATCH.items():
            with self.subTest(host=host, operation=operation):
                cell = self.cell(host, operation)
                self.assertEqual(cell["id"], f"{host}:{operation}")
                self.assertEqual(cell["status"], status)
                self.assertEqual(cell["semantic_review"], "reviewed")
                self.assertTrue(cell["symbols"])
                self.assertTrue(cell["evidence"])
                self.assertTrue(cell["rationale"])
                if status == "partial":
                    self.assertTrue(cell["limitations"])

    def test_evidence_resolves_to_cataloged_door_io_archive(self) -> None:
        manifest = json.loads(
            (ROOT / "catalog" / "archives" / "door_io12.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            manifest["source_sha256"],
            "a5e639b6e785d158c4c318aac087e7e47b4b4553a7609c364f5044e57a41a7a1",
        )
        paths = {entry["path"] for entry in manifest["entries"]}
        for host, operation in BATCH:
            for evidence in self.cell(host, operation)["evidence"]:
                with self.subTest(operation=operation, evidence=evidence):
                    self.assertEqual(evidence["archive"], "door_io12.lha")
                    self.assertIn(evidence["path"], paths)
                    self.assertTrue(evidence["symbol"])

    def test_batch_is_removed_from_queue_and_other_gaps_remain(self) -> None:
        queued = {item["id"] for item in self.queue["items"]}
        for host, operation in BATCH:
            self.assertNotIn(f"{host}:{operation}", queued)
        self.assertIn("door-io:session.identity", queued)
        self.assertIn("door-io:session.time_left", queued)
        self.assertIn("door-io:status.set", queued)
        self.assertIn("door-io:bbs.command", queued)

    def test_coverage_and_queue_match_the_declared_pr6_delta(self) -> None:
        summary = self.coverage["summary"]
        self.assertEqual(summary["total"], PR6_BASELINE["coverage"]["total"])
        self.assertEqual(summary["reviewed"], 56)
        self.assertEqual(summary["verified"], 43)
        self.assertEqual(summary["partial"], 13)
        self.assertEqual(summary["unassessed"], 34)
        self.assertEqual(summary["reviewed"], summary["verified"] + summary["partial"])
        self.assertEqual(
            self.queue["summary"],
            {"total": 34, "high": 27, "medium": 5, "low": 2},
        )

    def test_no_unrelated_reviewed_mapping_changed(self) -> None:
        earlier_batches = {
            ("abbs", "lifecycle.disconnect"),
            ("ambos", "terminal.read_key"),
            ("ambos", "terminal.read_line"),
            ("daydream", "lifecycle.exit"),
            ("ucdoor", "terminal.write"),
            ("ucdoor", "terminal.read_line"),
            ("ucdoor", "session.time_left"),
            ("ucdoor", "lifecycle.disconnect"),
            ("aedoor", "terminal.write"),
            ("aedoor", "terminal.read_key"),
            ("aedoor", "terminal.read_line"),
            ("aedoor", "session.identity"),
            ("aedoor", "session.time_left"),
            ("aedoor", "bbs.command"),
            ("aedoor", "lifecycle.exit"),
            ("aedoor", "lifecycle.disconnect"),
            ("fame", "terminal.write"),
            ("fame", "terminal.read_key"),
            ("fame", "terminal.read_line"),
            ("fame", "session.identity"),
            ("fame", "session.time_left"),
            ("fame", "bbs.command"),
            ("fame", "lifecycle.exit"),
            ("fame", "lifecycle.disconnect"),
            ("ucdoor", "terminal.read_key"),
            ("ucdoor", "session.identity"),
            ("ucdoor", "bbs.command"),
            ("ucdoor", "lifecycle.exit"),
        }
        m61_reviewed = set()
        for path in (ROOT / "catalog" / "mappings").glob("*.json"):
            record = json.loads(path.read_text(encoding="utf-8"))
            m61_reviewed.update(
                (record["api"], mapping["operation"])
                for mapping in record["mappings"]
            )
        current_reviewed = {
            (host, row["operation"])
            for host, record in self.crosswalk["hosts"].items()
            for row in record["operations"]
            if row["status"] in {"verified", "partial"}
        }
        self.assertEqual(current_reviewed, m61_reviewed | earlier_batches | set(BATCH))

    def test_all_generation_is_byte_identical_and_committed(self) -> None:
        with (
            tempfile.TemporaryDirectory() as first_dir,
            tempfile.TemporaryDirectory() as second_dir,
        ):
            first = Path(first_dir)
            second = Path(second_dir)
            for root in (first, second):
                self.assertEqual(
                    GENERATORS["crosswalk"].generate(
                        ROOT / "catalog" / "census", root
                    ),
                    0,
                )
                self.assertEqual(
                    GENERATORS["coverage"].generate(ROOT, root / "coverage.json"),
                    0,
                )
                self.assertEqual(
                    GENERATORS["queue"].generate(ROOT, root / "work-queue.json"),
                    0,
                )
            for path in sorted(first.glob("*.json")):
                self.assertEqual(path.read_bytes(), (second / path.name).read_bytes())
                self.assertEqual(
                    path.read_bytes(),
                    (ROOT / "catalog" / "crosswalk" / path.name).read_bytes(),
                )

    def test_strict_validation_accepts_the_batch(self) -> None:
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
