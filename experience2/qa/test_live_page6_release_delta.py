#!/usr/bin/env python3
"""Adversarial regression tests; private ZIP is supplied locally, never committed."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from verify_live_page6_release_delta import CHAPTERS, audit, candidate, media_name

ROOT = Path(__file__).resolve().parent
LIVE = json.loads((ROOT/'live_wp_page6_inventory.json').read_text())
ZIP = ROOT/'candidate/fv-ex2-official-playground-web-review.zip'

class DriftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.p = candidate(ZIP)

    def test_01_exact_candidate_source(self):
        self.assertEqual(self.p['sha256'], 'baf26bcaddbf1b86b90f0065e1d68fbd856be03027ecd9d14ebc0ada60a21b1d')

    def test_02_public_flagship_is_already_published(self):
        r=audit(LIVE,self.p)
        self.assertTrue(r['published_wordpress_page6_already_seven_chapter'])
        self.assertEqual(r['published']['chapters'],7)
        self.assertEqual(r['published']['margins'],72)

    def test_03_media_delta_holds(self):
        r=audit(LIVE,self.p)
        self.assertEqual(r['missing_from_preview'],['edit-017-v02-nypl-5003296-original.jpg'])
        self.assertIn('PUBLIC_NYPL_RIGHTS_REVIEW',r['source_delta_risks'])

    def test_04_focus_delta(self):
        r=audit(LIVE,self.p)
        self.assertEqual((r['published']['focus_links'],r['candidate']['focus_links']),(4,5))
        self.assertIn('FOCUS_CTA_COUNT_DIFFERENCE',r['source_delta_risks'])

    def test_05_published_nypl_query_normalization(self):
        self.assertEqual(media_name(LIVE['archive_images'][2]),'edit-017-v02-nypl-5003296-original.jpg')

    def test_06_reject_untrusted_media_hosts(self):
        for url in ('http://finalvestige.com/wp-content/uploads/a.jpg',
                    'https://evil.example/wp-content/uploads/a.jpg',
                    'https://i0.wp.com.evil.example/wp-content/uploads/a.jpg'):
            with self.subTest(url=url), self.assertRaises(ValueError): media_name(url)

    def test_07_reject_wrong_page_or_status(self):
        for key,val in (('wp_page_id',7),('wp_status','draft'),('wp_slug','focus')):
            fake=copy.deepcopy(LIVE);fake[key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):audit(fake,self.p)

    def test_08_reject_malformed_content_sha(self):
        fake=copy.deepcopy(LIVE);fake['wp_content_utf8_sha256']='not-a-sha'
        with self.assertRaises(ValueError):audit(fake,self.p)

    def test_09_reject_missing_chapter(self):
        fake=copy.deepcopy(LIVE);fake['chapter_ids']=CHAPTERS[:-1]
        with self.assertRaises(ValueError):audit(fake,self.p)

    def test_10_reject_tampered_zip(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'mutated.zip';path.write_bytes(ZIP.read_bytes()+b'X')
            with self.assertRaises(ValueError):candidate(path)

    def test_11_no_automatic_release_on_structural_parity(self):
        fake=copy.deepcopy(LIVE)
        fake['archive_images']=['https://finalvestige.com/wp-content/uploads/2026/08/'+x for x in self.p['images']]
        fake['focus_link_count']=self.p['focus']
        r=audit(fake,self.p)
        self.assertEqual(r['decision'],'HOLD')
        self.assertFalse(r['never_publish_automatically'] is False)

    def test_12_preserves_72_margins(self):
        fake=copy.deepcopy(LIVE);fake['margins_count']=71
        self.assertIn('MARGINS_DRIFT',audit(fake,self.p)['source_delta_risks'])

if __name__ == '__main__': unittest.main(verbosity=2)
