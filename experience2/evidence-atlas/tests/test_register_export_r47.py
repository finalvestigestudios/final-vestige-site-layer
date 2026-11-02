"""R47: conservative, metadata-only, complete source-register download contract."""
from pathlib import Path
import hashlib
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_atlas,build_wordpress_stage

class RegisterExportR47(unittest.TestCase):
    def test_source_remains_pinned(self):
        c=build_atlas.validate_custody()
        self.assertEqual(len(c['records']),6)
        self.assertTrue(all(x['media_rights']=='INDIVIDUAL_REVIEW_REQUIRED' for x in c['records']))
        self.assertEqual(c['records'][0]['date'],'1967-01')

    def test_export_progressively_enhanced(self):
        doc=build_atlas.make_html(build_atlas.validate_custody(),'', '')
        self.assertEqual(doc.count('data-fva-export hidden'),1)
        self.assertEqual(doc.count('data-fva-export-status'),1)
        self.assertEqual(doc.count('data-fva-citation-text'),6)
        self.assertEqual(doc.count('data-fva-record '),6)
        self.assertIn('With JavaScript enabled you may save the same references',doc)
        for needle in ('<img','<canvas','data-lat','data-lng'):
            self.assertNotIn(needle,doc)

    def test_js_uses_local_citations_without_network(self):
        js=(HERE/'atlas.js').read_text()
        for needle in ('new Blob([text]', 'document.createElement(\'a\')',
                       'URL.revokeObjectURL(blobUrl)', "root.querySelector('[data-fva-export]')",
                       'url.hostname!==\'www.nasa.gov\'',
                       "!citation.includes('individual review required')"):
            self.assertIn(needle,js)
        self.assertNotIn('fetch(',js)
        self.assertNotIn('localStorage',js)

    def test_compiled_stage_and_sha_pin(self):
        with tempfile.TemporaryDirectory() as td:
            m=build_wordpress_stage.build(Path(td))
            fragment=(Path(td)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_bytes()
            php=(HERE/'final-vestige-ex2-evidence-atlas.php').read_text()
            self.assertIn(hashlib.sha256(fragment).hexdigest(),php)
            self.assertIn('0.0.57-staging',php)
            self.assertEqual(m['schema'],'fv.ex2.apollo.wp-stage.r49.v1')
            self.assertEqual(m['embedded_images'],0)
            self.assertEqual(m['geographic_pins'],0)

if __name__=='__main__':unittest.main()
