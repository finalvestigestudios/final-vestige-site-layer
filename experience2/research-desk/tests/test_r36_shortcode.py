"""R36 WordPress lifecycle double for ACTUAL six-record NASA template.
No WordPress install is implied. Run: python -m unittest tests/test_r36_shortcode.py
"""
import hashlib, json, pathlib, subprocess, unittest
from html.parser import HTMLParser
BASE=pathlib.Path(__file__).resolve().parents[1]
PROBE=BASE/'tests/r36_wp_probe.php'
PLUGIN=BASE/'final-vestige-ex2-research-desk.php'
class Elements(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.refs=[]; self.urls=[]; self.records=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for key in ('for','aria-labelledby','aria-controls'):
            if key in a:self.refs.extend(a[key].split())
        if 'data-fvx-record' in a:self.records+=1
        if tag=='a' and 'href' in a:self.urls.append(a['href'])
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result=subprocess.run(['php',str(PROBE),str(PLUGIN)],check=True,capture_output=True,text=True)
        cls.html=json.loads(result.stdout)['html']
    def test_three_instances_and_six_records_each(self):
        self.assertEqual(len(self.html),3)
        for page in self.html:
            p=Elements();p.feed(page)
            self.assertEqual(p.records,6)
            self.assertEqual(len(p.ids),len(set(p.ids)))
    def test_cross_instance_identifiers_and_references(self):
        p=Elements();p.feed(''.join(self.html))
        self.assertEqual(len(p.ids),len(set(p.ids)))
        self.assertTrue(set(p.refs).issubset(set(p.ids)))
    def test_first_instance_existing_anchors_unchanged(self):
        self.assertIn('id="fv-ex2-ledger-apollo1-title"',self.html[0])
        self.assertNotIn('apollo1-2-',self.html[0])
    def test_second_third_instance_labels_and_controls(self):
        for count in (2,3):
            body=self.html[count-1]
            for value in (f'id="fv-ex2-ledger-apollo1-{count}-title"',f'for="fv-ex2-ledger-apollo1-{count}-search"',f'aria-controls="fv-ex2-ledger-apollo1-{count}-grid"'):
                self.assertIn(value,body)
    def test_evidence_content_and_nasa_destinations_are_unchanged(self):
        first=Elements();first.feed(self.html[0])
        self.assertTrue(any(url.startswith('https://www.nasa.gov/') for url in first.urls))
        self.assertIn('S67-19766',self.html[0])
        for body in self.html[1:]:
            other=Elements();other.feed(body)
            self.assertEqual(first.urls,other.urls)
            self.assertNotIn('must-not-render',body)
    def test_r37_reviewed_template_sha_and_six_source_drawers(self):
        p=BASE/'templates/ledger.html'
        raw=p.read_bytes()
        git_blob=hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        self.assertEqual(git_blob,'8b14587187b375e93cfbd4436b99bfb6cd3d2f32')
        self.assertEqual(raw.count(b'data-fvx-photo-record='),6)
        self.assertEqual(raw.count(b'data-fvx-chrono-link'),6)
    def test_php_and_js_parse(self):
        for path in (PLUGIN,PROBE):
            p=subprocess.run(['php','-l',str(path)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        p=subprocess.run(['node','--check',str(BASE/'assets/source-ledger.js')],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
    def test_js_strict_fail_open_markers(self):
        js=(BASE/'assets/source-ledger.js').read_text()
        for marker in ("search.removeEventListener('input',filter)","cards.forEach(card=>{card.hidden=false;})","if(indexed===null)throw"):
            self.assertIn(marker,js)
if __name__=='__main__':unittest.main()
