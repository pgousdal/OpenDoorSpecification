import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CatalogTests(unittest.TestCase):
    def test_archive_counts(self):
        manifests=[json.loads(p.read_text()) for p in (ROOT/'catalog/archives').glob('*.json')]
        self.assertGreaterEqual(len(manifests),11)
        index=json.loads((ROOT/'catalog/archive-index.json').read_text())
        self.assertEqual(len(manifests),index['archive_count'])
        self.assertEqual(sum(m['entry_count'] for m in manifests),index['entry_count'])
        for m in manifests:
            self.assertEqual(m['entry_count'],len(m['entries']))
    def test_api_ids_unique(self):
        items=[json.loads(p.read_text()) for p in (ROOT/'catalog/apis').glob('*.json')]
        ids=[x['id'] for x in items]
        self.assertEqual(len(ids),len(set(ids)))
if __name__=='__main__': unittest.main()
