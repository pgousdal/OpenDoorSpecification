import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NativeDayDreamTests(unittest.TestCase):
    def test_native_files_and_manifest(self):
        header = ROOT / "native/daydream/include/ods_daydream.h"
        source = ROOT / "native/daydream/src/ods_daydream.c"
        self.assertTrue(header.is_file())
        self.assertTrue(source.is_file())
        manifest = json.loads((ROOT / "catalog/adapters/daydream.json").read_text())
        self.assertEqual(manifest["native_backend"], "portable-c-binding-table")
        self.assertEqual(manifest["conformance"], "host-and-c-tested")

    @unittest.skipUnless(shutil.which("make") and shutil.which("cc"), "C toolchain unavailable")
    def test_native_adapter_builds_and_passes(self):
        subprocess.run(
            ["make", "-C", str(ROOT / "native/daydream"), "clean", "test"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
