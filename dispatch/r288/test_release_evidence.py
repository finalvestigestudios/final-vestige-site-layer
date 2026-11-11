"""Native Python tests, synthetic fixtures only; no subscriber data or network."""
import copy
import json
import unittest
from pathlib import Path
from release_evidence import (EXPECTED_ORIGINAL_BLOBS, MERCHANT_NUMBERS,
    confirmed_signup_from_event, git_blob_sha, realized_net_per_1000,
    release_decisions, validate_original_files)

HERE=Path(__file__).resolve().parent
S=HERE.parent/'campaign-2026-mind'
MANIFEST=json.loads((S/'manifest.json').read_text(encoding='utf-8'))
EVIDENCE=json.loads((HERE/'evidence_snapshot.json').read_text(encoding='utf-8'))

class SourceTest(unittest.TestCase):
    def test_eight_original_blob_hashes_match_actual_github(self):
        res=validate_original_files(S)
        self.assertEqual(res['files_checked'],8)
        self.assertTrue(res['byte_identical'],res['mismatches'])
    def test_sha_implementation_uses_git_object_header(self):
        self.assertEqual(git_blob_sha(b'test content\n'),'d670460b4b4aece5915caf5c68d12f560a9fe3e4')
    def test_original_release_gates_are_all_hold(self):
        rows=release_decisions(MANIFEST,EVIDENCE)
        self.assertFalse(rows['send_authorized'])
        self.assertFalse(rows['scheduled'])
        self.assertEqual([r['status'] for r in rows['issues']], ['HOLD_UNSENT']*6)
    def test_all_merchant_permissions_unknown_not_inferred(self):
        rows=release_decisions(MANIFEST,EVIDENCE)
        self.assertEqual(MERCHANT_NUMBERS,{3,5})
        for r in rows['issues']:
            if r['issue'] in MERCHANT_NUMBERS:
                self.assertIn('merchant_email_channel_permitted',r['blockers'])
                self.assertIn('inactive_buyer_guide_placeholder',r['blockers'])
    def test_editorial_copy_dangers_are_not_silenced(self):
        rows=release_decisions(MANIFEST,EVIDENCE)['issues']
        self.assertIn('apollo_14_second_interval_unexplained',rows[3]['blockers'])
        self.assertIn('duplicate_puysegur_destination_review_pending',rows[0]['blockers'])
        self.assertIn('duplicate_puysegur_destination_review_pending',rows[1]['blockers'])
        self.assertIn('fieldbook_already_in_welcome',rows[5]['blockers'])
    def test_all_synthetic_global_approvals_cannot_clear_original_merchant_tokens(self):
        e=copy.deepcopy(EVIDENCE)
        e['global']={k:True for k in e['global']}
        for k in ('03','05'):
            e['issues'][k]={p:True for p in e['issues'][k]}
        rows=release_decisions(MANIFEST,e)['issues']
        self.assertEqual(rows[2]['status'],'HOLD_UNSENT')
        self.assertEqual(rows[4]['status'],'HOLD_UNSENT')
    def test_manifest_wrong_split_rejected(self):
        m=copy.deepcopy(MANIFEST)
        m['issues'][2]['kind']='editorial'
        with self.assertRaises(ValueError): release_decisions(m,EVIDENCE)
    def test_manifest_earning_link_injection_rejected(self):
        m=copy.deepcopy(MANIFEST)
        m['issues'][2]['merchant_affiliate_url']='https://not-approved.example'
        with self.assertRaises(ValueError): release_decisions(m,EVIDENCE)
    def test_manifest_schedule_tampering_keeps_hold(self):
        m=copy.deepcopy(MANIFEST)
        m['issues'][0]['publish_state']='publish'
        row=release_decisions(m,EVIDENCE)['issues'][0]
        self.assertIn('source_manifest_must_remain_hold',row['blockers'])

class LeadTest(unittest.TestCase):
    def setUp(self):
        self.ok={'source':'authenticated_subscription_provider',
          'provider_state':'confirmed_email_eligible','user_marketing_consent':True,
          'is_suppressed':False,'dedupe_confirmation_event_id':'synthetic-01'}
    def test_valid_synthetic_confirmed_event(self):
        self.assertTrue(confirmed_signup_from_event(self.ok))
    def test_url_param_not_proof(self):
        e=dict(self.ok,source='focus_url_subscribe_query')
        self.assertFalse(confirmed_signup_from_event(e))
    def test_pdf_download_not_proof(self):
        self.assertFalse(confirmed_signup_from_event(dict(self.ok,source='pdf_click')))
    def test_suppressed_not_a_lead(self):
        self.assertFalse(confirmed_signup_from_event(dict(self.ok,is_suppressed=True)))
    def test_unconfirmed_not_a_lead(self):
        self.assertFalse(confirmed_signup_from_event(dict(self.ok,provider_state='requested')))
    def test_missing_provider_dedupe_key_not_a_lead(self):
        self.assertFalse(confirmed_signup_from_event(dict(self.ok,dedupe_confirmation_event_id='')))

class RevenueTest(unittest.TestCase):
    def setUp(self):
        self.ok={'orders_independently_settled':True,'qualified_sessions_verified':True,
          'qualified_human_sessions':1000,'gross_settled_usd':100,'refunded_usd':10,'fees_usd':20}
    def test_synthetic_net_per_thousand(self):
        self.assertEqual(realized_net_per_1000(self.ok),70.0)
    def test_clicks_not_orders(self):
        self.assertIsNone(realized_net_per_1000(dict(self.ok,orders_independently_settled=False)))
    def test_pageviews_not_qualified_session_proof(self):
        self.assertIsNone(realized_net_per_1000(dict(self.ok,qualified_sessions_verified=False)))
    def test_null_settlement_not_zero(self):
        self.assertIsNone(realized_net_per_1000(dict(self.ok,gross_settled_usd=None)))
    def test_zero_denominator_not_computable(self):
        self.assertIsNone(realized_net_per_1000(dict(self.ok,qualified_human_sessions=0)))
    def test_negative_financial_record_invalid(self):
        self.assertIsNone(realized_net_per_1000(dict(self.ok,refunded_usd=-2)))
    def test_excess_refunds_invalid(self):
        self.assertIsNone(realized_net_per_1000(dict(self.ok,refunded_usd=1000)))

if __name__=='__main__': unittest.main()
