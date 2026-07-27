import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'ods-tools' / 'src'))

from ods_tools.gaps import build_adapter_gap_report


class M45Tests(unittest.TestCase):
    def test_committed_report_is_current(self):
        stored = json.loads((ROOT / 'catalog/knowledge/adapter-gap-report.json').read_text())
        self.assertEqual(stored, build_adapter_gap_report(ROOT))

    def test_all_targets_cover_every_operation(self):
        report = build_adapter_gap_report(ROOT)
        expected = report['operations']
        for target in [*report['historical_apis'], *report['adapters']]:
            self.assertEqual([row['operation'] for row in target['rows']], expected)
            self.assertEqual(sum(target['summary'].values()), len(expected))

    def test_reference_adapters_are_complete(self):
        report = build_adapter_gap_report(ROOT)
        for adapter in report['adapters']:
            self.assertEqual(adapter['summary']['missing'], 0)
            self.assertEqual(adapter['summary']['partial'], 0)

    def test_cli_can_inspect_target(self):
        result = subprocess.run(
            [sys.executable, '-m', 'ods_tools', 'gaps', 'api:daydream'],
            cwd=ROOT,
            env={'PYTHONPATH': str(ROOT / 'tools/ods-tools/src')},
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn('terminal.write', result.stdout)
        self.assertIn('summary:', result.stdout)

    def test_cli_rejects_ambiguous_short_target(self):
        result = subprocess.run(
            [sys.executable, '-m', 'ods_tools', 'gaps', 'daydream'],
            cwd=ROOT,
            env={'PYTHONPATH': str(ROOT / 'tools/ods-tools/src')},
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ambiguous target', result.stderr)


if __name__ == '__main__':
    unittest.main()
