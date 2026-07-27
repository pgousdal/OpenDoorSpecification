import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
class M52Tests(unittest.TestCase):
 def test_report_covers_every_upload(self):
  d=json.loads((ROOT/'catalog/evidence/m52-comprehensive-amiexpress-reanalysis.json').read_text())
  self.assertEqual(d['archive_count'],12)
  self.assertEqual(len(d['archives']),12)
  self.assertTrue(all(a['extracted']+a['unextracted']==a['entries'] for a in d['archives']))
 def test_new_source_snapshots_are_not_duplicates(self):
  d=json.loads((ROOT/'catalog/evidence/m52-comprehensive-amiexpress-reanalysis.json').read_text())
  by={a['archive']:a for a in d['archives']}
  self.assertIsNone(by['AmiExpress-master.zip']['duplicate'])
  self.assertIsNone(by['AmiXDoors-master.zip']['duplicate'])
  self.assertGreater(by['AmiExpress-master.zip']['file_types']['amiga-e'],40)
 def test_redistributions_are_byte_identical(self):
  d=json.loads((ROOT/'catalog/evidence/m52-comprehensive-amiexpress-reanalysis.json').read_text())
  for a in d['archives']:
   if a['duplicate'] is not None: self.assertTrue(a['duplicate']['byte_identical'])
 def test_promoted_manifests_and_index(self):
  idx=json.loads((ROOT/'catalog/archive-index.json').read_text())
  self.assertEqual(idx['archive_count'],38)
  self.assertEqual(idx['entry_count'],1371)
  for f in ['amiexpress-master.json','amixdoors-master.json','DoorStatus.json','Mdoors1.json','Mdoors2.json','Mdoors3.json','Mdoors4.json','Mdoors5.json']:
   self.assertTrue((ROOT/'catalog/archives'/f).exists())
 def test_source_provenance_exists(self):
  for f in ['prov.amiexpress.host-source.1.json','prov.amixdoors.behavior-source.1.json']:
   self.assertTrue((ROOT/'catalog/provenance'/f).exists())
if __name__=='__main__': unittest.main()
