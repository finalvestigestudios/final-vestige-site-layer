"""R343 isolated CLI test: absence of native witness must remain invalid."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parents[1] / 'tools' / 'r343_native_claim_review_run.py'

class IsolatedEntrypoint(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-I', str(RUNNER), *map(str,args)],capture_output=True,text=True)
    def test_isolated_runner_executable(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.run_cli('--repo-root',td)
            self.assertEqual(p.returncode,1,p.stderr)
            r=json.loads(p.stdout)
            self.assertEqual(r['state'],'INVALID_HARD_HOLD')
            self.assertIn('R337_41_ENTRY_PINNED_GIT_AND_DEPTH_GATE_FAILED',r['errors'])
    def test_isolated_runner_never_approves(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.run_cli('--repo-root',td)
            r=json.loads(p.stdout)
            self.assertFalse(r['qualified_qd_pass'])
            self.assertFalse(r['may_publish'])
            self.assertFalse(r['paid_sku_verified'])
    def test_no_report_write_inside_repository(self):
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/'report.json'
            p=self.run_cli('--repo-root',td,'--output',output)
            self.assertEqual(p.returncode,1)
            self.assertFalse(output.exists())
            self.assertIn('NO_WRITING_REPORT_IN_SOURCE_REPOSITORY',p.stdout)
    def test_external_report_preserves_invalid_hard_hold(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as out:
            target=Path(out)/'report.json'
            p=self.run_cli('--repo-root',td,'--output',target)
            self.assertEqual(p.returncode,1)
            self.assertEqual(json.loads(target.read_text())['state'],'INVALID_HARD_HOLD')

if __name__ == '__main__':unittest.main()
