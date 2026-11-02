"""R45 static contract tests: bidirectional custody permalinks, no new asserted facts."""
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
    def __init__(self):
        super().__init__(); self.tags=[]
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))

class CitationNavigationR45(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.custody=build_atlas.validate_custody()
        cls.html=build_atlas.make_html(cls.custody,(HERE/'atlas.css').read_text(),(HERE/'atlas.js').read_text())
        p=Tags();p.feed(cls.html);cls.tags=p.tags
    def test_exact_six_record_and_citation_pairs(self):
        cards=[attrs for tag,attrs in self.tags if 'data-fva-record' in attrs]
        cite=[attrs for tag,attrs in self.tags if 'data-fva-cite-id' in attrs]
        self.assertEqual(len(cards),6)
        self.assertEqual(len(cite),6)
        for card,row in zip(cards,cite):
            self.assertEqual(card['data-fva-id'],row['data-fva-cite-id'])
            self.assertEqual(row['id'],'fva-citation-'+card['data-fva-id'])
    def test_bidirectional_anchors_and_unambiguous_targets(self):
        ids=[attrs['id'] for _,attrs in self.tags if 'id' in attrs]
        self.assertEqual(len(ids),len(set(ids)))
        to=[a for _,a in self.tags if 'data-fva-to-citation' in a]
        back=[a for _,a in self.tags if 'data-fva-back-record' in a]
        self.assertEqual(len(to),6)
        self.assertEqual(len(back),6)
        for n in range(1,7):
            self.assertEqual(to[n-1]['href'],f'#fva-citation-{n:02d}')
            self.assertEqual(back[n-1]['href'],f'#fva-record-{n:02d}')
        for anchor in to+back:
            self.assertIn(anchor['href'][1:],ids)
    def test_new_tab_notice_and_no_imagery(self):
        self.assertEqual(self.html.count('Open original NASA record (opens in new tab)'),6)
        for forbidden in ['<img','<picture','<iframe','<canvas','data-lat=','data-lng=','<script src=']:
            self.assertNotIn(forbidden,self.html)
        self.assertEqual(self.html.count('image reuse: individual review required.'),6)
        self.assertIn('photograph date January 1967',self.html)
        self.assertNotIn('January 27, 1967',self.html)
    def test_compiled_wordpress_integrity_and_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest=build_wordpress_stage.build(Path(tmp))
            package=Path(tmp)/'fv-ex2-evidence-atlas'
            fragment=(package/'templates/atlas-fragment.html').read_bytes()
            php=(package/'final-vestige-ex2-evidence-atlas.php').read_text()
            self.assertIn(hashlib.sha256(fragment).hexdigest(),php)
            self.assertIn('0.0.56-staging',php)
            self.assertEqual(manifest['schema'],'fv.ex2.apollo.wp-stage.r49.v1')
            self.assertEqual(fragment.count(b'data-fva-to-citation'),6)
            self.assertEqual(fragment.count(b'data-fva-back-record'),6)
            self.assertNotIn(b'<script',fragment)
    def test_js_adversarial_recovery_contract(self):
        js=(HERE/'atlas.js').read_text()
        self.assertIn('backLinks[i].closest',js)
        self.assertIn('jumps.push(...backLinks)',js)
        self.assertIn('if(!apply())return',js)
        self.assertIn('controls.hidden=true',js)

if __name__=='__main__':unittest.main()
