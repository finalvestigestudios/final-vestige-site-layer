"""R87 claim-to-institutional-source separation, including adversarial alterations."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1]/'tools/build_claim_boundary_r87.py'
spec = importlib.util.spec_from_file_location('r87_boundary', SCRIPT)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

class ClaimBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.desk = m.DESK.read_text('utf-8')
        cls.records = m.verify()

    def reject(self, corrupted):
        with self.assertRaises(ValueError):
            m.verify(desk_html=corrupted)

    def test_six_two_source_pairs(self):
        self.assertEqual(len(self.records), 6)
        for r in self.records:
            self.assertNotEqual(r['research_url'], r['photo_url'])
            self.assertEqual(r['research_url'], m.EXPECTED_RESEARCH[r['id']])
            self.assertTrue(m.official(r['research_url']))

    def test_swap_institutional_source_with_photo_rejected(self):
        self.reject(self.desk.replace(m.EXPECTED_RESEARCH['01'],
                                      self.records[0]['photo_url']))

    def test_swap_review_board_into_historical_01_rejected(self):
        self.reject(self.desk.replace(m.EXPECTED_RESEARCH['01'],
                                      m.EXPECTED_RESEARCH['02']))

    def test_non_nasa_lookalike_rejected(self):
        self.reject(self.desk.replace(m.EXPECTED_RESEARCH['02'],
                 'https://www.nasa.gov.evil.example/report/'))

    def test_injected_tracking_query_rejected(self):
        self.reject(self.desk.replace(m.EXPECTED_RESEARCH['01'],
                          m.EXPECTED_RESEARCH['01']+'?token=unsafe'))

    def test_removed_institutional_source_rejected(self):
        self.reject(self.desk.replace('Institutional research ↗</a>',
                                      'No original research</a>', 1))

    def test_additional_unreviewed_link_rejected(self):
        self.reject(self.desk.replace('Institutional research ↗</a>',
                    'Institutional research ↗</a><a href="https://www.nasa.gov/">More</a>', 1))

    def test_record_link_order_cannot_be_reversed(self):
        one = self.records[0]
        page = self.desk.replace(one['photo_url'], 'PLACEHOLDER', 1)
        page = page.replace(one['research_url'], one['photo_url'], 1)
        self.reject(page.replace('PLACEHOLDER', one['research_url'], 1))

    def test_ignition_claim_uncertainty_must_remain(self):
        self.reject(self.desk.replace('Probable is not proven.',
                                      'The ignition source was certain.'))

    def test_missing_limitation_rejected(self):
        self.reject(self.desk.replace('An unfueled launch vehicle did not mean a safe cabin.',
                                      ' '))

    def test_off_record_nasa_links_rejected(self):
        self.reject(self.desk.replace('Review the underlying finding</summary>',
                    'Review the underlying finding</summary><a href="https://www.nasa.gov/">Untracked</a>',1))

    def test_unreviewed_media_rejected(self):
        self.reject(self.desk.replace('Institutional research ↗</a>',
               'Institutional research ↗</a><picture><source srcset="x"></picture>', 1))

    def test_no_js_source_review_and_hold(self):
        page = m.render(self.records)
        self.assertNotIn('<script',page)
        self.assertNotIn('<img',page)
        self.assertNotIn('data-geo-edge',page)
        self.assertEqual(page.count('<article class="finding"'),6)
        self.assertEqual(page.count('<summary>'),6)
        self.assertEqual(page.count('class="source"'),12)
        self.assertIn('0 OF 6 IMAGE REUSE',page)
        self.assertIn('S67-19766',page)

    def test_deterministic_build(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            one,two=Path(a),Path(b)
            x,y=m.build(one),m.build(two)
            self.assertEqual(x,y)
            for name in ('R87_CLAIM_PHOTO_BOUNDARY.html','claim_boundary_r87.css','R87_RECEIPT.json'):
                self.assertEqual((one/name).read_bytes(),(two/name).read_bytes())
            self.assertEqual(x['image_reuse_cleared'],0)
            self.assertFalse(x['published'])

if __name__=='__main__': unittest.main()
