import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/ods-tools/src'))
from ods_tools.parsers.lha import inspect
class LhaTests(unittest.TestCase):
    def test_known_inventory_if_archive_available(self):
        archive=Path('/mnt/data/DoorRunner.lha')
        if not archive.exists(): self.skipTest('fixture unavailable')
        result=inspect(archive)
        self.assertEqual(result['entry_count'],14)
        self.assertTrue(any('guide' in e['path'].lower() for e in result['entries']))
if __name__=='__main__': unittest.main()
