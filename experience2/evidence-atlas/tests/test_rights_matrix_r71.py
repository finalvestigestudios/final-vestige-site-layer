"""R71: verify deterministic, photo-free source review and fail-closed changes."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import build_atlas as atlas

class RightsMatrixTests(unittest.TestCase):
    def test_deterministic_six_pending_reviews(self):
        with tempfile.TemporaryDirectory() as td:
            first=atlas.build_rights_matrix_r71(Path(td))
            page=(Path(td)/'apollo-r71-media-rights-STAGING-ONLY.html').read_bytes()
            second=atlas.build_rights_matrix_r71(Path(td))
            self.assertEqual(first,second)
            self.assertEqual(page,(Path(td)/'apollo-r71-media-rights-STAGING-ONLY.html').read_bytes())
            self.assertEqual(page.count(b'data-r71-rights-row'),6)
            self.assertEqual(first['photo_reuse_clearances'],0)
            self.assertIn(b'provisional catalog-to-photograph association',page)
            self.assertNotIn(b'<img ',page)
            self.assertIn(b'NASA source 06',page)

    def test_refuse_forged_metadata_and_clearance(self):
        ledger=atlas.validate_custody()
        audit=atlas.validate_rights_audit(ledger)
        for field,new_value in [
            ('rights_status','APPROVED'),('human_link_check',True),
            ('downloaded_or_embedded',True),('crosswalk_catalog','FALSE'),
            ('catalog_display','displayed_as_PIA_number'),
            ('nasa_page','https://example.com/forged')]:
            with self.subTest(field=field):
                forged=deepcopy(audit);forged['records'][0][field]=new_value
                with patch.object(atlas,'validate_rights_audit',return_value=forged):
                    with tempfile.TemporaryDirectory() as td:
                        with self.assertRaises(ValueError):
                            atlas.build_rights_matrix_r71(Path(td))
if __name__=='__main__':unittest.main()
