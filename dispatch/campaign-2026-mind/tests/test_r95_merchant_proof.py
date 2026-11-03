"""R95: adversarial offline verification of merchant-permission and claim-delta HOLD."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "r95-merchant-authorization"
SPEC = importlib.util.spec_from_file_location("r95", PACKAGE / "partner_proof.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
DATA = json.loads((PACKAGE / "merchant_evidence.json").read_text(encoding="utf-8"))

class ProofTests(unittest.TestCase):
    def test_actual_evidence_is_closed(self):
        o = MOD.inspect(copy.deepcopy(DATA))
        self.assertFalse(o["ready_to_send"])
        self.assertEqual([x["edition"] for x in o["editions"]], [3, 5])
        self.assertEqual(o["campaign"], "HOLD_UNSENT")

    def test_verification_gates_are_exactly_eleven(self):
        self.assertEqual(len(MOD.REQUIRED), 11)

    def test_each_missing_proof_stays_closed(self):
        for slot in (0, 1):
            for name in MOD.REQUIRED:
                d = copy.deepcopy(DATA)
                d["product_slots"][slot]["proofs"][name] = True
                with self.subTest(slot=slot, proof=name), self.assertRaises(MOD.EvidenceError):
                    MOD.inspect(d)

    def test_no_partial_pii_or_tracking(self):
        for name, value in (
            ("buyer_email", "a@example.org"), ("tracking_url", "https://seller.example/x"),
            ("subscriber_email", "a@example.org"), ("token", "secret")
        ):
            d = copy.deepcopy(DATA)
            d["product_slots"][0][name] = value
            with self.subTest(name=name), self.assertRaises(MOD.EvidenceError):
                MOD.inspect(d)

    def test_external_merchant_uri_not_approval(self):
        d = copy.deepcopy(DATA)
        d["product_slots"][0]["approval_state"] = "APPROVED"
        with self.assertRaises(MOD.EvidenceError):
            MOD.inspect(d)

    def test_coupon_or_url_not_activation(self):
        for item in ("https://zen12.com/hnp?affiliate=unknown", "https://affiliate.example/go"):
            d = copy.deepcopy(DATA)
            d["product_slots"][0]["affiliate_url"] = item
            with self.assertRaises(MOD.EvidenceError):
                MOD.inspect(d)

    def test_disguised_source_host_rejected(self):
        for url in (
            "http://zen12.com/hnp", "https://zen12.com.evil.test",
            "https://user@zen12.com/hnp", "https://zen12.com/hnp#tracking"
        ):
            d = copy.deepcopy(DATA)
            d["product_slots"][0]["merchant_sources"][0] = url
            with self.subTest(url=url), self.assertRaises(MOD.EvidenceError):
                MOD.inspect(d)

    def test_tampered_mix_rejected(self):
        d = copy.deepcopy(DATA)
        d["campaign_mix"]["commercial_reserved"] = [3, 4, 5]
        with self.assertRaises(MOD.EvidenceError):
            MOD.inspect(d)

    def test_fabricated_email_recipients_rejected(self):
        for n in (0, 2, 4, 100):
            d = copy.deepcopy(DATA)
            d["recipient_eligibility"] = n
            with self.subTest(n=n), self.assertRaises(MOD.EvidenceError):
                MOD.inspect(d)

    def test_conflict_cannot_be_marked_resolved(self):
        d = copy.deepcopy(DATA)
        d["product_slots"][1]["material_claim_conflicts"][0]["resolution"] = "PROVEN"
        with self.assertRaises(MOD.EvidenceError):
            MOD.inspect(d)

    def test_wrong_product_rejected(self):
        d = copy.deepcopy(DATA)
        d["product_slots"][0]["product_key"] = "brainwave-shots"
        with self.assertRaises(MOD.EvidenceError):
            MOD.inspect(d)

    def test_no_network_or_email_calls(self):
        source = (PACKAGE / "partner_proof.py").read_text(encoding="utf-8")
        for token in ("import requests", "import smtplib", "urllib.request", "subprocess", "send_mail(", "post("):
            self.assertNotIn(token, source)

if __name__ == "__main__":
    unittest.main()
