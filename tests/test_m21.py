import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST_PATH = "/usr/bin:/bin"
HOST_CC = shutil.which("gcc", path=HOST_PATH)
HOST_AR = shutil.which("ar", path=HOST_PATH)
HOST_MAKE = shutil.which("make", path=HOST_PATH)


class NativeDayDreamTests(unittest.TestCase):
    def test_native_files_and_manifest(self):
        header = ROOT / "native/daydream/include/ods_daydream.h"
        source = ROOT / "native/daydream/src/ods_daydream.c"
        self.assertTrue(header.is_file())
        self.assertTrue(source.is_file())
        manifest = json.loads((ROOT / "catalog/adapters/daydream.json").read_text())
        self.assertEqual(manifest["native_backend"], "portable-c-binding-table")
        self.assertEqual(manifest["conformance"], "host-and-c-tested")

    @unittest.skipUnless(
        HOST_MAKE and HOST_CC and HOST_AR,
        "host GCC toolchain unavailable",
    )
    def test_native_adapter_builds_and_passes(self):
        env = os.environ.copy()
        env["PATH"] = HOST_PATH
        env["CC"] = HOST_CC
        env["AR"] = HOST_AR

        subprocess.run(
            [HOST_MAKE, "-C", str(ROOT / "native/daydream"), "clean", "test"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )


if __name__ == "__main__":
    unittest.main()
