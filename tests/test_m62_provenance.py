from __future__ import annotations

import copy
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

from ods_tools.crosswalk import load_crosswalk
from ods_tools.crosswalk_evidence import (
    EvidenceValidationError,
    validate_crosswalk_evidence,
)


def load_generator(name: str):
    path = ROOT / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


generate_crosswalk = load_generator("generate_crosswalk")
generate_coverage = load_generator("generate_crosswalk_coverage")
generate_queue = load_generator("generate_crosswalk_work_queue")


class M62ProvenanceValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = load_crosswalk(ROOT)

    def cell(
        self,
        data: dict,
        host: str = "ucdoor",
        operation: str = "terminal.write",
    ) -> dict:
        return next(
            row
            for row in data["hosts"][host]["operations"]
            if row["operation"] == operation
        )

    def assert_invalid(self, mutate, message: str) -> None:
        data = copy.deepcopy(self.data)
        mutate(data)
        with self.assertRaisesRegex(EvidenceValidationError, message):
            validate_crosswalk_evidence(ROOT, data)

    def test_existing_repository_has_complete_provenance(self) -> None:
        reviewed = sum(
            row["status"] in {"verified", "partial"}
            for host in self.data["hosts"].values()
            for row in host["operations"]
        )
        self.assertEqual(validate_crosswalk_evidence(ROOT), reviewed)

    def test_missing_required_evidence_fields(self) -> None:
        cases = (
            (
                "archive",
                lambda data: self.cell(data)["evidence"][0].pop("archive"),
                "archive must be a non-empty string",
            ),
            (
                "document",
                lambda data: self.cell(data)["evidence"][0].pop("path"),
                "path must be a non-empty string",
            ),
            (
                "symbol",
                lambda data: self.cell(data)["evidence"][0].pop("symbol"),
                "symbol must be a non-empty string",
            ),
        )
        for name, mutate, message in cases:
            with self.subTest(name=name):
                self.assert_invalid(mutate, message)

    def test_partial_without_limitations(self) -> None:
        self.assert_invalid(
            lambda data: self.cell(
                data, "ucdoor", "terminal.read_line"
            ).update(limitations=[]),
            "partial mapping requires limitations",
        )

    def test_orphan_cross_references(self) -> None:
        cases = (
            (
                "archive",
                lambda data: self.cell(data)["evidence"][0].update(
                    archive="missing.lha"
                ),
                "orphan archive reference",
            ),
            (
                "document",
                lambda data: self.cell(data)["evidence"][0].update(
                    path="missing/document.txt"
                ),
                "orphan document reference",
            ),
            (
                "census",
                lambda data: data["hosts"]["ucdoor"]["host"].update(
                    census_path="catalog/census/missing.json"
                ),
                "orphan census reference",
            ),
            (
                "operation",
                lambda data: self.cell(data).update(
                    operation="missing.operation"
                ),
                "orphan canonical operation",
            ),
            (
                "provenance",
                lambda data: self.cell(
                    data, "daydream", "terminal.write"
                ).update(provenance=["prov.missing.mapping.1"]),
                "orphan provenance reference",
            ),
        )
        for name, mutate, message in cases:
            with self.subTest(name=name):
                self.assert_invalid(mutate, message)

    def test_duplicate_evidence_entry(self) -> None:
        def mutate(data):
            cell = self.cell(data)
            cell["evidence"].append(copy.deepcopy(cell["evidence"][0]))

        self.assert_invalid(mutate, "duplicate evidence entry")

    def test_invalid_status_and_provenance_structure(self) -> None:
        cases = (
            (
                "status",
                lambda data: self.cell(data).update(status="supported"),
                "invalid status",
            ),
            (
                "structure",
                lambda data: self.cell(data).update(evidence=["not-an-object"]),
                "must be an object",
            ),
            (
                "placeholder",
                lambda data: self.cell(data).update(rationale="TODO"),
                "placeholder text",
            ),
            (
                "impossible",
                lambda data: self.cell(data).update(status="unassessed"),
                "unassessed cell contains reviewed evidence",
            ),
        )
        for name, mutate, message in cases:
            with self.subTest(name=name):
                self.assert_invalid(mutate, message)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "ods_tools", *args],
            cwd=ROOT,
            env={"PYTHONPATH": str(TOOLS_SRC)},
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_evidence_text_and_json(self) -> None:
        text = self.run_cli(
            "crosswalk", "ucdoor", "terminal.write", "--evidence"
        )
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn("ucdoor:terminal.write", text.stdout)
        self.assertIn("ucdoor10.lha", text.stdout)
        self.assertIn("cd_PutStr", text.stdout)

        payload = self.run_cli(
            "crosswalk",
            "daydream",
            "lifecycle.exit",
            "--evidence",
            "--json",
        )
        self.assertEqual(payload.returncode, 0, payload.stderr)
        record = json.loads(payload.stdout)
        self.assertEqual(record["id"], "daydream:lifecycle.exit")
        self.assertTrue(record["evidence"])

    def test_cli_validate_evidence(self) -> None:
        result = self.run_cli("crosswalk", "--validate-evidence")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Crosswalk evidence is valid", result.stdout)

    def test_strict_validation_propagates_evidence_failure(self) -> None:
        data = copy.deepcopy(self.data)
        self.cell(data)["evidence"][0].pop("archive")
        operation = next(
            item
            for item in data["operations"]["operations"]
            if item["id"] == "terminal.write"
        )
        operation["hosts"]["ucdoor"]["evidence"][0].pop("archive")
        with mock.patch("ods_tools.crosswalk.load_crosswalk", return_value=data):
            from ods_tools.crosswalk import validate_crosswalk

            with self.assertRaisesRegex(
                EvidenceValidationError, "archive must be a non-empty string"
            ):
                validate_crosswalk(ROOT)

    def test_generator_checks_fail_on_invalid_provenance(self) -> None:
        failure = EvidenceValidationError("test: invalid provenance")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            cases = (
                (
                    generate_crosswalk,
                    lambda: generate_crosswalk.generate(
                        ROOT / "catalog" / "census",
                        output / "crosswalk",
                        check=True,
                    ),
                ),
                (
                    generate_coverage,
                    lambda: generate_coverage.generate(
                        ROOT,
                        output / "coverage.json",
                        check=True,
                    ),
                ),
                (
                    generate_queue,
                    lambda: generate_queue.generate(
                        ROOT,
                        output / "work-queue.json",
                        check=True,
                    ),
                ),
            )
            for module, call in cases:
                with self.subTest(generator=module.__name__):
                    with mock.patch.object(
                        module,
                        "validate_crosswalk_evidence",
                        side_effect=failure,
                    ):
                        self.assertEqual(call(), 1)


if __name__ == "__main__":
    unittest.main()
