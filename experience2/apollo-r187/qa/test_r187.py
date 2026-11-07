#!/usr/bin/env python3
"""Regression tests: byte custody, source isolation and PHP WP-function contract."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_r187 import PIN, NEEDLE, REPLACEMENT, SCAN, patch, sha


class R187Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = (ROOT.parent/'apollo-r186/dist/fv-ex2-apollo-r186.php').read_bytes()
        cls.new = (ROOT/'dist/fv-ex2-apollo-r187.php').read_bytes()
        cls.html = (ROOT/'dist/templates/atlas-fragment.html').read_bytes()
        cls.css = (ROOT/'dist/assets/atlas-scoped.css').read_bytes()

    def test_parent_php_digest(self):
        self.assertEqual(sha(self.old), PIN['php'])

    def test_parent_evidence_digest(self):
        self.assertEqual(sha(self.html), PIN['html'])
        self.assertEqual(sha(self.css), PIN['css'])

    def test_only_intentional_php_patch(self):
        self.assertEqual(self.new, patch(self.old))
        self.assertEqual(self.new.count(b'function fv_ex2_r187_has_target('), 1)
        self.assertIn(b'function fv_ex2_r187_preflight()', self.new)

    def test_unexpected_source_rejected(self):
        with self.assertRaises(ValueError): patch(self.old.replace(NEEDLE.encode(), b'corrupt'))

    def test_same_original_destination_and_rights(self):
        self.assertEqual(self.old.count(b'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'),self.new.count(b'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'))
        self.assertIn(b'Read the original investigation', self.new)
        self.assertNotIn(b'aw in',self.new)
        self.assertNotIn(b'utm_',self.new)

    def test_php_lint(self):
        proc = subprocess.run(['php','-l',str(ROOT/'dist/fv-ex2-apollo-r187.php')], capture_output=True,text=True)
        self.assertEqual(proc.returncode,0,proc.stderr)

    def test_php_function_harness(self):
        p = subprocess.run(['php', str(ROOT/'qa/wp_function_harness.php')],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        obj=json.loads(p.stdout)
        self.assertGreaterEqual(obj['passed'],17)
        self.assertEqual(obj['failed'],0)
        self.assertIn('NOT_INSTALLED_WORDPRESS',obj['environment'])

    def test_rendered_php_html_exact(self):
        p=subprocess.run(['php',str(ROOT/'qa/wp_function_harness.php'),'--html'],capture_output=True,check=True)
        self.assertEqual(sha(p.stdout), PIN['html'])

    def test_manifest(self):
        m=json.loads((ROOT/'dist/manifest.json').read_text())
        self.assertEqual(m['r187_php_sha256'],sha(self.new))
        self.assertFalse(m['axe_executed'])
        self.assertFalse(m['installed_wordpress_tested'])
        self.assertFalse(m['paid_orders_verified'])

    def test_no_merchant_or_remote_js(self):
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(self.html,'html.parser')
        self.assertEqual(len(soup.select('script,img,iframe,form')),0)
        self.assertEqual(len(soup.select('a.cta')),1)
        self.assertEqual(len(soup.select('.rail li')),4)
        self.assertEqual(len(soup.select('.plate')),4)
        self.assertEqual(len(soup.select('.source-card')),4)
        self.assertEqual(len(soup.select('details')),8)
        ids=[x['id'] for x in soup.select('[id]')]
        self.assertEqual(len(ids),len(set(ids)))
        for item in soup.select('[aria-labelledby]'):
            for ref in item['aria-labelledby'].split():
                self.assertIn(ref, ids)

if __name__=='__main__': unittest.main()
