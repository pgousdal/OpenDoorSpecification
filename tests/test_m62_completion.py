from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"
sys.path.insert(0, str(TOOLS_SRC))

from ods_tools.cli import validate
from ods_tools.crosswalk import load_crosswalk
from ods_tools.crosswalk_completion import (
    BACKLOG_CLASSES,
    GROUP_POLICY,
    build_m62_completion,
    select_m62_backlog,
    validate_m62_completion,
)
from ods_tools.crosswalk_triage import build_crosswalk_triage
from ods_tools.crosswalk_work_queue import build_crosswalk_work_queue


GENERATOR_PATH = ROOT / "tools" / "generate_crosswalk_completion.py"
SPEC = importlib.util.spec_from_file_location(
    "generate_crosswalk_completion", GENERATOR_PATH
)
GENERATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(GENERATOR)


class M62CompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_m62_completion(ROOT)
        cls.backlog = select_m62_backlog(ROOT)
        cls.queue = build_crosswalk_work_queue(ROOT)
        cls.triage = build_crosswalk_triage(ROOT)
        cls.crosswalk = load_crosswalk(ROOT)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(TOOLS_SRC)
        return subprocess.run(
            [sys.executable, "-m", "ods_tools", *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_completion_report_has_explicit_satisfied_criteria(self) -> None:
        self.assertTrue(self.report["complete"])
        criteria = self.report["criteria"]
        self.assertTrue(criteria)
        self.assertEqual(
            len({criterion["id"] for criterion in criteria}), len(criteria)
        )
        self.assertTrue(all(criterion["satisfied"] for criterion in criteria))
        self.assertTrue(all(criterion["detail"] for criterion in criteria))
        self.assertIn("not a claim", self.report["completion_semantics"])

    def test_backlog_exactly_covers_queue_and_triage_once(self) -> None:
        queue_ids = [item["id"] for item in self.queue["items"]]
        triage_ids = [item["id"] for item in self.triage["items"]]
        backlog_ids = [
            item["id"]
            for group in self.backlog["groups"]
            for item in group["items"]
        ]
        self.assertEqual(queue_ids, triage_ids)
        self.assertEqual(sorted(backlog_ids), sorted(queue_ids))
        self.assertEqual(len(backlog_ids), len(set(backlog_ids)))
        self.assertEqual(self.backlog["summary"]["total"], len(queue_ids))

    def test_backlog_contains_only_unassessed_mappings(self) -> None:
        statuses = {
            f"{host}:{cell['operation']}": cell["status"]
            for host, record in self.crosswalk["hosts"].items()
            for cell in record["operations"]
        }
        for group in self.backlog["groups"]:
            for item in group["items"]:
                self.assertEqual(statuses[item["id"]], "unassessed")

    def test_groups_follow_reason_policy_and_have_complete_summaries(self) -> None:
        for group in self.backlog["groups"]:
            policy = GROUP_POLICY[group["id"]]
            self.assertEqual(group["backlog_class"], policy["backlog_class"])
            self.assertIn(group["backlog_class"], BACKLOG_CLASSES)
            self.assertEqual(group["expected_value"], policy["expected_value"])
            self.assertEqual(
                group["recommended_milestone"],
                policy["recommended_milestone"],
            )
            self.assertEqual(group["item_count"], len(group["items"]))
            self.assertEqual(
                group["affected_hosts"],
                sorted({item["host"] for item in group["items"]}),
            )
            self.assertEqual(
                group["affected_operations"],
                sorted({item["operation"] for item in group["items"]}),
            )
            self.assertEqual(
                sum(group["effort_distribution"].values()),
                group["item_count"],
            )
            self.assertTrue(
                all(item["reason"] == group["id"] for item in group["items"])
            )

    def test_cli_completion_and_backlog_text_and_json(self) -> None:
        completion = self.run_cli("crosswalk", "--completion")
        self.assertEqual(completion.returncode, 0, completion.stderr)
        self.assertIn("M6.2 crosswalk evidence expansion: complete", completion.stdout)
        self.assertIn("PASS", completion.stdout)

        backlog = self.run_cli("crosswalk", "--backlog")
        self.assertEqual(backlog.returncode, 0, backlog.stderr)
        self.assertIn("M6.2 research backlog", backlog.stdout)
        self.assertIn("deferred-research", backlog.stdout)
        self.assertIn("archival-source-discovery", backlog.stdout)

        payload = self.run_cli("crosswalk", "--backlog", "--json")
        self.assertEqual(payload.returncode, 0, payload.stderr)
        self.assertEqual(json.loads(payload.stdout), self.backlog)

    def test_generator_is_deterministic_current_and_detects_stale_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            self.assertEqual(GENERATOR.generate(ROOT, first), 0)
            self.assertEqual(GENERATOR.generate(ROOT, second), 0)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(
                first.read_bytes(),
                (
                    ROOT / "catalog" / "crosswalk" / "m62-completion.json"
                ).read_bytes(),
            )
            self.assertEqual(GENERATOR.generate(ROOT, first, check=True), 0)
            first.write_text("{}\n", encoding="utf-8")
            self.assertEqual(GENERATOR.generate(ROOT, first, check=True), 1)

    def test_validation_accepts_current_and_rejects_stale_completion(self) -> None:
        self.assertEqual(
            validate_m62_completion(ROOT), len(self.queue["items"])
        )
        stale = dict(self.report)
        stale["complete"] = not stale["complete"]
        with patch(
            "ods_tools.cli.build_m62_completion",
            return_value=stale,
        ):
            with self.assertRaisesRegex(
                AssertionError, "stale M6.2 completion report"
            ):
                validate(ROOT)

    def test_schema_and_documentation_exist(self) -> None:
        self.assertTrue(
            (
                ROOT
                / "schemas"
                / "crosswalk-m62-completion.schema.json"
            ).exists()
        )
        self.assertTrue((ROOT / "docs" / "m62-completion.md").exists())


if __name__ == "__main__":
    unittest.main()
