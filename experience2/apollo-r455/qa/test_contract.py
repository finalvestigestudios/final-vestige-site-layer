#!/usr/bin/env python3
"""Source-custody, release-guard, commercial trust-boundary and corruption tests."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'apollo_crosswalk.php'


def php(code, cwd=None):
    r = subprocess.run(['php', '-r', code], text=True, capture_output=True, cwd=cwd, timeout=8)
    if r.returncode:
        raise AssertionError('PHP failure: ' + r.stderr)
    return r.stdout


def render(source=SRC):
    return php(f"require '{str(source)}'; echo fv455_render();")


class Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = render()
        cls.soup = BeautifulSoup(cls.html, 'html.parser')
        cls.section = cls.soup.select_one('section.fv455')
        cls.cards = cls.soup.select('.fv455__plate')

    def test_php_lint(self):
        r = subprocess.run(['php', '-l', str(SRC)], text=True, capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_semantic_staging_only(self):
        self.assertIsNotNone(self.section)
        self.assertEqual(self.section.get('aria-labelledby'), self.section.find('h2')['id'])
        self.assertIn('wp_get_environment_type()', SRC.read_text())
        self.assertIn("FV_R455_ENABLE_STAGING", SRC.read_text())

    def test_exact_four_cards_with_distinct_source_type(self):
        self.assertEqual(len(self.cards), 4)
        self.assertEqual([x['data-fv455-kind'] for x in self.cards], ['context', 'investigation', 'later', 'later'])

    def test_ordered_distinct_dates(self):
        dates = [x.find('time')['datetime'] for x in self.cards]
        self.assertEqual(dates, sorted(dates))
        self.assertEqual(dates, ['1966-10-18', '1967-01-27', '2017-01-27', '2018-02-14'])

    def test_supported_vs_not_established(self):
        for c in self.cards:
            self.assertEqual(len(c.select('[data-fv455-supported]')),1)
            self.assertEqual(len(c.select('[data-fv455-limit]')),1)
            self.assertIn('does not establish', c.get_text(' ',strip=True).lower())

    def test_record_vs_publication_date(self):
        body = self.section.get_text(' ',strip=True)
        self.assertIn('NOT the Board report publication date',body)
        self.assertIn('Retrospective publication date',body)
        self.assertIn('museum display',body)

    def test_real_official_source_links(self):
        links = [a['href'] for c in self.cards for a in c.select('a[href]')]
        self.assertEqual(len(links),4)
        for url in links:
            p=urlsplit(url)
            self.assertEqual((p.scheme,p.netloc),('https','www.nasa.gov'))
            self.assertFalse(p.query or p.fragment)

    def test_one_contextual_free_article_cta(self):
        ctas = self.section.select('.fv455__cta a[href]')
        self.assertEqual(len(ctas),1)
        self.assertEqual(ctas[0]['href'],'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/')

    def test_no_remote_assets_tracking_or_paid_link(self):
        self.assertFalse(self.section.select('img,iframe,video,form,object,embed,canvas'))
        self.assertNotIn('payhip.com',self.html.lower())
        self.assertNotIn('utm_',self.html)
        self.assertFalse(any(s.has_attr('src') for s in self.soup.find_all('script')))
        self.assertFalse(any(s.has_attr('href') for s in self.soup.find_all('link')))

    def test_non_js_all_records_accessible(self):
        self.assertFalse(any(c.has_attr('hidden') for c in self.cards))
        self.assertTrue(all(c.find('details') and c.find('summary') for c in self.cards))
        self.assertIn('Source-check challenge',self.html)

    def test_namespaced_no_global_collisions(self):
        self.assertIn('fv455-',self.html)
        self.assertFalse(re.search(r'<(?:div|section)[^>]*id="(?:app|root|content)"',self.html))

    def test_multi_instance_ids_unique(self):
        out = php(f"require '{SRC}'; echo fv455_render();echo fv455_render();")
        soup=BeautifulSoup(out,'html.parser')
        ids=[x['id'] for x in soup.select('[id]')]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len(soup.select('section.fv455')),2)

    def test_tampered_js_falls_back_without_false_claims(self):
        with tempfile.TemporaryDirectory() as d:
            tmp=Path(d);(tmp/'assets').mkdir();
            (tmp/'apollo_crosswalk.php').write_bytes(SRC.read_bytes())
            for source in (ROOT/'assets').iterdir(): (tmp/'assets'/source.name).write_bytes(source.read_bytes())
            with (tmp/'assets/evidence-crosswalk.js').open('ab') as f:f.write(b'\n// altered')
            h=render(tmp/'apollo_crosswalk.php')
            self.assertIn('evidence comparison is unavailable',h)
            self.assertNotIn('<script>',h)

    def test_missing_css_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            tmp=Path(d);(tmp/'assets').mkdir();(tmp/'apollo_crosswalk.php').write_bytes(SRC.read_bytes())
            (tmp/'assets/evidence-crosswalk.js').write_bytes((ROOT/'assets/evidence-crosswalk.js').read_bytes())
            h=render(tmp/'apollo_crosswalk.php')
            self.assertIn('evidence comparison is unavailable',h)

    def test_production_never_registers(self):
        code=f'''define('FV_R455_ENABLE_STAGING',true);define('FV_R455_STAGING_PAGE_ID',123);
        function add_action($name,$cb){{$GLOBALS['cb']=$cb;}}
        function add_shortcode($name,$cb){{$GLOBALS['shortcode']=$name;}}
        function wp_get_environment_type(){{return 'production';}}
        require '{SRC}'; ($GLOBALS['cb'])(); echo $GLOBALS['shortcode']??'not-registered';'''
        self.assertEqual(php(code),'not-registered')

    def test_staging_invalid_page_never_registers(self):
        code=f'''define('FV_R455_ENABLE_STAGING',true);define('FV_R455_STAGING_PAGE_ID',0);
        function add_action($name,$cb){{$GLOBALS['cb']=$cb;}}
        function add_shortcode($name,$cb){{$GLOBALS['shortcode']=$name;}}
        function wp_get_environment_type(){{return 'staging';}}
        require '{SRC}'; ($GLOBALS['cb'])(); echo $GLOBALS['shortcode']??'not-registered';'''
        self.assertEqual(php(code),'not-registered')

    def test_staging_wrong_page_returns_empty(self):
        code=f'''define('FV_R455_ENABLE_STAGING',true);define('FV_R455_STAGING_PAGE_ID',123);
        function add_action($name,$cb){{$GLOBALS['cb']=$cb;}}
        function add_shortcode($name,$cb){{$GLOBALS['shortcode']=$cb;}}
        function wp_get_environment_type(){{return 'staging';}}
        function get_queried_object_id(){{return 999;}}
        require '{SRC}'; ($GLOBALS['cb'])();echo ($GLOBALS['shortcode'])();'''
        self.assertEqual(php(code),'')

    def test_renderer_escape(self):
        self.assertEqual(php(f"require '{SRC}';echo fv455_escape('<script>\"&');"),'&lt;script&gt;&quot;&amp;')

    def test_source_validation_rejects_spoof_and_duplicate(self):
        code=f'''require '{SRC}';$s=fv455_records();$s[0]['url']='https://www.nasa.gov.attacker.example/gallery'; echo fv455_validate_records($s)?'unsafe':'safe';'''
        self.assertEqual(php(code),'safe')
        code=f'''require '{SRC}';$s=fv455_records();$s[1]['id']=$s[0]['id']; echo fv455_validate_records($s)?'unsafe':'safe';'''
        self.assertEqual(php(code),'safe')

if __name__=='__main__':unittest.main(verbosity=2)
