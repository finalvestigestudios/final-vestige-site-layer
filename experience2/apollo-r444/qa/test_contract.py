"""Zero-network source, rights, release and tamper contracts for Apollo R444."""
import hashlib, html.parser, json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path
D=Path(__file__).resolve().parent.parent
S=D/'source_manifest.json'
CODE=D/'review_panel.php'
CSS=D/'assets/review-panel.css'
JS=D/'assets/review-panel.js'

class Audit(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.sections=0;self.cards=0;self.controls=0;self.details=0;self.geo=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.links.append(a.get('href'))
        if 'data-r444-root' in a:self.sections+=1
        if 'data-r444-record' in a:self.cards+=1
        if 'data-r444-controls' in a:self.controls+=1
        if tag=='details':self.details+=1
        for k in a:
            if k in ('data-lat','data-lng','data-geo','data-longitude','data-latitude'):self.geo.append(k)

def fixture():return subprocess.run(['php',str(D/'qa/fixture.php')],check=True,capture_output=True,text=True).stdout

class TestSourceCustody(unittest.TestCase):
    def test_manifest_is_exact_sha(self):self.assertIn(hashlib.sha256(S.read_bytes()).hexdigest(),CODE.read_text())
    def test_assets_pinned(self):
        for f in (CSS,JS):self.assertIn(hashlib.sha256(f.read_bytes()).hexdigest(),CODE.read_text())
    def test_signoff_not_invented(self):self.assertEqual(json.loads(S.read_text())['editorial_signoff'],'PENDING_INDEPENDENT_QD')
    def test_five_curated_records(self):
        r=json.loads(S.read_text())['records'];self.assertEqual(len(r),5);self.assertEqual(len({x['id'] for x in r}),5)
    def test_sources_are_nasa_only(self):
        self.assertEqual({x['url'] for x in json.loads(S.read_text())['records']},{'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'})
    def test_periods_and_limitations(self):
        r=json.loads(S.read_text())['records'];self.assertEqual([x['period'] for x in r],['original']*4+['later']);self.assertTrue(all(len(x['limit'])>45 for x in r))
    def test_render_uses_escaping(self):self.assertIn('htmlspecialchars',CODE.read_text())
    def test_no_dynamic_external_calls(self):
        c=CODE.read_text()+JS.read_text();self.assertNotIn('fetch(',c);self.assertNotIn('XMLHttpRequest',c);self.assertNotIn('localStorage',c)
    def test_no_media_or_fake_map(self):
        dom=fixture();a=Audit();a.feed(dom);self.assertFalse(a.geo);self.assertNotIn('<img',dom);self.assertNotIn('<iframe',dom)
    def test_two_independent_renderings(self):
        a=Audit();a.feed(fixture());self.assertEqual((a.sections,a.cards,a.controls,a.details),(2,10,2,10));self.assertEqual(len(set(a.ids)),len(a.ids))
    def test_one_article_link_per_instance(self):
        a=Audit();a.feed(fixture());self.assertEqual(a.links.count('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'),2)
    def test_no_checkout_or_signup(self):
        dom=fixture().lower();self.assertNotIn('payhip.com',dom);self.assertNotIn('stripe.com',dom);self.assertNotIn('<form',dom)
    def test_disclosure_exact_states(self):
        t=fixture();self.assertIn('Source identity: checked',t);self.assertIn('Historical interpretation: review pending',t);self.assertIn('Commercial image rights: not cleared',t)
    def test_no_false_media_rights_grant(self):self.assertIn('NO_MEDIA_REPRODUCED',S.read_text());self.assertIn('NASA is not a sponsor or endorser',fixture())
    def test_failopen_missing_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            t=Path(tmp);shutil.copytree(D,t/'r',ignore=shutil.ignore_patterns('QA','__pycache__'))
            (t/'r/source_manifest.json').unlink()
            p=subprocess.run(['php','-r',f"require '{t/'r/review_panel.php'}';echo fv_r444_render();"],capture_output=True,text=True,check=True)
            self.assertIn('research preview is unavailable',p.stdout)
    def test_failopen_mutated_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            t=Path(tmp);shutil.copytree(D,t/'r',ignore=shutil.ignore_patterns('QA','__pycache__'))
            with (t/'r/source_manifest.json').open('a') as f:f.write(' ')
            p=subprocess.run(['php','-r',f"require '{t/'r/review_panel.php'}';echo fv_r444_render();"],capture_output=True,text=True,check=True)
            self.assertIn('research preview is unavailable',p.stdout)
    def test_safeguard_assets_mutated(self):
        with tempfile.TemporaryDirectory() as tmp:
            t=Path(tmp);shutil.copytree(D,t/'r',ignore=shutil.ignore_patterns('QA','__pycache__'))
            (t/'r/assets/review-panel.js').write_text(JS.read_text()+'\n// unauthorized edit\n')
            setup="define('ABSPATH','/staging'); $GLOBALS['cb']=null; function add_shortcode($n,$cb){$GLOBALS['cb']=$cb;}"
            call=f"{setup} require '{t/'r/review_panel.php'}'; echo ($GLOBALS['cb'])();"
            p=subprocess.run(['php','-r',call],capture_output=True,text=True,check=True)
            self.assertIn('research preview is unavailable',p.stdout)
    def test_css_no_unscoped_typography(self):
        css=CSS.read_text();self.assertIn('.fv-r444',css);self.assertIn('prefers-reduced-motion',css);self.assertIn('forced-colors',css)
    def test_native_disclosure_nojs(self):self.assertEqual(fixture().count('<details>'),10)

if __name__=='__main__':unittest.main()
