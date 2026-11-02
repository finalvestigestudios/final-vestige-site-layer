#!/usr/bin/env python3
"""R55 NASA primary-page metadata / reuse review ledger, offline and no external fetch."""
from __future__ import annotations
import hashlib, json, sys, unittest
from pathlib import Path

ATLAS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ATLAS))
import build_atlas
LEDGER = ATLAS / 'sources/NASA_PAGE_RIGHTS_AUDIT_R55.json'

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

class NASAIndividualSourcePageReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=json.loads(LEDGER.read_text(encoding='utf-8'))
        cls.custody=build_atlas.validate_custody()
        cls.rows=cls.audit['records']

    def test_original_crosswalk_unchanged_and_pinned(self):
        original=build_atlas.CROSSWALK.read_bytes()
        self.assertEqual(git_blob(original),build_atlas.EXPECTED_BLOB)
        self.assertEqual(self.audit['crosswalk_blob_git_sha1'],build_atlas.EXPECTED_BLOB)

    def test_exact_six_source_pages_match_original_order_and_urls(self):
        self.assertEqual(self.audit['schema'],'fv.ex2.apollo.nasa-page-rights.r55.v1')
        self.assertEqual(len(self.rows),6)
        for item, source in zip(self.rows,self.custody['records']):
            self.assertEqual(item['id'],source['id'])
            self.assertEqual(item['nasa_page'],source['photo_url'])
            self.assertEqual(item['crosswalk_catalog'],source['catalog'])
            self.assertEqual(item['rights_status'],source['media_rights'].replace('INDIVIDUAL_REVIEW_REQUIRED','INDIVIDUAL_REVIEW_PENDING'))
            self.assertEqual(item['downloaded_or_embedded'],False)
            self.assertEqual(item['human_link_check'],False)
            self.assertTrue(item['nasa_page'].startswith('https://www.nasa.gov/image-detail/'))

    def test_catalog_01_is_not_falsely_confirmed(self):
        self.assertEqual(self.rows[0]['catalog_display'],'not_displayed_on_linked_nasa_page')
        self.assertIn('does not print',self.audit['catalog_01_note'])
        self.assertTrue(all(x['catalog_display']=='displayed_as_PIA_number' for x in self.rows[1:]))

    def test_source_credits_and_producers_are_not_conflated(self):
        self.assertEqual(self.rows[0]['image_credit_as_displayed'],'NASA')
        self.assertEqual(self.rows[3]['image_credit_as_displayed'],'NASA/Kim Shiflett')
        self.assertEqual(self.rows[5]['image_credit_as_displayed'],'NASA/Kim Shiflett')
        for i in (1,2,4):
            self.assertIsNone(self.rows[i]['image_credit_as_displayed'])
            self.assertEqual(self.rows[i]['producer_as_displayed'],'JSC')

    def test_rights_review_and_safeguards_remain_pending(self):
        self.assertEqual(self.audit['status'],'STAGING_HOLD')
        self.assertEqual(self.audit['policy']['independent_rights_clearance'],'NOT_COMPLETE')
        self.assertEqual(len(self.audit['prohibitions']),4)
        for item in self.rows:
            self.assertEqual(item['rights_status'],'INDIVIDUAL_REVIEW_PENDING')
            self.assertEqual(item['recognizable_person_review'],'required_or_undetermined')
            self.assertFalse(item['downloaded_or_embedded'])
        self.assertNotIn('data-lat',LEDGER.read_text())
        self.assertNotIn('data-lng',LEDGER.read_text())

    def test_source_date_scope_is_not_event_timeline(self):
        dates={x['id']:x['page_date_as_displayed'] for x in self.rows}
        self.assertIn('day absent',dates['01'])
        self.assertEqual(dates['03'],'October 18, 1966')
        self.assertEqual(dates['04'],'January 24, 2017')
        self.assertEqual(dates['06'],'January 24, 2017')

if __name__=='__main__': unittest.main()
