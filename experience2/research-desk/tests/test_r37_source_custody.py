"""R37 source-custody contract tests for the ACTUAL NASA Research Desk template.
Does not install or alter WordPress. Run from full repository checkout:
    python -m unittest discover -s experience2/research-desk/tests -p 'test_r37*.py' -v
"""
import hashlib
import json
import pathlib
import re
import subprocess
import unittest
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]

def git_blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()

class HTMLRefs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.aria, self.embeds = [], [], [], []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get('id'):
            self.ids.append(d['id'])
        if tag == 'a':
            self.hrefs.append(d.get('href', ''))
        for key in ('aria-controls','aria-labelledby','for'):
            if d.get(key):
                self.aria += d[key].split()
        if tag in ('img','picture','iframe','video','script','canvas'):
            self.embeds.append(tag)

class R37SourceCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT/'templates/ledger.html').read_text(encoding='utf8')
        cls.css = (ROOT/'assets/source-ledger.css').read_text(encoding='utf8')
        cls.js = (ROOT/'assets/source-ledger.js').read_text(encoding='utf8')
        cls.data = json.loads((ROOT/'sources/R37_PHOTO_CUSTODY_CROSSWALK.json').read_text(encoding='utf8'))
        cls.records = cls.data['records']

    def validate(self, html):
        self.assertEqual(html.count('data-fvx-record data-fvx-search='), 6)
        self.assertEqual(html.count('data-fvx-photo-record='), 6)
        self.assertEqual(html.count('data-fvx-chrono-link'), 6)
        self.assertEqual(html.count('Image reuse has not been individually reviewed or cleared'), 6)
        parsed = HTMLRefs()
        parsed.feed(html)
        self.assertFalse(parsed.embeds, 'No NASA photographs or executable embeds permitted')
        self.assertEqual(len(parsed.ids), len(set(parsed.ids)), 'Duplicate IDs')
        self.assertTrue(set(parsed.aria).issubset(set(parsed.ids)), 'Unresolved ARIA references')
        for href in parsed.hrefs:
            self.assertTrue(href.startswith(('#','https://www.nasa.gov/','https://finalvestige.com/')),
                            'Unauthorized external destination: ' + href)
        for record in self.records:
            anchor = 'fv-ex2-ledger-apollo1-record-' + record['id']
            start = html.find('id="' + anchor + '"')
            self.assertGreaterEqual(start, 0)
            stop = html.find('</article>', start)
            self.assertGreater(stop, start)
            card = html[start:stop]
            self.assertIn('data-fvx-photo-record="' + record['id'] + '"', card)
            self.assertIn(record['photo_url'], card)
            self.assertIn(record['date_label'], card)
            self.assertIn('External NASA source link only', card)
            self.assertIn('href="#' + anchor + '"', html)
        self.assertNotRegex(html, r'data-(?:lat|lng|fvx-geo)|(?:mapbox|leaflet)')
        return parsed

    def test_six_original_records_source_custody_and_no_embedded_media(self):
        self.validate(self.html)

    def test_dates_not_mistaken_for_fire_sequence(self):
        self.assertIn('not a reconstruction of the fire', self.html)
        self.assertIn('no asserted day', self.html)
        self.assertIn('January 24, 2017', self.html)
        self.assertIn('October 18, 1966', self.html)

    def test_source_integrity_reviewed_exact_hashes(self):
        expected = {
            'templates/ledger.html':'8b14587187b375e93cfbd4436b99bfb6cd3d2f32',
            'assets/source-ledger.css':'e1e448f1ab14061d5ddd94fb51b652799f859791',
            'assets/source-ledger.js':'98e5cde97eb487df1a2854400833fd8ed1f06c69',
        }
        for name, digest in expected.items():
            self.assertEqual(git_blob(ROOT/name), digest, name+' changed without QA review')

    def test_source_rights_hold_and_no_speculative_geo(self):
        self.assertEqual(self.data['release'], 'STAGING_HOLD')
        self.assertEqual(len(self.records), 6)
        self.assertTrue(all(r['media_rights']=='INDIVIDUAL_REVIEW_REQUIRED' for r in self.records))
        self.assertIn('structured catalog metadata', self.records[0]['identity_note'])
        self.assertFalse(any('coordinate' in r or 'lat' in r for r in self.records))

    def test_progressive_enhancement_cleanup_and_native_disclosures(self):
        self.assertIn("root.addEventListener('click',navigate)", self.js)
        self.assertIn("root.removeEventListener('click',navigate)", self.js)
        self.assertIn("search.value=''", self.js)
        self.assertIn("cards.forEach(card=>{card.hidden=false;})", self.js)
        self.assertEqual(self.html.count('<details class="fv-ex2-ledger__custody"'), 6)
        self.assertNotRegex(self.html, r'<article[^>]*\shidden(?:\s|>|=)')

    def test_mobile_and_keyboard_styles_present(self):
        for marker in ('@media(max-width:760px)', '@media(max-width:480px)',
                       ':focus-visible', '@media(prefers-reduced-motion:reduce)',
                       '.fv-ex2-ledger__chronology', '.fv-ex2-ledger__custody'):
            self.assertIn(marker, self.css)

    def test_negative_missing_rights_note_rejected(self):
        with self.assertRaises(AssertionError):
            self.validate(self.html.replace('Image reuse has not been individually reviewed or cleared',
                                            'Rights cleared', 1))

    def test_negative_missing_photo_panel_rejected(self):
        with self.assertRaises(AssertionError):
            self.validate(self.html.replace('data-fvx-photo-record="01"', 'data-broken-record="01"', 1))

    def test_negative_added_coordinate_rejected(self):
        with self.assertRaises(AssertionError):
            self.validate(self.html.replace('data-fvx-ledger ', 'data-lat="0" data-fvx-ledger ', 1))

    def test_negative_unauthorized_destination_rejected(self):
        with self.assertRaises(AssertionError):
            self.validate(self.html.replace('https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
                                            'https://unverified.example/photo', 1))

    def test_php_and_node_syntax(self):
        files = [('php','-l',str(ROOT/'final-vestige-ex2-research-desk.php')),
                 ('node','--check',str(ROOT/'assets/source-ledger.js'))]
        for cmd in files:
            p=subprocess.run(cmd,check=False,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)

    def test_php_triple_shortcode_chronology_refs(self):
        probe=ROOT/'tests/r36_wp_probe.php'
        p=subprocess.run(['php',str(probe),str(ROOT/'final-vestige-ex2-research-desk.php')],
                         check=True,capture_output=True,text=True)
        bodies=json.loads(p.stdout)['html']
        self.assertEqual(len(bodies),3)
        ids=[]
        for instance,body in enumerate(bodies,1):
            self.assertEqual(body.count('data-fvx-chrono-link'),6)
            refs=HTMLRefs();refs.feed(body)
            ids += refs.ids
            for href in refs.hrefs:
                if href.startswith('#'):
                    self.assertIn(href[1:], refs.ids)
            if instance>1:
                self.assertIn(f'fv-ex2-ledger-apollo1-{instance}-record-01',body)
        self.assertEqual(len(ids),len(set(ids)), 'Repeated shortcode has duplicate anchor IDs')

if __name__=='__main__':
    unittest.main()
