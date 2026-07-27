import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ArchitectureBaselineTests(unittest.TestCase):
    def test_architecture_manifest_defines_product_boundaries(self):
        text = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        for heading in (
            "## Primary product",
            "## Product boundaries",
            "## Evidence model",
            "## Repository migration policy",
            "## Non-goals",
        ):
            self.assertIn(heading, text)

    def test_structure_document_preserves_current_paths(self):
        text = (ROOT / "docs" / "project-structure.md").read_text(encoding="utf-8")
        for path in ("`spec/`", "`catalog/", "`tools/ods-tools/`", "`native/`"):
            self.assertIn(path, text)
        self.assertIn("not an instruction to move everything at once", text)

    def test_readme_links_architecture_manifest(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[`ARCHITECTURE.md`](ARCHITECTURE.md)", text)


if __name__ == "__main__":
    unittest.main()
