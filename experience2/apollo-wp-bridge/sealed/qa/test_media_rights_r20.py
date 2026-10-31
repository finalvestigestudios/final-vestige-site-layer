"""R20 rights provenance acceptance + adversarial cases (not legal clearance)."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from media_rights_ledger import build_media_rights, MediaHold, CASEFILE
from qa.nasa_editorial_gate import EditorialHold, NASA_MEDIA_RULES
from staging_admission import AdmissionError, admit, no_redirect_fetch
import test_http

class MediaRightsLedgerR20(unittest.TestCase):
    def test_six_links_zero_image_clearance_one_visible_catalog_hold(self):
        html,css,body,receipt=build_media_rights()
        data=json.loads(body)
        self.assertEqual(data['cleared_images'],0)
        self.assertEqual(data['images_embedded'],0)
        self.assertEqual(data['source_records'],6)
        self.assertEqual(data['catalog_label_holds'],1)
        self.assertEqual([x['catalog_label_discrepancy'] for x in data['records']],[True,False,False,False,False,False])
        self.assertTrue(all(x['inline_reuse_review']=='HOLD_NOT_ADMITTED' for x in data['records']))
        self.assertTrue(all(x['photo_embedded'] is False and x['geo_coordinates'] is None for x in data['records']))
        self.assertEqual(html.count('data-media-review='),6)
        self.assertEqual(html.count('data-media-hold="true"'),6)
        self.assertEqual(html.count('<details>'),6)
        self.assertIn('S67-19766',html)
        self.assertIn('New tab',html.replace('new tab','New tab'))
        self.assertEqual(body.count('"nasa_policy"'),6)
        self.assertEqual(data['nasa_policy_url'],NASA_MEDIA_RULES)
        self.assertEqual(sha256(html.encode()).hexdigest(),receipt['html_sha256'])
        self.assertEqual(sha256(body.encode()).hexdigest(),receipt['json_sha256'])

    def test_native_no_js_no_external_embedded_media(self):
        html,css,body,_=build_media_rights()
        for danger in ('<img','<picture','<script','<iframe','data-lat=', 'data-lon=', 'src='):
            self.assertNotIn(danger,html.lower())
        self.assertIn('{{FV_EX2_RIGHTS_EXPORT}}',html)
        self.assertIn('@container(max-width:740px)',css)
        self.assertIn('prefers-reduced-motion:reduce',css)
        self.assertIn('target="_blank" rel="noopener noreferrer"',html)

    def test_fail_closed_on_catalog_image_reuse_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp); data=json.loads((CASEFILE/'records.json').read_text())
            data['records'][2]['rights']='approved_free_reuse'
            (d/'records.json').write_text(json.dumps(data))
            with self.assertRaises((EditorialHold,MediaHold)):
                build_media_rights(casefile=d)

    def test_fail_closed_on_2017_photo_relabel(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp); data=json.loads((CASEFILE/'records.json').read_text())
            data['records'][3]['source_date']='24 Jan 1967'
            (d/'records.json').write_text(json.dumps(data))
            with self.assertRaises((EditorialHold,MediaHold)):
                build_media_rights(casefile=d)

    def test_fail_closed_on_crosswalk_silent_identifier_normalization(self):
        import media_rights_ledger as m
        real=m.build_crosswalk
        def falsified(rows):
            h,r=real(rows)
            r['records'][0]['catalog_identifier_label_match']=True
            return h,r
        with patch.object(m,'build_crosswalk',side_effect=falsified):
            with self.assertRaisesRegex(MediaHold,'discrepancy'):
                build_media_rights()

    def test_deterministic_review_index(self):
        self.assertEqual(build_media_rights(),build_media_rights())

class MediaRightsHttpR20(unittest.TestCase):
    @classmethod
    def setUpClass(cls): test_http.ApolloHttp.setUpClass()
    @classmethod
    def tearDownClass(cls): test_http.ApolloHttp.tearDownClass()

    def test_seventh_editor_only_download_verified(self):
        proof=admit(test_http.ApolloHttp.base,'/review','fv_test_mode=editor',allow_stub=True)
        self.assertEqual(proof['media_rights_review_holds'],6)
        self.assertEqual(proof['photos_admitted_for_reuse'],0)
        self.assertEqual(len(proof['exports_sha256']),7)
        self.assertEqual(proof['exports_sha256']['media-rights.json'],build_media_rights()[3]['json_sha256'])

    def test_media_download_mutation_blocked(self):
        def mutated(url,cookie=''):
            status,h,data=no_redirect_fetch(url,cookie)
            if cookie and 'file=media-rights.json' in url:
                return status,h,data.replace(b'HOLD_NOT_ADMITTED',b'CLEARED_FOR_REUSE')
            return status,h,data
        with self.assertRaisesRegex(AdmissionError,'Export integrity'):
            admit(test_http.ApolloHttp.base,'/review','fv_test_mode=editor',allow_stub=True,fetch=mutated)

    def test_media_review_header_mutation_blocked(self):
        def mutated(url,cookie=''):
            status,h,data=no_redirect_fetch(url,cookie)
            if 'x-fv-ex2-apollo-media-rights-sha256' in h:
                h['x-fv-ex2-apollo-media-rights-sha256']='0'*64
            return status,h,data
        with self.assertRaisesRegex(AdmissionError,'Media rights'):
            admit(test_http.ApolloHttp.base,'/review','fv_test_mode=editor',allow_stub=True,fetch=mutated)

if __name__=='__main__': unittest.main()
