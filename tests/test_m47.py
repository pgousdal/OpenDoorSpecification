import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M47Tests(unittest.TestCase):
 def test_archive_totals(self):
  d=json.loads((ROOT/'catalog/archive-index.json').read_text())
  self.assertEqual((d['archive_count'],d['entry_count']),(38, 1371))
 def test_manifests(self):
  expected={'acp300':34,'ax300':116,'magnum-chat-1.1':12,'multi-quest-1.1':5}
  for name,count in expected.items():
   d=json.loads((ROOT/'catalog/archives'/f'{name}.json').read_text())
   self.assertEqual(d['entry_count'],count)
 def test_duplicate_redistributions(self):
  d=json.loads((ROOT/'catalog/evidence/duplicate-archives.json').read_text())
  names={x['uploaded'] for x in d['duplicates']}
  for name in ['MaxPro2 (1).lha','DayDreamBBS (1).lha','DayDreamBBSDev (1).lha','DayDreamBBSDoo (1).lha','max_e (1).lha']:
   self.assertIn(name,names)
 def test_research_boundary(self):
  d=json.loads((ROOT/'catalog/evidence/m47-archive-research.json').read_text())
  self.assertEqual(len(d['archives']),4)
  acp=next(x for x in d['archives'] if x['archive']=='acp300.lzh')
  self.assertIn('-lh1-',acp['compression_methods'])
  self.assertIn('No door API mapping added',acp['ods_result'])
 def test_documented_doors_join_corpus(self):
  d=json.loads((ROOT/'catalog/evidence/historical-door-corpus.json').read_text())
  rows={x['archive']:x for x in d['archives']}
  self.assertEqual(rows['mAG-cH_11.lha']['evidence_status'],'documented')
  self.assertEqual(rows['M_Quest_v11.lha']['evidence_status'],'documented')
