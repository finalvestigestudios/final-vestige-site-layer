#!/usr/bin/env python3
"""Independent adversarial tests: avoid accepting a passing *log* as source identity."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from archive_identity_gate import git_blob, inspect, ROOT, main


class IdentityGateTest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / 'manifest.json').read_text())['reviewed']

    def fixture(self, entries):
        b = io.BytesIO()
        with ZipFile(b, 'w') as z:
            for name, data in entries:
                z.writestr(name, data)
        b.seek(0)
        return b

    def test_git_blob_matches_known_sha(self):
        self.assertEqual(git_blob(b'hello\n'), 'ce013625030ba8dba906f756967f9e9ca394464a')

    def test_green_logs_cannot_override_tampered_source(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'candidate.zip'
            with ZipFile(p,'w') as z:
                z.writestr('README.md','forged provenance')
                z.writestr('QA/browser-tests.log','999/999 PASS')
            r = inspect(p,self.manifest['r417']['files'])
            self.assertEqual(r['result'],'HOLD')
            self.assertTrue(any(x['status']=='SOURCE_DRIFT' for x in r['findings']))
            self.assertTrue(any(x['status']=='MISSING_SOURCE' for x in r['findings']))

    def test_extra_source_and_duplicate_entry_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'candidate.zip'
            with ZipFile(p,'w') as z:
                z.writestr('unknown.php','<?php echo 1;')
                z.writestr('unknown.php','<?php echo 2;')
            result=inspect(p,{})
            self.assertEqual(result['result'],'HOLD')
            self.assertEqual({x['status'] for x in result['findings']},{'DUPLICATE_ENTRY','UNREVIEWED_SOURCE'})

    def test_clean_expected_archive_passes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'valid.zip'
            data=b'hello\n'
            with ZipFile(p,'w') as z:
                z.writestr('file.txt',data)
                z.writestr('QA/screenshot.png',b'image')
            self.assertEqual(inspect(p,{'file.txt':git_blob(data)})['result'],'PASS')

    def test_r417_actual_archive_is_hold(self):
        p=Path('/mnt/data/apollo_r417_lab/experience2/apollo-r417/QA/Apollo_R417_Local_Evidence.zip')
        if not p.exists(): self.skipTest('separate historical evidence archive is not mounted')
        r=inspect(p,self.manifest['r417']['files'])
        self.assertEqual(r['result'],'HOLD')
        self.assertEqual(len(r['findings']),4)

    def test_r421_actual_archive_matches_exact_head(self):
        p=Path('/mnt/data/fv_apollo_r421/experience2/apollo-r421/QA/Apollo_R421_Local_Evidence.zip')
        if not p.exists(): self.skipTest('separate historical evidence archive is not mounted')
        r=inspect(p,self.manifest['r421']['files'])
        self.assertEqual(r['result'],'PASS')
        self.assertEqual(len(r['findings']),0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
