"""Native offline tests: fail closed when counts or consent are inferred."""
import unittest
from decimal import Decimal
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from eligibility_guard import diagnose_counts, confirmed_signup, release_state, realized_revenue_per_1000

COUNTERS={"subscribers":{"total":3,"confirmed":3,"unconfirmed":2,"suppressed":0}}
FOLLOWERS={"total":3,"email":0,"wpcom":3,"comment":0,"publicize":{},"partial":False}
EVENT={"provider":"Jetpack","authenticated_provider":True,"current_email_status":"Subscribed",
       "previous_email_status":"Not confirmed","is_first_verified_transition":True,
       "deduplicated":True,"consent_for_dispatch":True,
       "attribution_evidence":"first_party_verified_source", "opaque_transition_id":"ab23ac1234227a8f"}
PAID={"independently_verified_paid":True,"settled":True,"attributed_qualified_session":True,
      "gross":"30.00","refunds":"0.00","fees":"2.40",
      "currency":"USD","report_authoritative":True,"opaque_order_ref":"order_0001",
      "partner_settlement_report_ref":"settled_batch_00001"}
class CountTests(unittest.TestCase):
    def test_nonadditive(self):
        x=diagnose_counts(COUNTERS,FOLLOWERS)
        self.assertEqual(x["confirmed_counter"],3)
        self.assertEqual(x["unconfirmed_requests_separate"],2)
        self.assertIsNone(x["eligible_email_recipients"])
        self.assertIsNone(x["attributed_confirmed_signups"])
    def test_zero_email_only_not_zero_recipients(self):
        self.assertIsNone(diagnose_counts(COUNTERS,FOLLOWERS)["eligible_email_recipients"])
    def test_boolean_counter_rejected(self):
        self.assertEqual(diagnose_counts({"subscribers":{**COUNTERS["subscribers"],"total":True}},FOLLOWERS)["status"],"UNVERIFIABLE_PROVIDER_COUNTERS")
    def test_conflicting_counts_rejected(self):
        self.assertEqual(diagnose_counts({"subscribers":{**COUNTERS["subscribers"],"total":2}},FOLLOWERS)["status"],"INCONSISTENT_PROVIDER_COUNTERS")
    def test_partial_status_rejected(self):
        self.assertEqual(diagnose_counts(COUNTERS,{**FOLLOWERS,"partial":True})["status"],"PARTIAL_FOLLOWER_COUNTERS")
class SignupTests(unittest.TestCase):
    def test_clean_synthetic_event_is_structurally_valid(self):
        self.assertTrue(confirmed_signup(EVENT)) # NOT proof a real subscriber exists
    def test_attempt_only(self):self.assertFalse(confirmed_signup({**EVENT,"authenticated_provider":False}))
    def test_reader_only(self):self.assertFalse(confirmed_signup({**EVENT,"current_email_status":"Not subscribed"}))
    def test_bounced(self):self.assertFalse(confirmed_signup({**EVENT,"current_email_status":"Bounced"}))
    def test_duplicate(self):self.assertFalse(confirmed_signup({**EVENT,"deduplicated":False}))
    def test_no_prior_transition(self):self.assertFalse(confirmed_signup({**EVENT,"previous_email_status":"Subscribed"}))
    def test_no_first_transition(self):self.assertFalse(confirmed_signup({**EVENT,"is_first_verified_transition":False}))
    def test_no_consent(self):self.assertFalse(confirmed_signup({**EVENT,"consent_for_dispatch":False}))
    def test_unlinked_utm(self):self.assertFalse(confirmed_signup({**EVENT,"attribution_evidence":"utm_only"}))
    def test_pii_fields_blocked(self):self.assertFalse(confirmed_signup({**EVENT,"email":"demo@example.org"}))
    def test_camelcase_email_key_blocked(self):self.assertFalse(confirmed_signup({**EVENT,"emailAddress":"demo@example.org"}))
    def test_pii_in_token_blocked(self):self.assertFalse(confirmed_signup({**EVENT,"opaque_transition_id":"test@example.com"}))
class ReleaseTests(unittest.TestCase):
    def test_every_issue_held(self):
        self.assertTrue(all(release_state(i,{})["status"]=="HOLD_UNSENT" for i in range(1,7)))
    def test_merchant_hold_only_3_5(self):
        self.assertEqual([i for i in range(1,7) if release_state(i,{})["merchant_status"]=="HOLD_MERCHANT"],[3,5])
    def test_fake_boolean_does_not_count(self):
        self.assertIn("working_received_unsubscribe",release_state(1,{"working_received_unsubscribe":True})["missing_proof"])
    def test_all_synthetic_proofs_cannot_send(self):
        req=release_state(3,{})["missing_proof"]
        proofs={z:True for z in req}|{z+"_evidence_ref":"synthetic" for z in req}
        self.assertFalse(release_state(3,proofs)["send_authorized_by_code"])
    def test_invalid_edition(self):
        with self.assertRaises(ValueError):release_state(7,{})
class MoneyTests(unittest.TestCase):
    def test_unknown_denominator(self):self.assertIsNone(realized_revenue_per_1000(None,[PAID]))
    def test_click_not_sale(self):self.assertIsNone(realized_revenue_per_1000(100,[{**PAID,"independently_verified_paid":False}]))
    def test_no_settlements(self):self.assertIsNone(realized_revenue_per_1000(100,[]))
    def test_refunds_subtracted(self):self.assertEqual(realized_revenue_per_1000(100,[{**PAID,"refunds":"5.00"}]),Decimal("226.00"))
    def test_negative_net_allowed(self):self.assertEqual(realized_revenue_per_1000(100,[{**PAID,"refunds":"35.00"}]),Decimal("-74.00"))
    def test_duplicate_order_double_count_blocked(self):self.assertIsNone(realized_revenue_per_1000(100,[PAID,PAID]))
    def test_no_settlement_report(self):self.assertIsNone(realized_revenue_per_1000(100,[{**PAID,"report_authoritative":False}]))
    def test_no_order_ref(self):self.assertIsNone(realized_revenue_per_1000(100,[{**PAID,"opaque_order_ref":""}]))
    def test_unsupported_currency(self):self.assertIsNone(realized_revenue_per_1000(100,[{**PAID,"currency":"EUR"}]))
    def test_nan_rejected(self):self.assertIsNone(realized_revenue_per_1000(100,[{**PAID,"gross":"NaN"}]))
if __name__=="__main__":unittest.main()
