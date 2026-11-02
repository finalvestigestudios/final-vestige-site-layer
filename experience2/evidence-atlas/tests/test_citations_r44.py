"""R44: source-custody citation register, deterministic WP template and no media."""
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_atlas
import build_wordpress_stage

ROOT=Path(__file__).resolve().parents[1]

class R44CitationRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.custody=build_atlas.validate_custody()
        cls.html=build_atlas.make_html(cls.custody,(ROOT/'atlas.css').read_text(),(ROOT/'atlas.js').read_text())
    def test_six_citations_with_exact_provenance(self):
        self.assertEqual(self.html.count('data-fva-cite-id='),6)
        self.assertEqual(self.html.count('data-fva-citation-text>'),6)
        for r in self.custody['records']:
            span=re.search(fr'<li data-fva-cite-id="{r["id"]}"[^>]*>(.*?)</li>',self.html,re.S)
            self.assertIsNotNone(span)
            self.assertIn(r['catalog'],span.group(1))
            self.assertIn(r['photo_url'],span.group(1))
            self.assertIn(r['date_label'],span.group(1))
            self.assertIn('image reuse: individual review required.',span.group(1))
    def test_month_only_not_inferred(self):
        self.assertIn('photograph date January 1967',self.html)
        self.assertNotIn('January 27, 1967',self.html)
    def test_bibliography_is_static_and_navigable(self):
        self.assertIn('aria-labelledby="fva-citations-title"',self.html)
        self.assertIn('role="status" aria-live="polite"',self.html)
        self.assertEqual(self.html.count('data-fva-copy hidden'),6)
        self.assertIn('The register remains complete when filters are applied',self.html)
    def test_no_images_or_geopins(self):
        for tag in ('<img','<picture','<iframe','<canvas','data-lat=','data-lng='):
            self.assertNotIn(tag,self.html)
    def test_wordpress_compiled_fragment_is_hash_pinned(self):
        with tempfile.TemporaryDirectory() as t:
            build_wordpress_stage.build(Path(t))
            package=Path(t)/'fv-ex2-evidence-atlas'
            fragment=(package/'templates/atlas-fragment.html').read_bytes()
            php=(package/'final-vestige-ex2-evidence-atlas.php').read_text()
            self.assertIn(hashlib.sha256(fragment).hexdigest(),php)
            self.assertIn('0.0.57-staging',php)
            self.assertEqual(fragment.count(b'data-fva-copy hidden'),6)

if __name__=='__main__':unittest.main()
