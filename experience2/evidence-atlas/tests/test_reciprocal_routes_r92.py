#!/usr/bin/env python3
"""R92 adversarial navigation/source custody tests: rebuild actual R91/R90 source."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
SRC=HERE.parent/'tools'/'build_reciprocal_routes_r92.py'
spec=importlib.util.spec_from_file_location('apollo_routes_r92',SRC)
r92=importlib.util.module_from_spec(spec);spec.loader.exec_module(r92)

class RouteCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='r92-custody-base-')
        cls.good=Path(cls.temp.name)/'good'
        r92.build(cls.good)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='r92-mutation-')
        self.stage=Path(self.temp.name)/'stage'
        shutil.copytree(self.good,self.stage)

    def tearDown(self):self.temp.cleanup()

    def replace(self,name,old,new):
        file=self.stage/name
        content=file.read_text('utf8')
        self.assertIn(old,content)
        file.write_text(content.replace(old,new,1),'utf8')

    def test_valid_source_and_release_receipts(self):
        result=r92.audit(self.stage)
        self.assertEqual(result['verified_new_reciprocal_routes'],54)
        self.assertEqual(result['existing_hub_routes'],18)
        self.assertEqual(result['source_bindings'],24)
        self.assertEqual(result['photographic_rights_cleared'],0)
        self.assertFalse(result['deployment_allowed'])

    def test_no_javascript_route_markup_54(self):
        for view in r92.VIEWS:
            text=(self.stage/view).read_text('utf8')
            if view!='R89_REVIEW_HUB.html':
                self.assertEqual(text.count('class="r92-evidence-routes"'),6)
                self.assertEqual(text.count('aria-label="Other evidence views for source '),6)

    def test_swapped_same_source_route_rejected(self):
        self.replace('R88_READING_ROOM.html',
          'R87_PHOTOGRAPH_DATE_RAIL.html#r87-record-01',
          'R87_PHOTOGRAPH_DATE_RAIL.html#r87-record-02')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_path_traversal_rejected(self):
        self.replace('R85_NASA_SOURCE_REVIEW.html',
          'R89_REVIEW_HUB.html#r89-source-03','../R89_REVIEW_HUB.html#r89-source-03')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_javascript_pseudolink_rejected(self):
        self.replace('R87_PHOTOGRAPH_DATE_RAIL.html',
          'R88_READING_ROOM.html#r88-03','javascript:alert(1)')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_duplicate_route_rejected(self):
        self.replace('R88_READING_ROOM.html',
          'R85_NASA_SOURCE_REVIEW.html#r85-source-04',
          'R89_REVIEW_HUB.html#r89-source-04')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_missing_route_rejected(self):
        self.replace('R88_READING_ROOM.html',
          'href="R87_PHOTOGRAPH_DATE_RAIL.html#r87-record-04"',
          'href=""')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_source_misattribution_rejected(self):
        self.replace('R85_NASA_SOURCE_REVIEW.html',
          'https://www.nasa.gov/image-detail/amf-s67-21294/',
          'https://www.nasa.gov/image-detail/amf-s67-15717/')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_duplicate_article_id_rejected(self):
        self.replace('R88_READING_ROOM.html','id="r88-01"','id="r88-02"')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_mutated_css_rejected(self):
        self.replace('reading_room_r88.css',
          '/* R92 same-source route switcher.','@import url(https://example.com/x.css);\n/* R92 same-source route switcher.')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_unreviewed_image_rejected(self):
        self.replace('R87_PHOTOGRAPH_DATE_RAIL.html',
           '<nav class="r92-evidence-routes"','<img src="https://example.com/unlicensed.jpg"><nav class="r92-evidence-routes"')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_inherited_receipt_mismatch_rejected(self):
        self.replace('R91_ASSET_BOUNDARY_RECEIPT.json','"release": "STAGING_HOLD"','"release": "PUBLISHED"')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_unapproved_rights_claim_rejected(self):
        self.replace('R89_INTEGRITY_RECEIPT.json',
          '"photo_rights_cleared": 0','"photo_rights_cleared": 6')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_hub_redirect_to_wrong_source_rejected(self):
        self.replace('R89_REVIEW_HUB.html',
            'R85_NASA_SOURCE_REVIEW.html#r85-source-01',
            'R85_NASA_SOURCE_REVIEW.html#r85-source-06')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_missing_print_rights_warning_rejected(self):
        self.replace('R87_PHOTOGRAPH_DATE_RAIL.html',
            '<p class="r92-print-rights">',
            '<p class="r92-unreviewed-rights">')
        with self.assertRaises(ValueError):r92.audit(self.stage)

    def test_print_rights_present_on_all_evidence_cards(self):
        for view in r92.VIEWS:
            if view!='R89_REVIEW_HUB.html':
                content=(self.stage/view).read_text('utf8')
                self.assertEqual(content.count('class="r92-print-rights"'),6)
                self.assertEqual(content.count('Photographic reuse: INDIVIDUAL REVIEW REQUIRED.'),6)

    def test_routes_only_same_record_no_speculation(self):
        receipt=r92.audit(self.stage)
        self.assertEqual(receipt['new_inferred_historical_edges'],0)
        self.assertEqual(receipt['reviewed_geographic_pins'],0)
        for view in r92.VIEWS:
            html=(self.stage/view).read_text('utf8')
            self.assertNotIn('data-lat=',html)
            self.assertNotIn('data-lon=',html)

if __name__=='__main__':unittest.main()
