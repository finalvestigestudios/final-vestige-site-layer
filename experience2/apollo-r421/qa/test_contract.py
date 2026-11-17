#!/usr/bin/env python3
"""Tests the real staging-only PHP component and its exact reviewed upstream sources."""
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT.parent
ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def fixture(mode='staging', folder=ROOT):
    e = dict(os.environ, FV_R421_MODE=mode)
    return subprocess.run(['php', str(folder/'qa/render_fixture.php')], capture_output=True, text=True, env=e, check=True).stdout

class Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = fixture()
        cls.soup = BeautifulSoup(cls.html, 'html.parser')
        cls.block = cls.soup.select_one('[data-fv-r421-receipts]')

    def test_staging_on_approved_page_only(self):
        self.assertIsNotNone(self.block)
        for mode in ('production', 'wrong-page', 'archive', 'disabled'):
            self.assertNotIn('data-fv-r421-receipts', fixture(mode))
            self.assertIn(ARTICLE, fixture(mode))

    def test_only_three_source_receipts(self):
        self.assertEqual(3, len(self.block.select('li.fv-r421__card')))
        self.assertEqual(3, len(self.block.select('details')))

    def test_full_text_is_visible_without_javascript(self):
        self.assertEqual(3, len(self.block.select('pre[tabindex="0"]')))
        for p in self.block.select('pre'):
            self.assertIn('Evidence limitation:', p.get_text())
            self.assertIn('Related photograph date:', p.get_text())
            self.assertIn('NASA historical publication:', p.get_text())
            self.assertIn('NASA image catalogue', p.get_text())

    def test_no_unlicensed_embedded_media(self):
        self.assertEqual([], self.block.select('img,video,audio,iframe,svg,canvas'))

    def test_just_one_relevant_article_cta(self):
        self.assertEqual(1, len(self.block.select('a.fv-r421__next')))
        self.assertEqual(ARTICLE, self.block.select_one('a.fv-r421__next')['href'])

    def test_no_commerce_scripts_forms_or_map(self):
        self.assertEqual([], self.block.select('form,script,input,textarea,[data-price],iframe'))
        self.assertNotIn('utm_', self.html)
        self.assertNotIn('payhip', self.html.lower())

    def test_all_external_reference_links_are_nasa(self):
        refs = self.block.select('.fv-r421__sources a')
        self.assertEqual(6,len(refs))
        self.assertTrue(all(a['href'].startswith('https://www.nasa.gov/') for a in refs))
        self.assertEqual(3, len([a for a in refs if '/image-detail/' in a['href']]))

    def test_copy_buttons_are_no_js_hidden(self):
        self.assertEqual(3, len(self.block.select('button[hidden][data-fv-r421-copy]')))
        self.assertEqual(3, len(self.block.select('[aria-live="polite"]')))

    def test_no_duplicate_element_ids(self):
        ids = [el['id'] for el in self.soup.select('[id]')]
        self.assertEqual(len(ids), len(set(ids)))
        double=BeautifulSoup(fixture('double'), 'html.parser')
        ids=[el['id'] for el in double.select('[id]')]
        self.assertEqual(len(ids), len(set(ids)))

    def test_pinned_dependency_receipts(self):
        php = (ROOT/'staging-source-receipts.php').read_text()
        for path in ('../apollo-r420/staging-educator-source-lab.php', 'assets/source-receipts.css', 'assets/source-receipts.js'):
            content = (ROOT/path).read_bytes()
            blob=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
            self.assertIn("'"+path+"' => '"+blob+"'",php)

    def test_tampered_assets_and_upstream_fail_open(self):
        with tempfile.TemporaryDirectory() as scratch:
            home=Path(scratch)
            for d in ('apollo-r411','apollo-r415','apollo-r418','apollo-r419','apollo-r420','apollo-r421'):
                shutil.copytree(EX/d,home/d)
            for rel in ('apollo-r420/staging-educator-source-lab.php','apollo-r421/assets/source-receipts.css', 'apollo-r421/assets/source-receipts.js'):
                p=home/rel
                old=p.read_bytes();p.write_bytes(old+b'\n/* adversarial change */')
                res=fixture(folder=home/'apollo-r421')
                self.assertNotIn('data-fv-r421-receipts',res)
                self.assertIn(ARTICLE,res)
                p.write_bytes(old)

    def test_pinned_ancestors_unmodified(self):
        deps={'apollo-r411/staging-source-drawer.php':'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1',
              'apollo-r415/staging-journey.php':'18d20114af2a854bc06f1b265026860f6ccee30c',
              'apollo-r418/staging-chronology-bridge.php':'2936eaac30cfe8a1c9016ca9298d98cb78ce9f7d',
              'apollo-r419/staging-evidence-concordance.php':'0d300360c6614be9c189ef5d555e1f497c844582',
              'apollo-r420/staging-educator-source-lab.php':'e3f1c9897e453512569a0fdd937c01e3b6e7f783'}
        for rel,sha in deps.items():
            raw=(EX/rel).read_bytes()
            self.assertEqual(sha,hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())

    def test_unambiguous_1967_vs_2017_provenance(self):
        self.assertIn('24 January 2017',self.html)
        self.assertIn('1967',self.html)
        self.assertIn('102 deliberate ignitions',self.html)
        self.assertIn('or a paid educational product',self.html)

if __name__=='__main__':unittest.main(verbosity=2)
