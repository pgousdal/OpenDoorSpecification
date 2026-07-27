from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"
sys.path.insert(0, str(TOOLS_SRC))

from ods_tools.crosswalk import load_crosswalk
from ods_tools.crosswalk_work_queue import (
    PRIORITIES,
    build_crosswalk_work_queue,
    select_crosswalk_work_queue,
    validate_crosswalk_work_queue,
)
from ods_tools.cli import validate


GENERATOR_PATH = ROOT / "tools" / "generate_crosswalk_work_queue.py"
spec = importlib.util.spec_from_file_location(
    "generate_crosswalk_work_queue", GENERATOR_PATH
)
generator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(generator)


class M62CrosswalkWorkQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.queue = build_crosswalk_work_queue(ROOT)
        self.crosswalk = load_crosswalk(ROOT)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "ods_tools", *args],
            cwd=ROOT,
            env={"PYTHONPATH": str(TOOLS_SRC)},
            text=True,
            capture_output=True,
            check=False,
        )

    def test_queue_is_exactly_the_unassessed_cells(self) -> None:
        expected = {
            f"{host_id}:{cell['operation']}"
            for host_id, host in self.crosswalk["hosts"].items()
            for cell in host["operations"]
            if cell["status"] == "unassessed"
        }
        actual = {item["id"] for item in self.queue["items"]}
        self.assertEqual(actual, expected)
        self.assertEqual(len(self.queue["items"]), len(expected))
        self.assertTrue(
            all(item["status"] == "unassessed" for item in self.queue["items"])
        )

    def test_reviewed_cells_are_excluded(self) -> None:
        reviewed = {
            f"{host_id}:{cell['operation']}"
            for host_id, host in self.crosswalk["hosts"].items()
            for cell in host["operations"]
            if cell["status"] in {"verified", "partial"}
        }
        self.assertTrue(reviewed.isdisjoint(item["id"] for item in self.queue["items"]))

    def test_ids_priorities_reasons_and_order_are_deterministic(self) -> None:
        items = self.queue["items"]
        ids = [item["id"] for item in items]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item["priority"] in PRIORITIES for item in items))
        self.assertTrue(all(item["reasons"] for item in items))
        rank = {priority: index for index, priority in enumerate(PRIORITIES)}
        self.assertEqual(
            [(rank[item["priority"]], item["id"]) for item in items],
            sorted((rank[item["priority"]], item["id"]) for item in items),
        )
        self.assertEqual(self.queue, build_crosswalk_work_queue(ROOT))

    def test_host_operation_and_priority_selection(self) -> None:
        host = select_crosswalk_work_queue(ROOT, "paragon")
        self.assertTrue(host["items"])
        self.assertTrue(all(item["host"] == "paragon" for item in host["items"]))
        operation = select_crosswalk_work_queue(ROOT, "terminal.write")
        self.assertTrue(operation["items"])
        self.assertTrue(
            all(item["operation"] == "terminal.write" for item in operation["items"])
        )
        high = select_crosswalk_work_queue(ROOT, priority="high")
        self.assertTrue(high["items"])
        self.assertTrue(all(item["priority"] == "high" for item in high["items"]))

    def test_cli_summary_and_filters(self) -> None:
        summary = self.run_cli("crosswalk", "--work-queue")
        self.assertEqual(summary.returncode, 0, summary.stderr)
        self.assertIn("crosswalk evidence work queue", summary.stdout)
        self.assertIn("high ", summary.stdout)

        host = self.run_cli("crosswalk", "paragon", "--work-queue")
        self.assertEqual(host.returncode, 0, host.stderr)
        self.assertTrue(
            all(
                "paragon:" in line
                for line in host.stdout.splitlines()[1:]
                if line and "no matching" not in line
            )
        )

        operation = self.run_cli(
            "crosswalk", "terminal.write", "--work-queue"
        )
        self.assertEqual(operation.returncode, 0, operation.stderr)
        self.assertIn(":terminal.write", operation.stdout)

        priority = self.run_cli(
            "crosswalk", "--work-queue", "--priority", "high"
        )
        self.assertEqual(priority.returncode, 0, priority.stderr)
        self.assertNotIn("\nmedium ", priority.stdout)
        self.assertNotIn("\nlow    ", priority.stdout)

    def test_cli_json_unknown_target_and_invalid_priority(self) -> None:
        result = self.run_cli("crosswalk", "--work-queue", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), self.queue)

        unknown = self.run_cli("crosswalk", "not-a-host", "--work-queue")
        self.assertNotEqual(unknown.returncode, 0)
        self.assertIn("unknown crosswalk work-queue target", unknown.stderr)

        invalid = self.run_cli(
            "crosswalk", "--work-queue", "--priority", "urgent"
        )
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("invalid choice", invalid.stderr)

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
            output = Path(directory) / "work-queue.json"
            self.assertEqual(generator.generate(ROOT, output), 0)
            first = output.read_bytes()
            self.assertEqual(generator.generate(ROOT, output), 0)
            self.assertEqual(output.read_bytes(), first)
            self.assertEqual(
                first,
                (ROOT / "catalog" / "crosswalk" / "work-queue.json").read_bytes(),
            )

    def test_stale_generated_data_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "catalog" / "census", root / "catalog" / "census")
            shutil.copytree(
                ROOT / "catalog" / "crosswalk", root / "catalog" / "crosswalk"
            )
            self.assertEqual(
                validate_crosswalk_work_queue(root),
                self.queue["summary"]["total"],
            )
            path = root / "catalog" / "crosswalk" / "work-queue.json"
            stored = json.loads(path.read_text(encoding="utf-8"))
            stored["items"][0]["reasons"].append("stale test value")
            path.write_text(json.dumps(stored, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(
                AssertionError, "stale crosswalk work queue"
            ):
                validate_crosswalk_work_queue(root)

    def test_strict_validation_rejects_stale_queue(self) -> None:
        stale = dict(self.queue)
        stale["summary"] = {**stale["summary"], "total": -1}
        with mock.patch(
            "ods_tools.cli.build_crosswalk_work_queue",
            return_value=stale,
        ):
            with self.assertRaisesRegex(
                AssertionError, "stale crosswalk work queue"
            ):
                validate(ROOT, strict=True)

    def test_schema_and_documentation_exist(self) -> None:
        self.assertTrue(
            (ROOT / "schemas" / "crosswalk-work-queue.schema.json").exists()
        )
        self.assertTrue((ROOT / "docs" / "m62-crosswalk-work-queue.md").exists())


if __name__ == "__main__":
    unittest.main()
