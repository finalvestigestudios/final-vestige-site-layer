import copy
import unittest
from release_audit import EXPECTED, COMMON_GATES, MERCHANT_GATES, audit


def proof(status="verified"):
    return {"status": status, "source": "synthetic fixture", "verified_at": "2026-11-10", "reviewer": "test-only"}


def fixture(fill=True):
    return {"release_policy": "NO_SEND_NO_PUBLICATION", "issues": [
        {"number": n, "kind": kind, "send_authorized": False,
         "evidence": {k: proof() for k in (COMMON_GATES + (MERCHANT_GATES if n in (3,5) else ()))} if fill else {}}
        for n, kind in EXPECTED.items()]}

class ReleaseAuditTests(unittest.TestCase):
    def test_all_unsupported_holds(self):
        d = fixture(False); r = audit(d)
        self.assertEqual(r['status'], 'HOLD')
        self.assertEqual(len(r['blockers']['3']), len(COMMON_GATES)+len(MERCHANT_GATES))
    def test_synthetic_full_remains_not_send_authority(self):
        r = audit(fixture()); self.assertEqual(r['status'], 'FOUNDER_REVIEW_CANDIDATE_ONLY_NOT_SEND_AUTHORIZATION')
        self.assertFalse(r['send_authorized'])
    def test_editorial_also_requires_postal(self):
        d=fixture();del d['issues'][0]['evidence']['final_vestige_postal_address_in_received_message']
        self.assertIn('final_vestige_postal_address_in_received_message',audit(d)['blockers']['1'])
    def test_no_reply_cannot_replace_unsubscribe(self):
        d=fixture();del d['issues'][0]['evidence']['unsubscribe_function_verified']
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_commercial_needs_email_permission(self):
        d=fixture();d['issues'][2]['evidence']['permission_to_promote_by_email']=proof('not_verified')
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_commercial_needs_offer_link(self):
        d=fixture();del d['issues'][4]['evidence']['merchant_issued_earning_url']
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_sender_physical_address_not_general_vendor_address(self):
        d=fixture();d['issues'][2]['evidence']['final_vestige_postal_address_in_received_message']=proof('blocked')
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_missing_recipient_count(self):
        d=fixture();d['issues'][1]['evidence']['eligible_recipients_provider_verified']=proof('not_verified')
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_unverified_preheader(self):
        d=fixture();del d['issues'][5]['evidence']['actual_received_render_review']
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_unapproved_guide(self):
        d=fixture();del d['issues'][2]['evidence']['approved_first_party_buyer_guide_live']
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_exact_six(self):
        d=fixture();d['issues'].pop();self.assertEqual(audit(d)['status'],'HOLD')
    def test_duplicate_issue(self):
        d=fixture();d['issues'][5]['number']=1;self.assertEqual(audit(d)['status'],'HOLD')
    def test_changed_commercial_mix(self):
        d=fixture();d['issues'][0]['kind']='commercial';self.assertEqual(audit(d)['status'],'HOLD')
    def test_false_evidence_boolean_not_accepted(self):
        d=fixture();d['issues'][0]['evidence']['genuine_jetpack_preview']=True
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_missing_provenance_fails(self):
        d=fixture();d['issues'][0]['evidence']['genuine_jetpack_preview']={'status':'verified'}
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_unknown_email_scope_not_same_as_wpcom_followers(self):
        d=fixture();del d['issues'][0]['evidence']['eligible_recipients_provider_verified']
        d['subscriber_summary']={'wpcom_followers':3, 'email_followers':0}
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_no_unapproved_send_flag(self):
        d=fixture();d['issues'][3]['send_authorized']=True
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_no_raw_recipient_evidence(self):
        d=fixture();d['issues'][0]['actual_received_evidence']='private raw email'
        self.assertEqual(audit(d)['status'],'HOLD')
    def test_no_send_policy_explicit(self):
        d=fixture();d['release_policy']='SEND';self.assertEqual(audit(d)['status'],'HOLD')
    def test_merchant_terms_all_required(self):
        for gate in MERCHANT_GATES:
            with self.subTest(gate=gate):
                d=fixture();del d['issues'][2]['evidence'][gate]
                self.assertEqual(audit(d)['status'],'HOLD')
    def test_legal_gates_all_required_on_editorial(self):
        for gate in COMMON_GATES:
            with self.subTest(gate=gate):
                d=fixture();del d['issues'][0]['evidence'][gate]
                self.assertEqual(audit(d)['status'],'HOLD')

if __name__ == '__main__':
    unittest.main()
