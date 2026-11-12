import json
import unittest
from pathlib import Path
from release_gate import EDITORIAL, MERCHANT, SHARED, MERCHANT_FIELDS, edition_gate, confirmed_signup, qualified_revenue_rate, static_subject_audit

class ReleaseGateTests(unittest.TestCase):
    def test_mix(self):
        self.assertEqual((len(EDITORIAL), len(MERCHANT)), (4, 2))
    def test_all_are_unsent(self):
        for i in range(1, 7):
            with self.subTest(i=i):
                self.assertFalse(edition_gate(i)["send_authorized"])
                self.assertEqual(edition_gate(i)["status"], "HOLD_UNSENT")
    def test_missing_shared(self):
        self.assertEqual(len(edition_gate(1)["missing"]), len(SHARED))
    def test_missing_merchant(self):
        self.assertEqual(len(edition_gate(3)["missing"]), len(SHARED) + len(MERCHANT_FIELDS))
    def test_merchant_isolation(self):
        proof = {x: True for x in SHARED}
        self.assertTrue(edition_gate(2, proof)["human_review_only"])
        self.assertFalse(edition_gate(3, proof)["human_review_only"])
    def test_all_true_still_no_send(self):
        proof = {x: True for x in SHARED + MERCHANT_FIELDS}
        self.assertTrue(edition_gate(3, proof)["human_review_only"])
        self.assertFalse(edition_gate(3, proof)["send_authorized"])
    def test_nonboolean_attestations(self):
        self.assertIn(SHARED[0], edition_gate(1, {SHARED[0]: "yes"})["missing"])
    def test_unknown_edition(self):
        with self.assertRaises(ValueError): edition_gate(7)
    def test_query_param_is_not_signup(self):
        self.assertFalse(confirmed_signup({"subscribe":"success"}))
    def test_reader_only_not_signup(self):
        self.assertFalse(confirmed_signup({"source":"authenticated_provider", "new_email_status":"reader"}))
    def test_synthetic_transition(self):
        p = {"source":"authenticated_provider", "confirmation_attested":True, "prior_email_status":"pending",
             "new_email_status":"subscribed", "opaque_provider_key":"synthetic-key-123", "deduplicated":True, "opted_out":False}
        self.assertTrue(confirmed_signup(p))
        for field, value in [("prior_email_status", "subscribed"),("new_email_status", "paused"),
                             ("confirmation_attested",False),("deduplicated",False),("opted_out",True),
                             ("opaque_provider_key","test@example.com")]:
            with self.subTest(field=field):
                self.assertFalse(confirmed_signup({**p,field:value}))
    def test_no_money_data(self):
        self.assertEqual(qualified_revenue_rate(50,[])["status"], "NOT_COMPUTABLE")
        self.assertEqual(qualified_revenue_rate(None,[])["status"], "NOT_COMPUTABLE")
        self.assertEqual(qualified_revenue_rate(0,[])["status"], "NOT_COMPUTABLE")
    def test_inferred_click_is_not_order(self):
        self.assertEqual(qualified_revenue_rate(10,[{"click":True}])["status"], "NOT_COMPUTABLE")
    def test_synthetic_revenue(self):
        row={"settled":True,"source_verified":True,"opaque_order_id":"synthetic-order-01","gross":"30.00","refunds":"5.00","fees":"2.00","currency":"USD"}
        out=qualified_revenue_rate(100,[row])
        self.assertEqual(out["rate"],"230.00")
        self.assertEqual(qualified_revenue_rate(100,[row,row])["status"],"NOT_COMPUTABLE")
        for k,val in [("settled",False),("source_verified",False),("fees",None),("currency","EUR"),("refunds","31.00"),("gross","NaN")]:
            with self.subTest(k=k):
                self.assertEqual(qualified_revenue_rate(100,[{**row,k:val}])["status"],"NOT_COMPUTABLE")
    def test_manifest_flags(self):
        manifest_path=Path(__file__).parents[2]/"master"/"dispatch"/"campaign-2026-mind"/"manifest.json"
        if not manifest_path.exists():
            self.skipTest("Canonical manifest not provided; fixture test below always runs")
        flags=static_subject_audit(json.loads(manifest_path.read_text()))
        self.assertIn("DUPLICATE_EDITORIAL_DESTINATION",flags["1"])
        self.assertIn("DUPLICATE_EDITORIAL_DESTINATION",flags["2"])
        self.assertIn("NASA_TIMING_CLAIM_REVIEW",flags["4"])
        self.assertIn("RETURNING_SUBSCRIBER_REOPTIN_RISK",flags["6"])
    def test_fixture_flags(self):
        f={"issues":[{"number":1,"editorial_cta":"https://a.org","subject":"A"},
                     {"number":2,"editorial_cta":"https://a.org","subject":"B"},
                     {"number":3,"editorial_cta":"[[PENDING]]","subject":"C"},
                     {"number":4,"editorial_cta":"https://b.org","subject":"Fourteen seconds. A much longer explanation."},
                     {"number":6,"editorial_cta":"https://finalvestige.com/focus/","subject":"E"}]}
        a=static_subject_audit(f)
        self.assertIn("DUPLICATE_EDITORIAL_DESTINATION",a["1"])
        self.assertIn("PENDING_CTA_INERT",a["3"])
        self.assertIn("NASA_TIMING_CLAIM_REVIEW",a["4"])
        self.assertIn("RETURNING_SUBSCRIBER_REOPTIN_RISK",a["6"])

if __name__ == "__main__": unittest.main()
