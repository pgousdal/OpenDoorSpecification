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
    "terminal.write": "verified",
    "terminal.read_key": "verified",
    "terminal.read_line": "verified",
    "session.identity": "verified",
    "session.time_left": "verified",
    "bbs.command": "verified",
    "lifecycle.exit": "verified",
    "lifecycle.disconnect": "partial",
}
PR3_BASELINE = {
    "coverage": {
        "total": 90,
        "reviewed": 34,
        "verified": 23,
        "partial": 11,
        "unassessed": 56,
    },
    "queue": {"total": 56, "high": 46, "medium": 6, "low": 4},
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


class M62AEDoorEvidenceBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.crosswalk = load_crosswalk(ROOT)
        cls.coverage = build_crosswalk_coverage(ROOT)
        cls.queue = build_crosswalk_work_queue(ROOT)
        cls.aedoor = {
            row["operation"]: row
            for row in cls.crosswalk["hosts"]["aedoor"]["operations"]
        }

    def test_manifest_cells_have_complete_validated_provenance(self) -> None:
        self.assertEqual(validate_crosswalk_evidence(ROOT), 42)
        for operation, status in BATCH.items():
            with self.subTest(operation=operation):
                cell = self.aedoor[operation]
                self.assertEqual(cell["id"], f"aedoor:{operation}")
                self.assertEqual(cell["status"], status)
                self.assertEqual(cell["semantic_review"], "reviewed")
                self.assertTrue(cell["symbols"])
                self.assertTrue(cell["evidence"])
                self.assertTrue(cell["rationale"])
                if status == "partial":
                    self.assertTrue(cell["limitations"])

    def test_evidence_resolves_to_the_cataloged_aedoor_archive(self) -> None:
        manifest = json.loads(
            (ROOT / "catalog" / "archives" / "aedoor28.json").read_text(
                encoding="utf-8"
            )
        )
        paths = {entry["path"] for entry in manifest["entries"]}
        for operation in BATCH:
            for evidence in self.aedoor[operation]["evidence"]:
                with self.subTest(operation=operation, evidence=evidence):
                    self.assertEqual(evidence["archive"], "aedoor28.lha")
                    self.assertIn(evidence["path"], paths)
                    self.assertTrue(evidence["symbol"])

    def test_batch_is_removed_from_queue_and_uncertain_cell_remains(self) -> None:
        queued = {item["id"] for item in self.queue["items"]}
        self.assertTrue(
            all(f"aedoor:{operation}" not in queued for operation in BATCH)
        )
        self.assertIn("aedoor:status.set", queued)

    def test_coverage_and_queue_match_the_declared_pr3_delta(self) -> None:
        summary = self.coverage["summary"]
        self.assertEqual(summary["total"], PR3_BASELINE["coverage"]["total"])
        self.assertEqual(
            summary["reviewed"],
            PR3_BASELINE["coverage"]["reviewed"] + len(BATCH),
        )
        self.assertEqual(
            summary["verified"],
            PR3_BASELINE["coverage"]["verified"] + 7,
        )
        self.assertEqual(
            summary["partial"],
            PR3_BASELINE["coverage"]["partial"] + 1,
        )
        self.assertEqual(
            summary["unassessed"],
            PR3_BASELINE["coverage"]["unassessed"] - len(BATCH),
        )
        self.assertEqual(summary["reviewed"], summary["verified"] + summary["partial"])
        self.assertEqual(
            self.queue["summary"],
            {"total": 48, "high": 40, "medium": 6, "low": 2},
        )

    def test_only_aedoor_mappings_are_new_in_this_batch(self) -> None:
        pr2_batch = {
            ("abbs", "lifecycle.disconnect"),
            ("ambos", "terminal.read_key"),
            ("ambos", "terminal.read_line"),
            ("daydream", "lifecycle.exit"),
            ("ucdoor", "terminal.write"),
            ("ucdoor", "terminal.read_line"),
            ("ucdoor", "session.time_left"),
            ("ucdoor", "lifecycle.disconnect"),
        }
        m61_reviewed = set()
        for path in (ROOT / "catalog" / "mappings").glob("*.json"):
            record = json.loads(path.read_text(encoding="utf-8"))
            m61_reviewed.update(
                (record["api"], mapping["operation"])
                for mapping in record["mappings"]
            )
        current_reviewed = {
            (host_id, row["operation"])
            for host_id, host in self.crosswalk["hosts"].items()
            for row in host["operations"]
            if row["status"] in {"verified", "partial"}
        }
        expected = (
            m61_reviewed
            | pr2_batch
            | {("aedoor", operation) for operation in BATCH}
        )
        self.assertEqual(current_reviewed, expected)

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
