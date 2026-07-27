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
    "lifecycle.disconnect": "verified",
}
PR4_BASELINE = {
    "coverage": {
        "total": 90,
        "reviewed": 42,
        "verified": 30,
        "partial": 12,
        "unassessed": 48,
    },
    "queue": {"total": 48, "high": 40, "medium": 6, "low": 2},
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


class M62FAMEEvidenceBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.crosswalk = load_crosswalk(ROOT)
        cls.coverage = build_crosswalk_coverage(ROOT)
        cls.queue = build_crosswalk_work_queue(ROOT)
        cls.fame = {
            row["operation"]: row
            for row in cls.crosswalk["hosts"]["fame"]["operations"]
        }

    def test_manifest_cells_have_complete_validated_provenance(self) -> None:
        self.assertEqual(validate_crosswalk_evidence(ROOT), 50)
        for operation, status in BATCH.items():
            with self.subTest(operation=operation):
                cell = self.fame[operation]
                self.assertEqual(cell["id"], f"fame:{operation}")
                self.assertEqual(cell["status"], status)
                self.assertEqual(cell["semantic_review"], "reviewed")
                self.assertTrue(cell["symbols"])
                self.assertTrue(cell["evidence"])
                self.assertTrue(cell["rationale"])
                self.assertIn("limitations", cell)

    def test_evidence_resolves_to_cataloged_fcomm130_archive(self) -> None:
        manifest = json.loads(
            (ROOT / "catalog" / "archives" / "fcomm130.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            manifest["source_sha256"],
            "9b010d4c807fe2fca82f784f2fadc31e5f21231f355c9c609a0e0db31e5462db",
        )
        paths = {entry["path"] for entry in manifest["entries"]}
        for operation in BATCH:
            for evidence in self.fame[operation]["evidence"]:
                with self.subTest(operation=operation, evidence=evidence):
                    self.assertEqual(evidence["archive"], "fcomm130.lha")
                    self.assertIn(evidence["path"], paths)
                    self.assertTrue(evidence["symbol"])

    def test_batch_is_removed_from_queue_and_status_set_remains(self) -> None:
        queued = {item["id"] for item in self.queue["items"]}
        self.assertTrue(
            all(f"fame:{operation}" not in queued for operation in BATCH)
        )
        self.assertIn("fame:status.set", queued)

    def test_coverage_and_queue_match_the_declared_pr4_delta(self) -> None:
        summary = self.coverage["summary"]
        self.assertEqual(summary["total"], PR4_BASELINE["coverage"]["total"])
        self.assertEqual(
            summary["reviewed"],
            PR4_BASELINE["coverage"]["reviewed"] + len(BATCH),
        )
        self.assertEqual(
            summary["verified"],
            PR4_BASELINE["coverage"]["verified"] + len(BATCH),
        )
        self.assertEqual(summary["partial"], PR4_BASELINE["coverage"]["partial"])
        self.assertEqual(
            summary["unassessed"],
            PR4_BASELINE["coverage"]["unassessed"] - len(BATCH),
        )
        self.assertEqual(summary["reviewed"], summary["verified"] + summary["partial"])
        self.assertEqual(
            self.queue["summary"],
            {"total": 40, "high": 32, "medium": 6, "low": 2},
        )

    def test_only_fame_mappings_are_new_in_this_batch(self) -> None:
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
            | earlier_batches
            | {("fame", operation) for operation in BATCH}
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
