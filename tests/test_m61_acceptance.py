from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS_SRC = ROOT / "tools" / "ods-tools" / "src"


class M61AcceptanceTests(unittest.TestCase):
    maxDiff = None

    def run_command(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(TOOLS_SRC)
        return subprocess.run(
            args,
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_m61_acceptance(self) -> None:
        for generator in (
            "tools/generate_crosswalk.py",
            "tools/generate_crosswalk_coverage.py",
        ):
            result = self.run_command(sys.executable, generator, "--check")
            self.assertEqual(result.returncode, 0, result.stderr)

        index = json.loads(
            (ROOT / "catalog/crosswalk/index.json").read_text(encoding="utf-8")
        )
        coverage = json.loads(
            (ROOT / "catalog/crosswalk/coverage.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(index["host_count"], 10)
        self.assertEqual(index["operation_count"], 9)
        self.assertEqual(coverage["summary"]["total"], 90)
        self.assertEqual(coverage["summary"]["reviewed"], 34)
        self.assertEqual(
            coverage["summary"]["reviewed"],
            coverage["summary"]["verified"]
            + coverage["summary"]["partial"],
        )
        self.assertEqual(coverage["summary"]["unassessed"], 56)
        self.assertIn(
            "does not mean unsupported",
            coverage["semantics"]["unassessed"],
        )

        commands = (
            ("crosswalk",),
            ("crosswalk", "paragon"),
            ("crosswalk", "terminal.write"),
            ("crosswalk", "--coverage"),
            ("crosswalk", "--gaps"),
            ("validate",),
        )
        for command in commands:
            result = self.run_command(
                sys.executable,
                "-m",
                "ods_tools",
                *command,
            )
            self.assertEqual(
                result.returncode,
                0,
                f"{' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
