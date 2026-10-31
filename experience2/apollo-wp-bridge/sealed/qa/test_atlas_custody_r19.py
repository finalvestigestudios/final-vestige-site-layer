"""R19 evidence Atlas editorial refusal/HTML/private export regression tests."""
from __future__ import annotations
from pathlib import Path
import json
import tempfile
import unittest
from atlas_custody import build_atlas, AtlasHold
from staging_admission import AdmissionError, admit, no_redirect_fetch
import test_http

HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent / 'generated'

class TestR19AtlasCustody(unittest.TestCase):
    def test_01_pinned_six_published_links_and_no_geo(self):
        html,css,data,proof=build_atlas()
        obj=json.loads(data)
        self.assertEqual(obj['record_count'],6)
        self.assertEqual(obj['map_pin_count'],0)
        self.assertEqual(obj['relationship_edge_count'],0)
        self.assertEqual(proof['status'],'PASS_PINNED_PUBLICATION_INDEX_WITHOUT_GEO')
        self.assertEqual(sum(row['map_pin_eligible'] for row in obj['records']),0)
        self.assertTrue(all(row['coordinates'] is None and row['relationship_edges']==[]
                            and row['image_assets']==[] for row in obj['records']))
        self.assertEqual(html.count('data-atlas-custody-id='),6)
        self.assertIn('<details id="fv-ex2-atlas-custody"',html)
        self.assertIn('not a live-HTTP audit',html)
        self.assertNotIn('<img',html)
        self.assertNotIn('<iframe',html)
        self.assertNotIn('<script',html)

    def _mutate(self, old, new, expected_hold=None):
        raw=(BASE/'fragment.html').read_text()
        self.assertIn(old,raw)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'fragment.html').write_text(raw.replace(old,new,1))
            with self.assertRaises(AtlasHold) as exc:
                build_atlas(p)
            if expected_hold: self.assertIn(expected_hold,str(exc.exception))

    def test_02_reject_invented_geopins(self):
        self._mutate('data-ex2-atlas-item data-ex2-theme="engineering"',
                     'data-ex2-atlas-item data-lat="28.5" data-ex2-theme="engineering"',
                     'Map coordinates')

    def test_03_reject_invented_map_edge(self):
        self._mutate('data-ex2-atlas-item data-ex2-theme="engineering"',
                     'data-ex2-atlas-item data-geo-edge="next" data-ex2-theme="engineering"',
                     'Map coordinates')

    def test_04_reject_hypothetical_nasa_image_embedding(self):
        self._mutate('id="atlas" class="ex2-section ex2-atlas"',
                     'id="atlas" class="ex2-section ex2-atlas"><img src="https://www.nasa.gov/photo.jpg" alt="">',
                     'Map coordinates')

    def test_05_reject_changed_link_even_same_website(self):
        self._mutate('the-hatch-opened-inward-apollo-1/',
                     'an-unsourced-apollo-1-copy/', 'Atlas publication')

    def test_06_reject_changed_post_id(self):
        self._mutate('WP 434','WP 999','Atlas publication')

    def test_07_reject_hidden_geo_status(self):
        self._mutate('No mapped location: archival precision unreviewed.',
                     'Map pin verified.', 'Atlas publication')

    def test_08_reject_extra_unapproved_record(self):
        self._mutate('<p class="ex2-atlas__empty"',
                     '<article data-ex2-atlas-item data-ex2-theme="engineering"></article><p class="ex2-atlas__empty"',
                     'exactly six')

    def test_09_reject_script_and_event_handlers(self):
        self._mutate('data-ex2-atlas-item data-ex2-theme="engineering"',
                     'data-ex2-atlas-item onclick="alert(1)" data-ex2-theme="engineering"',
                     'Map coordinates')

    def test_10_reject_truncated_atlas(self):
        self._mutate('<section id="atlas"', '<div id="atlas"', 'Atlas root')

class TestR19ActualPHP(unittest.TestCase):
    @classmethod
    def setUpClass(cls): test_http.ApolloHttp.setUpClass()
    @classmethod
    def tearDownClass(cls): test_http.ApolloHttp.tearDownClass()

    def test_11_real_php_private_atlas_export_and_response_provenance(self):
        report=admit(test_http.ApolloHttp.base, '/review','fv_test_mode=editor',allow_stub=True)
        self.assertEqual(report['atlas_publication_references'],6)
        self.assertEqual(report['atlas_geo_pins'],0)
        self.assertEqual(report['atlas_edges'],0)
        self.assertEqual(len(report['exports_sha256']),6)
        self.assertIn('atlas-custody.json',report['exports_sha256'])
        self.assertFalse(report['wordpress_integrated'])

    def test_12_mutated_atlas_http_provenance_rejected(self):
        def corrupt(url,cookie=''):
            status,h,raw=no_redirect_fetch(url,cookie)
            if 'x-fv-ex2-apollo-atlas-sha256' in h:
                h['x-fv-ex2-apollo-atlas-sha256']='0'*64
            return status,h,raw
        with self.assertRaisesRegex(AdmissionError,'Atlas provenance index hash mismatch'):
            admit(test_http.ApolloHttp.base, '/review','fv_test_mode=editor',allow_stub=True,fetch=corrupt)

    def test_13_mutated_atlas_export_rejected(self):
        def corrupt(url,cookie=''):
            status,h,raw=no_redirect_fetch(url,cookie)
            if cookie and 'file=atlas-custody.json' in url:
                raw=raw.replace(b'"map_pin_count": 0',b'"map_pin_count": 1')
            return status,h,raw
        with self.assertRaisesRegex(AdmissionError,'Export integrity'):
            admit(test_http.ApolloHttp.base, '/review','fv_test_mode=editor',allow_stub=True,fetch=corrupt)

    def test_14_missing_atlas_panel_rejected(self):
        def corrupt(url,cookie=''):
            status,h,raw=no_redirect_fetch(url,cookie)
            if 'x-fv-ex2-apollo-atlas-panel-sha256' in h:
                raw=raw.replace(b'id="fv-ex2-atlas-custody"',b'id="removed-panel"')
            return status,h,raw
        with self.assertRaisesRegex(AdmissionError,'six-record geography hold missing'):
            admit(test_http.ApolloHttp.base, '/review','fv_test_mode=editor',allow_stub=True,fetch=corrupt)

if __name__=='__main__':unittest.main()
