"""Apollo R419 evidence custody and staging contract tests. No live modifications."""
from pathlib import Path
import hashlib, os, re, subprocess, unittest
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
EX2=ROOT.parent
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
NASA_TEXT=[
'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/',
]
RIGHTS='https://www.nasa.gov/nasa-brand-center/images-and-media/'
PHOTO_URLS=[
'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
'https://www.nasa.gov/image-detail/amf-s67-15717/',
'https://www.nasa.gov/image-detail/amf-s66-58038/',
'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
'https://www.nasa.gov/image-detail/amf-s67-21294/',
'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
]
PINS={EX2/'apollo-r411/staging-source-drawer.php':'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1',
EX2/'apollo-r418/staging-chronology-bridge.php':'2936eaac30cfe8a1c9016ca9298d98cb78ce9f7d',
ROOT/'assets/concordance.css':'42bcc4e606b035f0b52519fb97acb5d3fefd7352'}
def blob(path):
    b=path.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def render(mode='staging'):
    p=subprocess.run(['php',str(ROOT/'qa/render_fixture.php')],capture_output=True,text=True,check=True,env=dict(os.environ,FV_R419_MODE=mode))
    return BeautifulSoup(p.stdout,'html.parser')
class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=render();cls.root=cls.doc.select_one('[data-fv-r419-concordance]')
    def test_php_lint(self):
        for p in (ROOT/'staging-evidence-concordance.php',ROOT/'qa/render_fixture.php'):
            self.assertEqual(subprocess.run(['php','-l',str(p)],capture_output=True).returncode,0)
    def test_git_blob_custody(self):
        for p,sha in PINS.items():self.assertEqual(blob(p),sha,str(p))
    def test_live_source_count_and_order(self):
        self.assertIsNotNone(self.root)
        stages=self.root.select('.fv-r419__rail > li');cards=self.root.select('ol.fv-r419__grid > li')
        self.assertEqual((len(stages),len(cards)),(3,6))
        self.assertEqual([i['id'].split('-')[-1] for i in cards],['01','02','03','04','05','06'])
    def test_source_claim_evidence_separation(self):
        for i,card in enumerate(self.root.select('ol.fv-r419__grid > li')):
            urls=[a['href'] for a in card.select('a[href]')]
            self.assertEqual(len(urls),2)
            self.assertEqual(urls[1],PHOTO_URLS[i]);self.assertIn(urls[0],NASA_TEXT[:2])
            self.assertIn('What the image cannot establish:',card.get_text(' ',strip=True))
            self.assertIn('Source limitation:',card.get_text(' ',strip=True))
        for i,stage in enumerate(self.root.select('.fv-r419__rail > li')):
            self.assertEqual([a['href'] for a in stage.select('a[href]')],[NASA_TEXT[i]])
            self.assertIn('Evidence limitation:',stage.get_text(' ',strip=True))
    def test_2017_exhibit_not_historical_telemetry(self):
        cards=self.root.select('ol.fv-r419__grid > li')
        self.assertIn('18 October 1966',cards[2].get_text(' ',strip=True))
        for i in (3,5):self.assertIn('24 January 2017',cards[i].get_text(' ',strip=True))
        self.assertIn('28 January 1967',cards[4].get_text(' ',strip=True))
        self.assertIn('not conclusive identification',cards[4].get_text(' ',strip=True))
    def test_distinct_chronology_and_parseable_time(self):
        pairs=[(t['datetime'],t.get_text(' ',strip=True)) for t in self.root.select('time')]
        self.assertEqual(pairs,[('1967-01-27','27 January 1967'),('1967-12','December 1967'),('1968-02','February 1968'),('1968-03-14','14 March 1968')])
        stage=self.root.select('.fv-r419__rail > li')
        self.assertIn('102 deliberate ignitions',stage[1].get_text(' ',strip=True))
        self.assertIn('could not conclusively identify',stage[0].get_text(' ',strip=True))
    def test_no_invented_geo_media_or_marketing(self):
        for s in ('script','iframe','img','video','audio','canvas','svg','map','form','input','picture'):
            self.assertFalse(self.root.select(s),s)
        self.assertNotIn('Related evidence 06',str(self.root))
        links=[a['href'] for a in self.root.select('a[href]')]
        self.assertTrue(all(l in NASA_TEXT+PHOTO_URLS+[ARTICLE,RIGHTS] or l.startswith('#fv-r419-1-') for l in links))
        self.assertFalse(any('utm_' in u or 'payhip' in u for u in links))
    def test_one_free_next_action(self):
        self.assertEqual(len(self.root.select('a[href="'+ARTICLE+'"]')),1)
        self.assertEqual(len(self.root.select('.fv-r419__next')),1)
    def test_native_no_javascript_disclosure(self):
        self.assertEqual(len(self.root.select('details > summary')),6)
        for card in self.root.select('.fv-r419__card'):
            self.assertTrue(card.select_one('details > summary'))
            self.assertTrue(card.select_one('.fv-r419__boundary'))
    def test_nav_fragments_are_real_unique_targets(self):
        ids=[e['id'] for e in self.root.select('[id]')]
        self.assertEqual(len(ids),len(set(ids)))
        for a in self.root.select('nav a'):
            self.assertTrue(self.root.select_one('[id="'+a['href'][1:]+'"]'))
    def test_unauthorized_fallback(self):
        for mode in ('production','archive','wrong-page','disabled'):
            d=render(mode)
            self.assertFalse(d.select('[data-fv-r419-concordance]'))
            self.assertEqual(len(d.select('a[href="'+ARTICLE+'"]')),1)
    def test_duplicate_instance_ids_and_ctas(self):
        d=render('double');self.assertEqual(len(d.select('[data-fv-r419-concordance]')),2)
        ids=[e['id'] for e in d.select('[id]')]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len(d.select('a[href="'+ARTICLE+'"]')),2)
    def test_css_integrity_mutation_stays_off(self):
        p=ROOT/'assets/concordance.css';raw=p.read_bytes()
        try:
            p.write_bytes(raw+b'\n/* injected */')
            self.assertFalse(render().select('[data-fv-r419-concordance]'))
        finally:p.write_bytes(raw)
        self.assertEqual(blob(p),PINS[p])
    def test_source_integrity_mutation_stays_off(self):
        p=EX2/'apollo-r418/staging-chronology-bridge.php';raw=p.read_bytes()
        try:
            p.write_bytes(raw+b'\n// injected')
            self.assertFalse(render().select('[data-fv-r419-concordance]'))
        finally:p.write_bytes(raw)
        self.assertEqual(blob(p),PINS[p])
if __name__=='__main__':unittest.main(verbosity=2)
