"""Adversarial source-attestation tests for derived, never-live chapter trail fix."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from apply_ex2_chapter_trail_fix import derive,digest,PHP_PATH,PARENT_ZIP,PARENT_PHP

class PatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).parent
        cls.css=cls.root/'chapter-trail-focus-visibility.css'
        cls.js=cls.root/'chapter-trail-focus-visibility.js'
        # Parent ZIP is provided from protected PR #1469 evidence; not committed.
        import os
        cls.parent=Path(os.environ['FV_EX2_PROTECTED_PARENT_ZIP'])

    def test_parent_attestation(self):
        self.assertEqual(digest(self.parent.read_bytes()),PARENT_ZIP)

    def test_derivation_invariants(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'derived.zip'
            r=derive(self.parent,p,self.css,self.js)
            self.assertNotEqual(r['derived_php_sha256'],PARENT_PHP)
            self.assertFalse(r['native_wordpress_tested'])
            self.assertFalse(r['release_authorized'])
            with ZipFile(p) as z:
                manifest=json.loads(z.read('SOURCE_CUSTODY.json'))
                php=z.read(PHP_PATH)
                self.assertEqual(digest(php),manifest['files_sha256'][PHP_PATH])
                self.assertTrue(manifest['requires_fresh_exact_source_acceptance'])
                self.assertEqual(php.count(b'class="fv-margin-strip__item"'),72)
                self.assertEqual(php.count(b'href="https://finalvestige.com/focus/"'),5)
                self.assertIn(b'ARCHIVAL REFERENCE',php)

    def test_drift_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            changed=Path(t)/'tampered.zip'
            changed.write_bytes(self.parent.read_bytes()[:-1]+b'0')
            with self.assertRaisesRegex(ValueError,'PROTECTED_PARENT_SHA_MISMATCH'):
                derive(changed,Path(t)/'out.zip',self.css,self.js)

    def test_unreviewed_css_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            wrong=Path(t)/'wrong.css'
            wrong.write_text('body{color:black}')
            with self.assertRaisesRegex(ValueError,'CSS_PATCH_NOT_REVIEWED'):
                derive(self.parent,Path(t)/'out.zip',wrong,self.js)

    def test_unreviewed_js_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            wrong=Path(t)/'wrong.js'
            wrong.write_text('console.log("hello")')
            with self.assertRaisesRegex(ValueError,'JS_PATCH_NOT_REVIEWED'):
                derive(self.parent,Path(t)/'out.zip',self.css,wrong)

if __name__=='__main__':
    unittest.main()
