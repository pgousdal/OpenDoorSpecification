import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M23Tests(unittest.TestCase):
 def test_archive_totals(self):
  d=json.loads((ROOT/'catalog/archive-index.json').read_text())
  self.assertEqual((d['archive_count'],d['entry_count']),(22,713))
 def test_new_manifests_exist(self):
  for n in ['ucdoor10','runraw','mcesrc','c-door-example','aris-doors-for-maxs']:
   self.assertTrue((ROOT/'catalog/archives'/f'{n}.json').is_file(),n)
 def test_observed_corpus(self):
  d=json.loads((ROOT/'catalog/evidence/historical-door-corpus.json').read_text())
  self.assertEqual(len(d['archives']),5)
  aris=next(x for x in d['archives'] if x['archive']=='ArisDoors4MAXs.lha')
  self.assertGreater(aris['observed_calls']['terminal.write'],1000)
  self.assertTrue(all(x['evidence_status']=='observed' for x in d['archives']))
 def test_aedoor_duplicate(self):
  d=json.loads((ROOT/'catalog/evidence/duplicate-archives.json').read_text())
  x=next(x for x in d['duplicates'] if x['uploaded']=='aedoor28(1).lha')
  self.assertEqual(x['canonical'],'aedoor28.lha')
  self.assertEqual(x['status'],'byte-identical')
