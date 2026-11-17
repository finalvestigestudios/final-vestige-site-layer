#!/usr/bin/env python3
"""Prove the R424 gate cannot be fooled with missing, changed or redirected source."""
import pathlib, tempfile, unittest
from real_research_desk_acceptance import PR158, git_blob, custody, run

class GateTests(unittest.TestCase):
    def test_git_object_known(self):
        self.assertEqual(git_blob(b'test'),'30d74d258442c7c65512eafab474568dd706c430')
    def test_missing_source_hold(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            self.assertEqual(run(p,p,p/'qa',False),2)
            self.assertIn('missing or changed',(p/'qa/receipt.json').read_text())
    def test_tampering_hold(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d);(p/'templates').mkdir()
            (p/'templates/ledger.html').write_text('tampered')
            r=custody(p,{'templates/ledger.html':PR158['templates/ledger.html']})
            self.assertEqual(r[0]['state'],'FAIL')
    def test_valid_object(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d);(p/'test.js').write_text('safe')
            self.assertEqual(custody(p,{'test.js':git_blob(b'safe')})[0]['state'],'PASS')
    def test_escape_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d);(p/'root').mkdir();(p/'outside').write_text('safe')
            (p/'root/alias').symlink_to(p/'outside')
            self.assertEqual(custody(p/'root',{'alias':git_blob(b'safe')})[0]['state'],'BLOCKED')

if __name__=='__main__':unittest.main(verbosity=2)
