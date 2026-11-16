"""Read-only R417 source, rights, chronology and fail-open acceptance. Requires PHP and bs4."""
from pathlib import Path
import hashlib, os, subprocess, unittest
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
EX2=ROOT.parent
FIXTURE=ROOT/'qa/render_fixture.php'
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'

def render(mode='staging'):
    output=subprocess.run(['php',str(FIXTURE)],env=dict(os.environ,FV_TEST_MODE=mode),
                          capture_output=True,text=True,check=True).stdout
    return BeautifulSoup(output,'html.parser')

class R417Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=render()
        cls.component=cls.html.select_one('[data-fv-r417-provenance]')

    def test_php_syntax(self):
        for p in (ROOT/'staging-provenance-guide.php',FIXTURE):
            self.assertIn('No syntax errors',subprocess.run(['php','-l',str(p)],capture_output=True,text=True,check=True).stdout)

    def test_custody_pins(self):
        expected={'apollo-r411/staging-source-drawer.php':'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1',
                  'apollo-r415/staging-journey.php':'18d20114af2a854bc06f1b265026860f6ccee30c',
                  'apollo-r417/assets/provenance.css':'921f50a471fad20ee3562e60333cba8f6c84a74d'}
        for file,sha in expected.items():
            data=(EX2/file).read_bytes()
            self.assertEqual(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),sha,file)

    def test_six_distinct_historical_roles(self):
        self.assertIsNotNone(self.component)
        cards=self.component.select('ol.fv-r417__list > li')
        self.assertEqual(len(cards),6)
        for text in ('January 1967','3 January 1967','18 October 1966','24 January 2017','28 January 1967'):
            self.assertIn(text,self.component.get_text(' ',strip=True))
        self.assertIn('not telemetry',cards[2].get_text(' ',strip=True).lower())
        self.assertIn('2017 museum',cards[3].get_text(' ',strip=True).lower())
        self.assertIn('does not establish',cards[4].get_text(' ',strip=True).lower())

    def test_external_record_vs_report(self):
        for card in self.component.select('.fv-r417__item'):
            anchors=[a['href'] for a in card.select('a')]
            self.assertEqual(len(anchors),2)
            self.assertTrue(anchors[0].startswith('https://www.nasa.gov/image-detail/'))
            self.assertTrue(anchors[1].startswith('https://www.nasa.gov/'))
        self.assertEqual(len(self.component.select('a[href="'+BOARD+'"]')),5)

    def test_evidence_limit_visible_without_javascript(self):
        self.assertEqual(len(self.component.select('.fv-r417__limit')),6)
        self.assertEqual(len(self.component.select('details > summary')),6)
        self.assertEqual(len(self.component.select('.fv-r417__type')),6)

    def test_no_unapproved_commerce_or_media(self):
        for selector in ('script','img','video','iframe','svg','map','form','input','canvas','picture','audio'):
            self.assertFalse(self.component.select(selector),selector)
        self.assertEqual(len(self.component.select('a[href="'+ARTICLE+'"]')),1)
        self.assertIn('NASA does not endorse',self.component.get_text(' ',strip=True))
        self.assertIn('does not license',self.component.get_text(' ',strip=True))

    def test_wrong_context_fails_to_existing_free_article(self):
        for mode in ('production','wrong-page','disabled','archive'):
            soup=render(mode)
            self.assertIsNone(soup.select_one('[data-fv-r417-provenance]'))
            self.assertEqual(len(soup.select('a[href="'+ARTICLE+'"]')),1)

    def test_multiple_instances_no_duplicate_ids(self):
        soup=render('double')
        self.assertEqual(len(soup.select('[data-fv-r417-provenance]')),2)
        ids=[x['id'] for x in soup.select('[id]')]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len(soup.select('a[href="'+ARTICLE+'"]')),2)

    def test_malicious_supplied_record_rejected(self):
        php='define("ABSPATH",__DIR__); require '+repr(str(ROOT/'staging-provenance-guide.php'))+'; require '+repr(str(EX2/'apollo-r411/staging-source-drawer.php'))+'; $r=fv_r411_catalog(); $r[0][3]="https://www.nasa.gov.evil.example/"; echo fv_r417_markup(1,$r);'
        actual=subprocess.run(['php','-r',php],capture_output=True,text=True,check=True).stdout
        self.assertNotIn('evil.example',actual)
        self.assertIn('Source provenance guide unavailable',actual)

if __name__=='__main__':unittest.main(verbosity=2)
