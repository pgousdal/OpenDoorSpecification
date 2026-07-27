from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"
sys.path.insert(0, str(TOOLS_SRC))

from ods_tools.cli import validate
from ods_tools.crosswalk import load_crosswalk
from ods_tools.crosswalk_triage import (
    CATEGORIES,
    CONFIDENCES,
    DOCUMENTATION_QUALITIES,
    EFFORTS,
    RECOMMENDED_PRIORITIES,
    build_crosswalk_triage,
    select_crosswalk_triage,
    validate_crosswalk_triage,
)
from ods_tools.crosswalk_work_queue import build_crosswalk_work_queue


GENERATOR_PATH = ROOT / "tools" / "generate_crosswalk_triage.py"
spec = importlib.util.spec_from_file_location(
    "generate_crosswalk_triage", GENERATOR_PATH
)
generator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(generator)


class M62CrosswalkTriageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.triage = build_crosswalk_triage(ROOT)
        cls.queue = build_crosswalk_work_queue(ROOT)
        cls.crosswalk = load_crosswalk(ROOT)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "ods_tools", *args],
            cwd=ROOT,
            env={"PYTHONPATH": str(TOOLS_SRC)},
            text=True,
            capture_output=True,
            check=False,
        )

    def test_triage_exactly_covers_queue_once(self) -> None:
        queue_ids = [item["id"] for item in self.queue["items"]]
        triage_ids = [item["id"] for item in self.triage["items"]]
        self.assertEqual(triage_ids, queue_ids)
        self.assertEqual(len(triage_ids), len(set(triage_ids)))
        self.assertEqual(self.triage["summary"]["total"], len(queue_ids))

    def test_no_reviewed_mapping_is_triaged(self) -> None:
        reviewed = {
            f"{host}:{cell['operation']}"
            for host, record in self.crosswalk["hosts"].items()
            for cell in record["operations"]
            if cell["status"] in {"verified", "partial"}
        }
        self.assertTrue(
            reviewed.isdisjoint(item["id"] for item in self.triage["items"])
        )
        self.assertTrue(
            all(item["status"] == "unassessed" for item in self.triage["items"])
        )

    def test_vocabularies_and_distributions_are_valid(self) -> None:
        self.assertTrue(
            all(item["category"] in CATEGORIES for item in self.triage["items"])
        )
        self.assertTrue(
            all(item["effort"] in EFFORTS for item in self.triage["items"])
        )
        self.assertTrue(
            all(item["confidence"] in CONFIDENCES for item in self.triage["items"])
        )
        for field, vocabulary in (
            ("categories", CATEGORIES),
            ("efforts", EFFORTS),
            ("confidences", CONFIDENCES),
        ):
            distribution = self.triage["summary"][field]
            self.assertEqual(list(distribution), list(vocabulary))
            self.assertEqual(sum(distribution.values()), len(self.triage["items"]))

    def test_host_summaries_cover_every_remaining_host(self) -> None:
        expected_hosts = {item["host"] for item in self.queue["items"]}
        summaries = {item["host"]: item for item in self.triage["hosts"]}
        self.assertEqual(set(summaries), expected_hosts)
        for host, summary in summaries.items():
            host_items = [
                item for item in self.triage["items"] if item["host"] == host
            ]
            reviewed = sum(
                cell["status"] in {"verified", "partial"}
                for cell in self.crosswalk["hosts"][host]["operations"]
            )
            self.assertEqual(summary["reviewed_mappings"], reviewed)
            self.assertEqual(summary["remaining_mappings"], len(host_items))
            self.assertTrue(summary["triage_categories"])
            self.assertTrue(summary["next_evidence_opportunity"])
            self.assertIn(
                summary["documentation_quality"], DOCUMENTATION_QUALITIES
            )
            self.assertIn(
                summary["recommended_priority"], RECOMMENDED_PRIORITIES
            )

    def test_host_selection(self) -> None:
        report = select_crosswalk_triage(ROOT, "ambos")
        self.assertTrue(report["items"])
        self.assertTrue(all(item["host"] == "ambos" for item in report["items"]))
        self.assertEqual(report["filters"], {"host": "ambos"})
        with self.assertRaises(KeyError):
            select_crosswalk_triage(ROOT, "missing-host")

    def test_cli_text_json_and_host_filter(self) -> None:
        text = self.run_cli("crosswalk", "--triage")
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn("remaining evidence triage", text.stdout)
        self.assertIn("documented-but-not-reviewed", text.stdout)

        payload = self.run_cli("crosswalk", "--triage", "--json")
        self.assertEqual(payload.returncode, 0, payload.stderr)
        self.assertEqual(json.loads(payload.stdout), self.triage)

        host = self.run_cli("crosswalk", "--triage", "--host", "ambos")
        self.assertEqual(host.returncode, 0, host.stderr)
        self.assertIn("ambos", host.stdout)
        self.assertNotIn("door-io:", host.stdout)

        unknown = self.run_cli(
            "crosswalk", "--triage", "--host", "missing-host"
        )
        self.assertNotEqual(unknown.returncode, 0)
        self.assertIn("unknown crosswalk triage host", unknown.stderr)

    def test_generator_check_and_byte_identical_generation(self) -> None:
        check = subprocess.run(
            [sys.executable, str(GENERATOR_PATH), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(check.returncode, 0, check.stderr)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "triage.json"
            self.assertEqual(generator.generate(ROOT, output), 0)
            first = output.read_bytes()
            self.assertEqual(generator.generate(ROOT, output), 0)
            self.assertEqual(output.read_bytes(), first)
            self.assertEqual(
                first,
                (ROOT / "catalog" / "crosswalk" / "triage.json").read_bytes(),
            )

    def test_validation_integration_rejects_stale_triage(self) -> None:
        self.assertEqual(validate_crosswalk_triage(ROOT), len(self.queue["items"]))
        stale = dict(self.triage)
        stale["summary"] = {**stale["summary"], "total": -1}
        with mock.patch(
            "ods_tools.cli.build_crosswalk_triage",
            return_value=stale,
        ):
            with self.assertRaisesRegex(
                AssertionError, "stale crosswalk evidence triage"
            ):
                validate(ROOT)

    def test_schema_and_documentation_exist(self) -> None:
        self.assertTrue(
            (ROOT / "schemas" / "crosswalk-triage.schema.json").exists()
        )
        self.assertTrue((ROOT / "docs" / "m62-evidence-triage.md").exists())


if __name__ == "__main__":
    unittest.main()
