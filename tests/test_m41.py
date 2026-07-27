import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CanonicalKnowledgeModelTests(unittest.TestCase):
    def test_registry_matches_core_operations_and_mapping_apis(self):
        registry = json.loads((ROOT / "catalog/knowledge/id-registry.json").read_text(encoding="utf-8"))
        core = json.loads((ROOT / "catalog/operations/core.json").read_text(encoding="utf-8"))
        self.assertEqual(
            {item["id"] for item in registry["operations"]},
            {item["id"] for item in core["operations"]},
        )
        mapping_apis = {
            json.loads(path.read_text(encoding="utf-8"))["api"]
            for path in (ROOT / "catalog/mappings").glob("*.json")
        }
        self.assertEqual({item["id"] for item in registry["apis"]}, mapping_apis)

    def test_operation_index_contains_every_operation_once(self):
        index = json.loads((ROOT / "catalog/knowledge/operation-index.json").read_text(encoding="utf-8"))
        ids = [item["id"] for item in index["operations"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(11, len(ids))
        self.assertTrue(all(item["definition_ref"] == "catalog/operations/core.json" for item in index["operations"]))

    def test_provenance_schema_uses_common_evidence_vocabulary(self):
        schema = json.loads((ROOT / "schemas/provenance-record.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            ["documented", "observed", "inferred", "unknown"],
            schema["properties"]["status"]["enum"],
        )

    def test_documentation_defines_non_destructive_migration(self):
        text = (ROOT / "docs/canonical-knowledge-model.md").read_text(encoding="utf-8")
        self.assertIn("M4.1 adds an index, not a second source of truth", text)
        self.assertIn("IDs must never be reused", text)


if __name__ == "__main__":
    unittest.main()
