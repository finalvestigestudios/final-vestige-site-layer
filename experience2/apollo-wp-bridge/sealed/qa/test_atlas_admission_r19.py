"""Atlas historical restraint: exact source custody, no geography, no-JS UX."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from atlas_admission import build_atlas_admission, AtlasHold, EXPECTED, GENERATED

class TestAtlasAdmissionR19(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fragment=(GENERATED/'fragment.html').read_text(encoding='utf-8')

    def test_six_verified_pinned_listing_links_but_zero_geo(self):
        html,css,content,receipt=build_atlas_admission(self.fragment)
        data=json.loads(content)
        self.assertEqual(data['record_count'],6)
        self.assertEqual([r['wordpress_listing_id'] for r in data['records']], [434,621,370,269,37,433])
        self.assertEqual([r['published_link_from_pinned_source'] for r in data['records']], [r[3] for r in EXPECTED])
        self.assertEqual(data['admitted_point_coordinates'],0)
        self.assertEqual(data['admitted_relationship_edges'],0)
        for r in data['records']:
            self.assertIsNone(r['coordinates'])
            self.assertFalse(r['map_pin_eligible'])
            self.assertEqual(r['geo_edges'],[])
            self.assertEqual(r['relationships_to_apollo_records'],'NONE_ESTABLISHED')
        self.assertEqual(receipt['json_sha256'],sha256(content.encode()).hexdigest())

    def test_native_no_js_details_export_not_media(self):
        html,css,content,receipt=build_atlas_admission(self.fragment)
        self.assertTrue(html.startswith('<details'))
        self.assertEqual(html.count('data-admission-record='),6)
        self.assertEqual(html.count('rel="noopener noreferrer"'),6)
        self.assertEqual(html.count('target="_blank"'),6)
        self.assertIn('{{FV_EX2_ATLAS_EXPORT}}',html)
        self.assertNotIn('<script',html)
        self.assertNotIn('<img',html)
        self.assertIn('@container(max-width:760px)',css)
        self.assertTrue(receipt['no_js_native_details'])

    def test_reject_changed_wp_id(self):
        with self.assertRaisesRegex(AtlasHold,'unexpected canonical'):
            build_atlas_admission(self.fragment.replace('WP 434','WP 999',1))

    def test_reject_changed_url_host(self):
        with self.assertRaisesRegex(AtlasHold,'unexpected canonical'):
            build_atlas_admission(self.fragment.replace('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',
                                                   'https://lookalike.invalid/2026/08/20/the-hatch-opened-inward-apollo-1/',1))

    def test_reject_silent_geospatial_promotion(self):
        with self.assertRaisesRegex(AtlasHold,'map status changed'):
            build_atlas_admission(self.fragment.replace('No mapped location: archival precision unreviewed.',
                                                  'Mapped location exact.',1))

    def test_reject_injected_coordinate(self):
        with self.assertRaisesRegex(AtlasHold,'unsafe element'):
            build_atlas_admission(self.fragment.replace('data-ex2-atlas-item data-ex2-theme',
                                                  'data-ex2-atlas-item data-lat="1.23" data-ex2-theme',1))

    def test_reject_mutated_category(self):
        with self.assertRaisesRegex(AtlasHold,'unexpected canonical'):
            build_atlas_admission(self.fragment.replace('data-ex2-theme="engineering"',
                                                   'data-ex2-theme="expeditions"',1))

    def test_reject_added_map_svg(self):
        with self.assertRaisesRegex(AtlasHold,'unsafe element'):
            build_atlas_admission(self.fragment.replace('data-ex2-atlas-grid>',
                                                  'data-ex2-atlas-grid><svg></svg>',1))

    def test_reject_deleted_atlas_card(self):
        with self.assertRaisesRegex(AtlasHold,'unsafe element'):
            build_atlas_admission(self.fragment.replace('data-ex2-atlas-item','data-removed-atlas-item',1))

    def test_export_is_deterministic(self):
        one=build_atlas_admission(self.fragment)
        two=build_atlas_admission(self.fragment)
        self.assertEqual(one,two)

if __name__=='__main__':unittest.main()
