"""R51 source catalog-association notice and deterministic WP-output contract."""
from pathlib import Path
import hashlib,sys,tempfile,unittest
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_atlas,build_wordpress_stage

class R51SourceDisclosure(unittest.TestCase):
    def test_unmodified_custody_source(self):
        source=build_atlas.validate_custody()
        self.assertEqual(source['records'][0]['catalog'],'S67-19766')
        self.assertIn('not separately confirmed',source['records'][0]['identity_note'])
        self.assertEqual(build_atlas.git_blob(build_atlas.CROSSWALK.read_bytes()),build_atlas.EXPECTED_BLOB)
    def test_original_atlas_exposes_provisional_identity(self):
        document=build_atlas.make_html(build_atlas.validate_custody(),'','')
        self.assertEqual(document.count('data-fva-catalog-unconfirmed'),1)
        self.assertIn('Catalog-to-photograph identity remains unconfirmed pending archival review.',document)
        self.assertIn('Catalog verification notice: record 01',document)
        self.assertEqual(document.count('Catalog-to-photograph identity remains unconfirmed'),2)
        self.assertEqual(document.count('data-fva-record '),6)
        self.assertEqual(document.count('data-fva-citation-text'),6)
        self.assertNotIn('<img',document)
    def test_wordpress_custody_template_pinned(self):
        with tempfile.TemporaryDirectory() as path:
            m=build_wordpress_stage.build(Path(path))
            fragment=(Path(path)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_bytes()
            self.assertIn('0.0.51-staging',(HERE/'final-vestige-ex2-evidence-atlas.php').read_text())
            self.assertIn(hashlib.sha256(fragment).hexdigest(),(HERE/'final-vestige-ex2-evidence-atlas.php').read_text())
            self.assertEqual(m['embedded_images'],0)
            self.assertEqual(m['geographic_pins'],0)
            self.assertIn(b'data-fva-catalog-unconfirmed',fragment)
    def test_suite_warns_unconditionally_without_js(self):
        s=(HERE/'integration/fv-ex2-apollo-suite.php').read_text()
        self.assertIn('record 01 uses an unconfirmed S67-19766',s)
        self.assertIn('fv-ex2-apollo-suite__provenance',s)
        self.assertNotIn('wp_update_post(',s)
if __name__=='__main__':unittest.main()
