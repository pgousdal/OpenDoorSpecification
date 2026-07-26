import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M17Tests(unittest.TestCase):
 def test_function_manifests(self):
  files=list((ROOT/'catalog/functions').glob('*.json')); self.assertGreaterEqual(len(files),5)
  for p in files:
   d=json.loads(p.read_text()); self.assertEqual(d['function_count'],len(d['functions']))
 def test_paragon_symbols(self):
  d=json.loads((ROOT/'catalog/functions/paragon.json').read_text()); self.assertGreater(len(d['functions']),0)
 def test_capability_matrix(self):
  d=json.loads((ROOT/'catalog/capabilities/matrix.json').read_text()); self.assertGreaterEqual(len(d['rows']),5)
