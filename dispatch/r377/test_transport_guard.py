"""Native offline tests; no external calls, no emails, no account changes."""
import copy
import json
import unittest
from pathlib import Path
from transport_guard import (
    BASE_GATES, COMMERCIAL_GATES, evaluate_issue, reconcile_subscribers,
    revenue_per_1000, validate_manifest, dossier)
M=Path(__file__).resolve().parents[1]/"campaign-2026-mind/manifest.json"
DATA=json.loads(M.read_text())
class SourceAndReleaseTests(unittest.TestCase):
    def test_six_originals(self): self.assertTrue(validate_manifest(DATA))
    def test_all_six_hold(self): self.assertTrue(all(x['decision']=='HOLD_UNSENT' for x in dossier(DATA)['issue_decisions']))
    def test_all_six_cannot_send(self): self.assertTrue(all(not x['send_authorized'] for x in dossier(DATA)['issue_decisions']))
    def test_commercial_rights_extra(self):
        x=dossier(DATA)['issue_decisions']; self.assertTrue(len(x[2]['release_proofs_missing'])>len(x[0]['release_proofs_missing']))
    def test_offer_ctas_deliberately_blocked(self):
        x=dossier(DATA)['issue_decisions']; self.assertIn('verified_first_party_cta',x[2]['release_proofs_missing']); self.assertIn('verified_first_party_cta',x[4]['release_proofs_missing'])
    def test_disclosure_not_approval(self):
        self.assertIn('specific_sku_email_channel_permission_verified',evaluate_issue(DATA['issues'][2])['release_proofs_missing'])
    def test_forged_proof_string_fails(self):
        self.assertIn('native_jetpack_preview_captured',evaluate_issue(DATA['issues'][0],{'native_jetpack_preview_captured':'yes'})['release_proofs_missing'])
    def test_all_true_evidence_never_grants_send(self):
        p={k:True for k in BASE_GATES+COMMERCIAL_GATES}; self.assertFalse(evaluate_issue(DATA['issues'][0],p)['send_authorized'])
    def test_auto_post_setting_is_not_release_approval(self):
        p={'email_new_posts_by_default':False,'site_can_send':True}; self.assertFalse(evaluate_issue(DATA['issues'][0],p)['send_authorized'])
    def test_subject_is_draft_only(self): self.assertTrue(evaluate_issue(DATA['issues'][0])['subject_is_proposed_post_title_not_verified_rendered_email'])
    def test_preheader_not_native_verified(self): self.assertTrue(evaluate_issue(DATA['issues'][0])['preheader_is_draft_metadata_not_verified_jetpack_control'])
    def test_wrong_mix_rejected(self):
        d=copy.deepcopy(DATA); d['issues'][2]['kind']='editorial'
        with self.assertRaises(ValueError): validate_manifest(d)
    def test_extra_edition_rejected(self):
        d=copy.deepcopy(DATA); d['issues'].append(dict(d['issues'][0]))
        with self.assertRaises(ValueError): validate_manifest(d)
    def test_merchant_url_rejected(self):
        d=copy.deepcopy(DATA['issues'][2]); d['merchant_affiliate_url']='https://example.org'
        self.assertIn('merchant_url_not_allowed_in_draft',evaluate_issue(d)['release_proofs_missing'])
    def test_unknown_kind_rejected(self):
        d=copy.deepcopy(DATA['issues'][0]); d['kind']='evergreen'
        with self.assertRaises(ValueError): evaluate_issue(d)
    def test_approved_cta_does_not_bypass_legal(self):
        self.assertIn('final_vestige_postal_address_verified_in_render',evaluate_issue(DATA['issues'][0])['release_proofs_missing'])
    def test_publish_state_must_hold(self):
        d=copy.deepcopy(DATA['issues'][0]); d['publish_state']='publish'
        self.assertIn('source_must_remain_held',evaluate_issue(d)['release_proofs_missing'])
    def test_3_3_2_not_five(self):
        d=reconcile_subscribers(3,3,2,3,0)
        self.assertEqual(d['relationship'],'not_inherently_contradictory_unconfirmed_excluded')
        self.assertIsNone(d['unique_email_eligible_inboxes'])
    def test_reader_follower_not_email_signup(self):
        self.assertIsNone(reconcile_subscribers(3,3,2,3,0)['confirmed_signup_events'])
    def test_bad_counts_rejected(self):
        with self.assertRaises(ValueError): reconcile_subscribers(3,-1,2,3,0)
    def test_click_not_paid_conversion(self): self.assertIsNone(revenue_per_1000(sessions=100,session_evidence='qualified_human_audited',partner_orders=[{'evidence':'click','gross':99,'refunds':0,'fees':0}],costs_verified=True))
    def test_missing_denominator(self): self.assertIsNone(revenue_per_1000(sessions=None,session_evidence='qualified_human_audited',partner_orders=[],costs_verified=True))
    def test_missing_orders_not_zero(self): self.assertIsNone(revenue_per_1000(sessions=100,session_evidence='qualified_human_audited',partner_orders=[],costs_verified=True))
    def test_missing_fees(self): self.assertIsNone(revenue_per_1000(sessions=100,session_evidence='qualified_human_audited',partner_orders=[{'evidence':'partner_settled','gross':50,'refunds':0}],costs_verified=True))
    def test_synthetic_financial_math(self):
        v=revenue_per_1000(sessions=200,session_evidence='qualified_human_audited',partner_orders=[{'evidence':'partner_settled','gross':60,'refunds':15,'fees':5}],costs_verified=True)
        self.assertEqual(v['net_revenue_per_1000'],200.0);self.assertTrue(v['small_sample_warning'])
    def test_fake_follower_denominator(self):self.assertIsNone(revenue_per_1000(sessions=200,session_evidence='wpcom_followers',partner_orders=[],costs_verified=True))
    def test_no_unverified_vendor_link(self):
        self.assertTrue(all(i['merchant_affiliate_url'] is None for i in DATA['issues']))
    def test_root_review_only(self): self.assertEqual(dossier(DATA)['mode'],'REVIEW_ONLY_NEVER_SEND')
if __name__=='__main__': unittest.main()
