"""R46 custody-first pair inspector: source-integrity and no-JS contracts."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_atlas
import build_wordpress_stage

class Tags(HTMLParser):
    def __init__(self): super().__init__(); self.tags=[]
    def handle_starttag(self,tag,attrs): self.tags.append((tag,dict(attrs)))

class PairInspectorR46(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=build_atlas.make_html(build_atlas.validate_custody(),
            (HERE/'atlas.css').read_text(),(HERE/'atlas.js').read_text())
        t=Tags();t.feed(cls.html);cls.tags=t.tags
    def test_exactly_six_disabled_by_default_selection_buttons(self):
        controls=[attrs for tag,attrs in self.tags if tag=='button' and 'data-fva-select' in attrs]
        self.assertEqual([a['data-fva-select'] for a in controls],list(build_atlas.IDS))
        self.assertTrue(all('hidden' in a and a['aria-pressed']=='false' for a in controls))
    def test_inspector_is_optional_no_js_has_six_accessible_sources(self):
        sections=[a for _,a in self.tags if 'data-fva-compare' in a]
        self.assertEqual(len(sections),1)
        self.assertIn('hidden',sections[0])
        self.assertEqual(len([a for _,a in self.tags if 'data-fva-record' in a]),6)
        self.assertEqual(len([a for _,a in self.tags if 'data-fva-cite-id' in a]),6)
        self.assertEqual(len([a for _,a in self.tags if 'data-fva-compare-slot' in a]),2)
        self.assertIn('does not establish causation, proximity',self.html)
    def test_no_new_fact_sources_images_or_geo(self):
        self.assertEqual(self.html.count('Individual review required. No photograph is reproduced here.'),6)
        for forbidden in ('<img','<picture','<iframe','<canvas','data-lat=','data-lng='):
            self.assertNotIn(forbidden,self.html)
        for url in build_atlas.EXPECTED_URLS.values(): self.assertIn(url,self.html)
        self.assertIn('January 1967; exact day not asserted',self.html)
    def test_fail_open_no_html_injection_js(self):
        script=(HERE/'atlas.js').read_text()
        self.assertIn('const onSelect=event=>',script)
        self.assertIn('if(!valid())throw',script)
        self.assertIn('onCompareJump',script)
        self.assertIn('compare.hidden=true',script)
        self.assertIn('slot.replaceChildren()',script)
        self.assertNotIn('.innerHTML',script)
        self.assertNotIn('fetch(',script)
    def test_print_and_mobile_contracts(self):
        css=(HERE/'atlas.css').read_text()
        self.assertIn('@media(max-width:700px){.fva-compare__pair',css)
        self.assertIn('@media print{.fva-compare,.fva-card__compare{display:none!important}}',css)
        self.assertIn('min-height:44px',css)
    def test_exact_wordpress_template_pin(self):
        with tempfile.TemporaryDirectory() as t:
            manifest=build_wordpress_stage.build(Path(t))
            plugin=Path(t)/'fv-ex2-evidence-atlas'
            markup=(plugin/'templates/atlas-fragment.html').read_bytes()
            php=(plugin/'final-vestige-ex2-evidence-atlas.php').read_text()
            self.assertIn(hashlib.sha256(markup).hexdigest(),php)
            self.assertIn('0.0.46-staging',php)
            self.assertEqual(manifest['schema'],'fv.ex2.apollo.wp-stage.r46.v1')
            self.assertEqual(markup.count(b'data-fva-select='),6)
            self.assertNotIn(b'<script',markup)

if __name__=='__main__':unittest.main()
