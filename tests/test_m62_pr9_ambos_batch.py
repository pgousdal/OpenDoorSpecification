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
from ods_tools.crosswalk_triage import build_crosswalk_triage
from ods_tools.crosswalk_work_queue import build_crosswalk_work_queue


BATCH = {
    ("ambos", "lifecycle.exit"): "verified",
    ("ambos", "session.identity"): "verified",
}
PR8_BASELINE = {
    "coverage": {
        "total": 90,
        "reviewed": 56,
        "verified": 43,
        "partial": 13,
        "unassessed": 34,
    },
    "queue": {"total": 34, "high": 27, "medium": 5, "low": 2},
    "triage": {
        "total": 34,
        "documented-but-not-reviewed": 2,
        "small": 2,
        "high": 2,
    },
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
    "triage": load_generator("generate_crosswalk_triage"),
}


class M62PR9AmBoSBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.crosswalk = load_crosswalk(ROOT)
        cls.coverage = build_crosswalk_coverage(ROOT)
        cls.queue = build_crosswalk_work_queue(ROOT)
        cls.triage = build_crosswalk_triage(ROOT)

    def cell(self, host: str, operation: str) -> dict:
        return next(
            row
            for row in self.crosswalk["hosts"][host]["operations"]
            if row["operation"] == operation
        )

    def test_manifest_cells_have_complete_validated_provenance(self) -> None:
        self.assertEqual(validate_crosswalk_evidence(ROOT), 58)
        for (host, operation), status in BATCH.items():
            with self.subTest(host=host, operation=operation):
                cell = self.cell(host, operation)
                self.assertEqual(cell["id"], f"{host}:{operation}")
                self.assertEqual(cell["status"], status)
                self.assertEqual(cell["semantic_review"], "reviewed")
                self.assertTrue(cell["symbols"])
                self.assertTrue(cell["evidence"])
                self.assertTrue(cell["rationale"])
                self.assertEqual(cell["limitations"], [])

    def test_evidence_resolves_to_cataloged_ambos_archive(self) -> None:
        manifest = json.loads(
            (ROOT / "catalog" / "archives" / "AmBoS_doc_dev.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            manifest["source_sha256"],
            "1785840c7dc5303bc3d59accdf1250ce003af36bcfd3804917a25207f7259b27",
        )
        paths = {entry["path"] for entry in manifest["entries"]}
        for host, operation in BATCH:
            for evidence in self.cell(host, operation)["evidence"]:
                with self.subTest(operation=operation, evidence=evidence):
                    self.assertEqual(evidence["archive"], "AmBoS_doc_dev.lha")
                    self.assertIn(evidence["path"], paths)
                    self.assertTrue(evidence["symbol"])

    def test_batch_leaves_queue_and_triage_consistently(self) -> None:
        queue_ids = {item["id"] for item in self.queue["items"]}
        triage_ids = {item["id"] for item in self.triage["items"]}
        for host, operation in BATCH:
            item_id = f"{host}:{operation}"
            self.assertNotIn(item_id, queue_ids)
            self.assertNotIn(item_id, triage_ids)
        self.assertEqual(queue_ids, triage_ids)
        self.assertFalse(
            any(
                item["host"] == "ambos"
                and item["effort"] == "small"
                and item["confidence"] == "high"
                for item in self.triage["items"]
            )
        )

    def test_coverage_queue_and_triage_match_pr8_delta(self) -> None:
        summary = self.coverage["summary"]
        self.assertEqual(summary["total"], PR8_BASELINE["coverage"]["total"])
        self.assertEqual(summary["reviewed"], 58)
        self.assertEqual(summary["verified"], 45)
        self.assertEqual(summary["partial"], 13)
        self.assertEqual(summary["unassessed"], 32)
        self.assertEqual(
            self.queue["summary"],
            {"total": 32, "high": 25, "medium": 5, "low": 2},
        )
        self.assertEqual(self.triage["summary"]["total"], 32)
        self.assertEqual(
            self.triage["summary"]["categories"][
                "documented-but-not-reviewed"
            ],
            0,
        )
        self.assertEqual(self.triage["summary"]["efforts"]["small"], 0)
        self.assertEqual(self.triage["summary"]["confidences"]["high"], 0)

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
            ("door-io", "lifecycle.disconnect"),
            ("door-io", "lifecycle.exit"),
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
                self.assertEqual(
                    GENERATORS["triage"].generate(ROOT, root / "triage.json"),
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
