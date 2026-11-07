import io
import json
import os
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from local_cli_bundle import pack, sha, BP_HASH

SOURCE = Path(os.environ.get('FV_EX2_REVIEW_ZIP', 'review-only-source.zip'))

class BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SOURCE.is_file():
            raise RuntimeError('Provide exact PR #1379 source ZIP via FV_EX2_REVIEW_ZIP (fail closed)')
        cls.src=SOURCE.read_bytes()
    def test_repeatable_compact(self):
        a, _ = pack(self.src); b, _ = pack(self.src)
        self.assertEqual(a,b)
        self.assertLess(len(a),len(self.src)//2)
    def test_bundle_extracted_import_steps_and_privacy(self):
        blob, receipt = pack(self.src)
        with ZipFile(io.BytesIO(blob)) as z:
            self.assertEqual(len(z.namelist()),5)
            bp=json.loads(z.read('blueprint.json'))
            self.assertEqual(bp['landingPage'],'/')
            self.assertEqual(receipt['exact_source_sha256'],BP_HASH)
            self.assertEqual(sum(s['step']=='runPHP' for s in bp['steps']),2)
            for s in bp['steps']:
                if s['step']=='writeFile':
                    self.assertEqual(s['data']['resource'],'bundled')
                    self.assertTrue(z.read(s['data']['path'].lstrip('/')).startswith(b'<?php'))
            self.assertIn(b'Never install on production',z.read('REVIEW.txt'))
            self.assertFalse(any(p.endswith(('.sql','.env')) for p in z.namelist()))
    def _changed(self, which, before, after):
        with ZipFile(io.BytesIO(self.src)) as z:
            files={p:z.read(p) for p in z.namelist()}
        self.assertIn(before,files[which])
        files[which]=files[which].replace(before,after,1)
        buf=io.BytesIO()
        with ZipFile(buf,'w',compression=ZIP_DEFLATED) as z:
            for p,v in files.items(): z.writestr(p,v)
        return buf.getvalue()
    def test_blueprint_mutation_rejected(self):
        bad=self._changed('blueprint_with_local_receipt.json', b'fv-ex2-review',b'fv-ex2-revieX')
        with self.assertRaisesRegex(ValueError,'SOURCE_DRIFT'):pack(bad)
    def test_manifest_mutation_rejected(self):
        bad=self._changed('source_manifest.json',b'75faa8a1',b'15faa8a1')
        with self.assertRaisesRegex(ValueError,'PIN_DRIFT'):pack(bad)

if __name__=='__main__': unittest.main(verbosity=2)
