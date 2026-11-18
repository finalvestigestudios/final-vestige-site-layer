import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('g',Path(__file__).parent/'atlas_gate.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

BASE='''<main><h1>The Hatch Opened Inward</h1><p>NASA Review Board examined the fire.</p>
<p>The hatch opened inward. No single ignition source was conclusively identified.
The most probable initiator was an electrical arc. Evidence boundary: probable is not proven.</p>
<a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">NASA report</a>
<a href="https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/">Later testing</a>
<a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the investigation</a>
<img src="placeholder.jpg" alt="Context-only illustration"></main>'''

class Audit(unittest.TestCase):
    def report(self, html, origin='synthetic_test'):return g.audit(html,origin)
    def test_control_pass(self):self.assertEqual(self.report(BASE)['status'],'PASS_SOURCE_SNAPSHOT')
    def test_live_review_placeholder_blocked(self):
        x=self.report(BASE+'<p>Atlas review status: Not yet reviewed.</p>')
        self.assertEqual(x['status'],'HOLD_REVIEW');self.assertEqual(x['unresolved_review_labels'],1)
    def test_two_live_placeholders_blocked(self):
        x=self.report(BASE+'<p>Atlas review status: Not yet reviewed.</p>'*2)
        self.assertEqual(x['unresolved_review_labels'],2)
    def test_missing_primary_source(self):self.assertFalse(self.report(BASE.replace(g.BOARD,'https://example.org'))['checks']['nasa_board_source_link'])
    def test_missing_later_testing(self):self.assertFalse(self.report(BASE.replace(g.TESTS,'https://example.org'))['checks']['nasa_followup_research_link'])
    def test_no_cta(self):self.assertFalse(self.report(BASE.replace(g.INVESTIGATION,'/'))['checks']['full_free_investigation_link'])
    def test_payment_rejected(self):self.assertFalse(self.report(BASE+'<a href="https://payhip.com/a">Pay now</a>')['checks']['no_unauthorized_payment_destinations'])
    def test_geo_claim_rejected(self):self.assertFalse(self.report(BASE+'<i data-lat="28.5"></i>')['checks']['no_unverified_geo_markers'])
    def test_duplicate_ids_rejected(self):self.assertFalse(self.report(BASE+'<b id="a"></b><b id="a"></b>')['checks']['unique_dom_ids'])
    def test_missing_alt_rejected(self):self.assertFalse(self.report(BASE+'<img src="a.jpg">')['checks']['image_alt_attribute_present'])
    def test_source_and_claim_evidence_required(self):self.assertFalse(self.report(BASE.replace('most probable','definite'))['checks']['chronological_claims_and_limits_present'])
    def test_provenance_required(self):
        with self.assertRaises(ValueError):self.report(BASE,'')
    def test_staging_without_actual_markers_fails(self):
        x=self.report(BASE,'approved_staging_snapshot');self.assertFalse(x['checks']['five_staging_source_cards']);self.assertFalse(x['checks']['one_original_educator_preview'])
    def test_staging_cards_pass_with_one_preview(self):
        x=self.report(BASE+'<div data-r438-card></div>'*5+'<section data-r440-root></section>','approved_staging_snapshot')
        self.assertEqual(x['status'],'PASS_SOURCE_SNAPSHOT')
    def test_staging_multiple_ctas_fail(self):
        x=self.report(BASE+f'<a href="{g.INVESTIGATION}">Again</a>'+'<div data-r438-card></div>'*5+'<section data-r440-root></section>','approved_staging_snapshot')
        self.assertFalse(x['checks']['exactly_one_stage_investigation_cta'])
    def test_http_nasa_links_fail(self):
        self.assertFalse(self.report(BASE+'<a href="http://www.nasa.gov/extra">source</a>')['checks']['no_http_nasa_link'])

if __name__=='__main__':unittest.main(verbosity=2)
