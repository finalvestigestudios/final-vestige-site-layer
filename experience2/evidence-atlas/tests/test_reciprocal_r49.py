"""R49 exact PR158 source identity and reciprocal navigation regression gates."""
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_atlas,build_wordpress_stage

class ReciprocalR49(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js=(HERE/'atlas.js').read_text()
        cls.custody=build_atlas.validate_custody()
        cls.pr158=(HERE/'tests/fixtures/source-ledger.pr158.html').read_bytes()
        cls.css=(HERE/'tests/fixtures/source-ledger.pr158.css').read_bytes()
    def test_exact_pr158_original_source_blobs(self):
        self.assertEqual(build_atlas.git_blob(self.pr158),'403d128c57b9bc82dac7c619651689070edef86c')
        self.assertEqual(build_atlas.git_blob(self.css),'b8cf00afeceba115a9e9d19044fc11dcf2890cbe')
        self.assertNotIn(b'data-fvx-photo-record',self.pr158)
        self.assertEqual(self.pr158.count(b'fv-ex2-ledger__recordlinks'),6)
    def test_all_six_record_ids_catalogs_and_photo_urls(self):
        for row in self.custody['records']:
            self.assertIn(('id="fv-ex2-ledger-apollo1-record-'+row['id']+'"').encode(),self.pr158)
            self.assertIn(row['catalog'].encode(),self.pr158)
            self.assertIn(('href="'+row['photo_url']+'"').encode(),self.pr158)
            self.assertIn(("['"+row['id']+"','"+row['catalog']+"','"+row['photo_url']+"']").encode().decode(),self.js)
    def test_links_are_custody_gated_and_reversible(self):
        for token in ("const proof=verifyDesk();","slots.every(Boolean)","removeDeskBacklinks();",
                      "link.setAttribute('data-fvx-to-atlas',id)","link.href='#'+cards[i].id",
                      "const onDeskBackJump=event=>{","event.preventDefault();withdrawDesk(true);return;"):
            self.assertIn(token,self.js)
    def test_no_unsourced_geo_or_tracking(self):
        for token in ('fetch(', 'navigator.geolocation','data-fva-geo','localStorage'):
            self.assertNotIn(token,self.js)
    def test_version_and_staging_manifest(self):
        self.assertIn('0.0.56-staging',(HERE/'final-vestige-ex2-evidence-atlas.php').read_text())
        self.assertIn('fv.ex2.apollo.wp-stage.r49.v1',(HERE/'build_wordpress_stage.py').read_text())
    def test_source_integrity_and_safety(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            m=build_wordpress_stage.build(Path(tmp))
        self.assertEqual(m['media_rights_unreviewed'],6)
        self.assertEqual(m['embedded_images'],0)
        self.assertEqual(m['geographic_pins'],0)

if __name__=='__main__':unittest.main()
