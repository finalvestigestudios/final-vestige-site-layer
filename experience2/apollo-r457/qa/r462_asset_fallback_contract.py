#!/usr/bin/env python3
"""R462 source-controlled minimal dependency-loss acceptance gate (read-only)."""
from contextlib import contextmanager
from pathlib import Path
import hashlib
import json
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
CSS=ROOT/'assets/gallery.css'
JS=ROOT/'assets/gallery.js'

def render():
    cmd=f'require {json.dumps(str(ROOT/"apollo_rights_gallery.php"))}; echo fv457_render();'
    return subprocess.check_output(['php','-r',cmd],text=True)

@contextmanager
def missing(*paths):
    moves=[]
    try:
        for p in paths:
            moved=p.with_name(p.name+'.r462-test-missing')
            if moved.exists():raise RuntimeError('stale test residue')
            p.rename(moved);moves.append((p,moved))
        yield
    finally:
        for p,moved in reversed(moves):moved.rename(p)

class AssetDegradation(unittest.TestCase):
    def assert_six(self,html):
        self.assertEqual(html.count('data-fv457-card='),6)
        self.assertEqual(html.count('class="fv457__print-custody"'),6)
        self.assertIn('Source acceptance HOLD',html)
        self.assertIn('not accepted provenance or commercial permissions',html)
        self.assertEqual(html.count('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'),1)
        self.assertNotIn('<img',html.lower())

    def test_full_markup_with_assets(self):
        html=render();self.assert_six(html)
        self.assertIn('<style>',html);self.assertIn('<script>',html)

    def test_missing_javascript_preserves_styled_evidence(self):
        with missing(JS):
            html=render();self.assert_six(html)
            self.assertIn('<style>',html);self.assertNotIn('<script>',html)

    def test_missing_stylesheet_preserves_unstyled_static_evidence(self):
        with missing(CSS):
            html=render();self.assert_six(html)
            self.assertNotIn('<style>',html);self.assertNotIn('<script>',html)

    def test_both_absent_preserves_evidence(self):
        with missing(CSS,JS):
            html=render();self.assert_six(html)
            self.assertNotIn('<style>',html);self.assertNotIn('<script>',html)

    def test_present_but_corrupted_asset_fails_closed(self):
        for path in (CSS,JS):
            original=path.read_bytes()
            try:
                path.write_bytes(original+b'\n/* test modification */')
                html=render()
                self.assertIn('temporarily unavailable',html)
                self.assertNotIn('data-fv457-card=',html)
            finally:path.write_bytes(original)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),hashlib.sha256(original).hexdigest())

    def test_scoped_to_staging_shortcode(self):
        php=(ROOT/'apollo_rights_gallery.php').read_text()
        self.assertIn("wp_get_environment_type()!=='staging'",php)
        self.assertIn('FV_R457_STAGING_PAGE_ID',php)
        self.assertIn("if(!$cssPresent)return $out;",php)

if __name__=='__main__':unittest.main(verbosity=2)
