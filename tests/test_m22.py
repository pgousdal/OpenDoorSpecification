import hashlib, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M22Tests(unittest.TestCase):
 def test_archive_expansion(self):
  d=json.loads((ROOT/'catalog/archive-index.json').read_text())
  self.assertEqual(d['archive_count'],17)
  self.assertEqual(d['entry_count'],429)
 def test_duplicate_evidence(self):
  d=json.loads((ROOT/'catalog/evidence/duplicate-archives.json').read_text())
  self.assertEqual(len(d['duplicates']),2)
  self.assertTrue(all(x['status']=='byte-identical' for x in d['duplicates']))
 def test_paragon_evidence(self):
  d=json.loads((ROOT/'catalog/evidence/paragon-message-protocol.json').read_text())
  ids={x['id'] for x in d['findings']}
  self.assertTrue({'command-1','command-6','command-8','command-20','carrier-field'} <= ids)
 def test_paragon_mapping_reviewed(self):
  d=json.loads((ROOT/'catalog/mappings/paragon.json').read_text())
  self.assertGreaterEqual(len(d['mappings']),7)
  self.assertTrue(all(x['semantic_review']=='reviewed' for x in d['mappings']))
 def test_no_embedded_nul_paths(self):
  for p in (ROOT/'catalog/archives').glob('*.json'):
   d=json.loads(p.read_text())
   self.assertTrue(all('\x00' not in e['path'] for e in d['entries']),p.name)
