import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools" / "generate_crosswalk.py"

spec = importlib.util.spec_from_file_location("generate_crosswalk", GENERATOR_PATH)
generate_crosswalk = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(generate_crosswalk)


class M61CrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.index = json.loads(
            (ROOT / "catalog/crosswalk/index.json").read_text(encoding="utf-8")
        )
        self.operations = json.loads(
            (ROOT / "catalog/crosswalk/operations.json").read_text(encoding="utf-8")
        )

    def test_index_matches_census_hosts(self):
        census = json.loads(
            (ROOT / "catalog/census/index.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.index["host_count"], census["system_count"])
        self.assertEqual(
            [host["id"] for host in self.index["hosts"]],
            sorted(system["id"] for system in census["systems"]),
        )

    def test_every_host_has_explicit_status_for_every_operation(self):
        expected = [
            operation["id"] for operation in self.operations["operations"]
        ]
        for summary in self.index["hosts"]:
            record = json.loads(
                (ROOT / summary["path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(
                [operation["operation"] for operation in record["operations"]],
                expected,
            )
            for operation in record["operations"]:
                self.assertIn(
                    operation["status"], {"verified", "partial", "unassessed"}
                )

    def test_unassessed_is_not_unsupported(self):
        for summary in self.index["hosts"]:
            record = json.loads(
                (ROOT / summary["path"]).read_text(encoding="utf-8")
            )
            statuses = {operation["status"] for operation in record["operations"]}
            self.assertNotIn("unsupported", statuses)

    def test_reviewed_mappings_preserve_census_symbols(self):
        for summary in self.index["hosts"]:
            census = json.loads(
                (ROOT / "catalog/census" / f"{summary['id']}.json").read_text(
                    encoding="utf-8"
                )
            )
            crosswalk = json.loads(
                (ROOT / summary["path"]).read_text(encoding="utf-8")
            )
            by_operation = {
                operation["operation"]: operation
                for operation in crosswalk["operations"]
            }
            for mapping in census["mappings"]:
                derived = by_operation[mapping["operation"]]
                self.assertEqual(derived["status"], mapping["status"])
                self.assertEqual(derived["symbols"], mapping.get("symbols", []))
                self.assertEqual(
                    derived["semantic_review"],
                    mapping.get("semantic_review", "unknown"),
                )

    def test_generator_is_deterministic_and_committed_output_is_current(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            self.assertEqual(
                generate_crosswalk.generate(
                    ROOT / "catalog" / "census", out, check=False
                ),
                0,
            )
            for path in [
                "index.json",
                "operations.json",
                *[f"{host['id']}.json" for host in self.index["hosts"]],
            ]:
                self.assertEqual(
                    (out / path).read_text(encoding="utf-8"),
                    (ROOT / "catalog" / "crosswalk" / path).read_text(
                        encoding="utf-8"
                    ),
                )

    def test_schema_and_documentation_exist(self):
        self.assertTrue((ROOT / "schemas/crosswalk.schema.json").exists())
        self.assertTrue((ROOT / "docs/m61-crosswalk-data-model.md").exists())


if __name__ == "__main__":
    unittest.main()
