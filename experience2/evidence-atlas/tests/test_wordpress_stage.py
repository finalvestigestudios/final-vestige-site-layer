"""R40: tests the actual R39 source-custody rendered shortcode and PHP adapter."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys
from html.parser import HTMLParser
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import build_wordpress_stage as stage

HERE = Path(__file__).resolve().parents[1]
PROBE = HERE / 'tests/wordpress_shortcode_probe.php'

class Tags(HTMLParser):
    def __init__(self): super().__init__();self.tags=[]
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))

class WordPressStage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.dest=Path(cls.tmp.name)
        cls.manifest=stage.build(cls.dest)
        cls.plugin=cls.dest/'fv-ex2-evidence-atlas'
        cls.html=(cls.plugin/'templates/atlas-fragment.html').read_text()
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def probe(self,singular=True):
        env={**os.environ, 'FV_SINGULAR':'1' if singular else '0'}
        result=subprocess.run(['php',str(PROBE),str(self.plugin/'final-vestige-ex2-evidence-atlas.php')],
             capture_output=True,text=True,check=True,env=env)
        return json.loads(result.stdout)
    def test_exact_custody_refused_on_change(self):
        self.assertEqual(self.manifest['source_crosswalk_blob'],stage.build_atlas.EXPECTED_BLOB)
        self.assertEqual(self.manifest['media_rights_unreviewed'],6)
    def test_actual_six_records(self):
        parser=Tags();parser.feed(self.html)
        a=[attrs for tag,attrs in parser.tags if tag=='article' and 'data-fva-record' in attrs]
        self.assertEqual([x['data-fva-id'] for x in a],list(stage.build_atlas.IDS))
        self.assertEqual(self.html.count('Individual review required. No photograph is reproduced here.'),6)
    def test_wordpress_fragment_is_not_document_nested_main_or_script(self):
        parser=Tags();parser.feed(self.html)
        self.assertNotIn('main',[t for t,_ in parser.tags]);self.assertNotIn('script',[t for t,_ in parser.tags])
        self.assertNotIn('style',[t for t,_ in parser.tags]);self.assertNotIn('img',[t for t,_ in parser.tags])
        self.assertNotIn('canvas',[t for t,_ in parser.tags]);self.assertIn('<section class="fva"',self.html)
    def test_accessibility_references_unique(self):
        parser=Tags();parser.feed(self.html)
        ids=[a['id'] for _,a in parser.tags if 'id' in a]
        self.assertEqual(len(ids),len(set(ids)))
        for _,a in parser.tags:
            for attr in ('for','aria-labelledby','aria-controls'):
                if attr in a:
                    self.assertTrue(all(s in ids for s in a[attr].split()),(attr,a[attr]))
    def test_php_singular_asset_hook(self):
        p=self.probe();self.assertTrue(p['shortcode_registered'])
        self.assertEqual(list(p['assets']['styles']),['fv-ex2-evidence-atlas'])
        self.assertEqual(list(p['assets']['scripts']),['fv-ex2-evidence-atlas'])
        self.assertTrue(p['assets']['scripts']['fv-ex2-evidence-atlas'][2]);self.assertIn('data-fva-atlas',p['markup'])
    def test_non_singular_does_not_enqueue(self):
        self.assertFalse(self.probe(False)['assets'])
    def test_second_shortcode_does_not_duplicate_ids(self):
        p=self.probe();self.assertEqual(p['markup'].count('data-fva-record '),6)
        self.assertIn('already on this page',p['duplicate'])
        self.assertNotIn('data-fva-record',p['duplicate'])
    def test_unmodified_upstream_atlas(self):
        self.assertEqual((self.plugin/'assets/atlas.js').read_bytes(),(HERE/'atlas.js').read_bytes())
        self.assertEqual((self.plugin/'assets/atlas.css').read_bytes(),(HERE/'atlas.css').read_bytes())
    def test_deterministic_build_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest=stage.build(Path(temp))
            self.assertEqual(manifest,self.manifest)
            self.assertEqual((Path(temp)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_bytes(),
                (self.plugin/'templates/atlas-fragment.html').read_bytes())
    def test_missing_compiled_template_fallback(self):
        source=self.plugin/'templates/atlas-fragment.html'
        source.rename(source.with_suffix('.held'))
        try:self.assertIn('Evidence Atlas is unavailable',self.probe()['markup'])
        finally:source.with_suffix('.held').rename(source)
    def test_no_geo_or_unreviewed_image(self):
        for token in ('<img','<picture','data-lat=','data-lng=','<iframe','<canvas','<svg'):
            self.assertNotIn(token,self.html)
        self.assertIn('Why no map?',self.html)

if __name__=='__main__':unittest.main()
