"""R48 non-geospatial source-identity bridge contract and build integrity."""
import hashlib,re,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE/'tests'))
import build_atlas,build_wordpress_stage
from browser_r48_smoke import document,JSP

class ResearchDeskBridgeR48(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.custody=build_atlas.validate_custody()
        cls.html=build_atlas.make_html(cls.custody,'','')
        cls.js=(HERE/'atlas.js').read_text()
    def test_all_six_same_page_anchors_generated(self):
        for record in self.custody['records']:
            self.assertIn('href="#fv-ex2-ledger-apollo1-record-'+record['id']+'" hidden',self.html)
        self.assertEqual(self.html.count('data-fva-to-desk'),6)
    def test_bridge_is_hidden_without_script(self):
        self.assertEqual(self.html.count('data-fva-to-desk href='),6)
        self.assertIn('data-fva-desk-status role="status" aria-live="polite" hidden',self.html)
    def test_id_url_catalog_pins(self):
        for record in self.custody['records']:
            self.assertIn("['"+record['id']+"','"+record['catalog']+"','"+record['photo_url']+"']",self.js)
    def test_pinned_original_research_desk_js(self):
        self.assertEqual(build_atlas.git_blob(JSP.read_bytes()),'32e757cc4dc8708397ff65ac21e89dd319781d78')
    def test_research_desk_requires_all_six_exact_sources(self):
        self.assertIn('records.length!==6',self.js)
        self.assertIn('photoLinks.length===1',self.js)
        self.assertIn("photoLinks[0].getAttribute('href')===url",self.js)
        self.assertIn('roots.length!==1',self.js)
    def test_desk_failure_does_not_hide_atlas_records(self):
        self.assertIn('withdrawDesk(true)',self.js)
        self.assertIn('deskLinks.forEach(link=>{link.hidden=true;})',self.js)
        self.assertNotIn('target.hidden=true',self.js)
    def test_normal_cohost_fixture_has_unique_ids(self):
        from html.parser import HTMLParser
        class IDs(HTMLParser):
            def __init__(self):super().__init__();self.ids=[]
            def handle_starttag(self,t,attrs):
                d=dict(attrs)
                if 'id' in d:self.ids.append(d['id'])
        p=IDs();p.feed(document())
        self.assertEqual(len(p.ids),len(set(p.ids)))
    def test_no_images_coordinates_network_tracking(self):
        self.assertNotIn('<img',self.html)
        for token in ('data-lat','data-lng','fetch(', 'localStorage','navigator.geolocation'):
            self.assertNotIn(token,self.js)
    def test_exact_php_fragment_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest=build_wordpress_stage.build(Path(temp))
            frag=(Path(temp)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_bytes()
            expected=hashlib.sha256(frag).hexdigest()
            self.assertIn(expected,(HERE/'final-vestige-ex2-evidence-atlas.php').read_text())
            self.assertEqual(manifest['schema'],'fv.ex2.apollo.wp-stage.r49.v1')
    def test_component_css_keyboard_and_print(self):
        css=(HERE/'atlas.css').read_text()
        self.assertIn('.fva-card__desk-link{display:inline-flex;align-items:center;min-height:44px',css)
        self.assertIn('@media print{.fva-card__desk-link,.fva-desk-status{display:none!important}}',css)

if __name__=='__main__':unittest.main()
