import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class M60Tests(unittest.TestCase):
 def setUp(self): self.index=json.loads((ROOT/'catalog/census/index.json').read_text())
 def test_expected_families(self):
  self.assertEqual(self.index['system_count'],10)
  self.assertEqual({x['id'] for x in self.index['systems']},{'abbs','aedoor','ambos','daydream','door-io','fame','paragon','ucdoor','zeus','wwbbs'})
 def test_counts_are_deterministic(self):
  records=[json.loads((ROOT/x['path']).read_text()) for x in self.index['systems']]
  self.assertEqual(self.index['entry_count'],sum(x['entry_count'] for x in records))
  self.assertEqual(self.index['mapping_count'],sum(x['mapping_count'] for x in records))
  for r in records:
   self.assertEqual(r['entry_count'],len(r['entries']))
   self.assertEqual(r['mapping_count'],len(r['mappings']))
 def test_evidence_boundaries(self):
  by={x['id']:json.loads((ROOT/x['path']).read_text()) for x in self.index['systems']}
  self.assertEqual(by['paragon']['evidence_class'],'documented-protocol')
  self.assertEqual(by['ucdoor']['evidence_class'],'wrapper-binding')
  self.assertEqual(by['zeus']['evidence_class'],'observed-doors')
  self.assertEqual(by['wwbbs']['evidence_class'],'observed-doors')
  self.assertEqual(by['ucdoor']['mapping_count'],8)
 def test_all_sources_are_grounded(self):
  for item in self.index['systems']:
   r=json.loads((ROOT/item['path']).read_text())
   for a in r['archives']:
    self.assertTrue((ROOT/'catalog/archives'/a).exists(),a)
   for e in r['entries']:
    self.assertIn(e['kind'],{'function','structure'})
    self.assertTrue(e['name'])
 def test_schema_and_documentation_exist(self):
  self.assertTrue((ROOT/'schemas/api-census.schema.json').exists())
  self.assertTrue((ROOT/'docs/m60-complete-api-census.md').exists())
if __name__=='__main__': unittest.main()
