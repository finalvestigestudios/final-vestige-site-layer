#!/usr/bin/env python3
"""Adversarial tests using real inherited R415 PHP-rendered HTML, no invented payments."""
import copy
import unittest
from journey_acceptance import (render_fixture,inspect_markup,review_campaign,
                                review_commerce,release_gate,FREE,BOARD,ARCHIVES)

HTML=render_fixture()

def bad(old,new):
    assert old in HTML,old
    return inspect_markup(HTML.replace(old,new,1))

class SourceAndOfferTests(unittest.TestCase):
    def test_original_markup(self): self.assertEqual(inspect_markup(HTML)['status'],'PASS')
    def test_fatal_source_swap(self): self.assertEqual(bad(BOARD,'https://www.nasa.gov/other/')['status'],'FAIL')
    def test_false_ignition_certainty(self):
        self.assertEqual(bad('did not conclusively identify its ignition initiator','identified an electrical wire as the ignition initiator')['status'],'FAIL')
    def test_later_tests_not_original_fire(self):
        self.assertEqual(bad('102 separate, later deliberate ignitions','102 deliberate January 1967 reconstructions')['status'],'FAIL')
    def test_replaced_archive_link(self): self.assertEqual(bad(ARCHIVES[0],ARCHIVES[1])['status'],'FAIL')
    def test_broken_evidence_fragment(self): self.assertEqual(bad('href="#fv-r414-gallery-1-05"','href="#invented"')['status'],'FAIL')
    def test_invented_geopins(self): self.assertEqual(bad('<section class="fv-r415"','<section data-lat="28" class="fv-r415"')['status'],'FAIL')
    def test_paid_cross_sell(self):
        self.assertEqual(bad('</body>','<a href="https://payhip.com/b/unverified">BUY NOW</a></body>')['status'],'FAIL')
    def test_unsafe_script(self): self.assertEqual(bad('</body>','<script src="evil.js"></script></body>')['status'],'FAIL')
    def test_unauthorized_form(self): self.assertEqual(bad('</body>','<form action="/subscribe"><input></form></body>')['status'],'FAIL')
    def test_removed_disclaimer(self):
        self.assertEqual(bad('NASA has not approved or endorsed','NASA approves and endorses')['status'],'FAIL')
    def test_duplicate_id(self):
        self.assertEqual(bad('</body>','<p id="fv-r415-1-heading"></p></body>')['status'],'FAIL')
    def test_uncleared_cta(self): self.assertEqual(bad(FREE,'https://payhip.com/b/unknown')['status'],'FAIL')
    def test_nasa_lookalike(self):
        self.assertEqual(bad(ARCHIVES[0],'https://www.nasa.gov.evil.example/')['status'],'FAIL')
    def test_http_insecure(self):
        self.assertEqual(bad(ARCHIVES[0],ARCHIVES[0].replace('https:','http:'))['status'],'FAIL')
    def test_no_creator_post(self):
        self.assertEqual(review_campaign({})['state'],'HOLD')
    def test_no_paid_offer(self):
        r=review_commerce({});self.assertEqual(r['state'],'HOLD');self.assertIsNone(r['confirmed_orders'])
    def test_campaign_syntax_is_not_verified_attribution(self):
        asset='existing-creator-id'
        q='?utm_source=youtube&utm_medium=organic_social&utm_campaign=apollo_case_2026_11&utm_content='+asset
        p={'asset_id':asset,'platform':'youtube','post_url':'https://youtube.com/watch?v=abc',
           'landing_url':FREE+q,'source_review_url':'https://docs.google.com/document/d/review'}
        r=review_campaign(p)
        self.assertEqual(r['state'],'HOLD' if not r.get('publisher_verified',False) and r['state']=='HOLD' else 'REVIEW_REQUIRED')
        self.assertFalse(r.get('publisher_verified',False))
    def test_campaign_wrong_asset_id(self):
        p={'asset_id':'A','platform':'youtube','post_url':'https://youtube.com/watch?v=abc',
           'landing_url':FREE+'?utm_source=youtube&utm_medium=organic_social&utm_campaign=apollo_2026&utm_content=OTHER',
           'source_review_url':'https://docs.google.com/document/d/review'}
        self.assertEqual(review_campaign(p)['state'],'HOLD')
    def test_spoofed_merchant_report_never_becomes_paid_order(self):
        p=dict.fromkeys(('sku','seller_legal_name','sale_url','rights_manifest',
                         'fulfillment_proof','refund_terms','merchant_report_url','independent_review'),'fabricated')
        r=review_commerce(p)
        self.assertIsNone(r['net_revenue_per_1000_qualified_sessions'])
        self.assertNotEqual(r['state'],'VERIFIED')
    def test_no_self_attested_release_pass(self):
        r=release_gate(inspect_markup(HTML),{'state':'FIXTURE_PASS','runtime':'offline'},
                       {'founder':'yes','axe':'yes','merchant':'yes'})
        self.assertEqual(r['decision'],'HARD_HOLD')
        self.assertEqual(r['commercial_metrics'],'NOT_COMPUTABLE')

if __name__=='__main__':unittest.main(verbosity=2)
