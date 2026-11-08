"""R93 production-proof triage: no marketing side effects or subscriber data."""
import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("triage", ROOT / "triage.py")
triage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(triage)

class TriageTests(unittest.TestCase):
    def setUp(self):
        self.doc = triage.load()

    def bad(self, func):
        d = copy.deepcopy(self.doc)
        func(d)
        with self.assertRaises(triage.InvalidProof):
            triage.review(d)

    def test_initial_review(self):
        result = triage.review(self.doc)
        self.assertEqual("HOLD_UNSENT", result["status"])
        self.assertEqual("HOLD_MERCHANT", result["commercial_status"])
        self.assertFalse(result["can_publish_or_send"])
        self.assertEqual("UNKNOWN", result["eligible_recipients"])
        self.assertEqual(5, len(result["global_blockers"]))
        self.assertEqual(6, len(result["commercial_blockers"]))
        self.assertEqual([1, 2, 4, 6], result["editorial_issues"])
        self.assertEqual([3, 5], result["commercial_issues"])

    def test_opaque_attestation_does_not_override_hold(self):
        d = copy.deepcopy(self.doc)
        for item in d["evidence"].values():
            item.update(verified=True, proof_ref="QA_20261103")
        r = triage.review(d)
        self.assertFalse(r["can_publish_or_send"])
        self.assertEqual("HOLD_UNSENT", r["status"])

    def test_bad_status(self): self.bad(lambda d: d.update(campaign_state="APPROVED"))
    def test_wrong_master(self): self.bad(lambda d: d.update(original_master_sha="wrong"))
    def test_bad_sender(self): self.bad(lambda d: d.update(send_or_publish_authorized=True))
    def test_toggle_attempt(self): self.bad(lambda d: d.update(preview_toggle_authorized=True))
    def test_hide_preview_dependency(self): self.bad(lambda d: d.update(native_preview_requires_editor_send_toggle=False))
    def test_full_mode_change(self): self.bad(lambda d: d.update(mode="full"))
    def test_auto_post_send(self): self.bad(lambda d: d.update(email_new_posts_by_default=True))
    def test_infer_recipient(self): self.bad(lambda d: d.update(recipient_count=2))
    def test_infer_total_of_four(self): self.bad(lambda d: d.update(recipient_count=4))
    def test_changed_total(self): self.bad(lambda d: d["aggregates"].update(newsletter_total=3))
    def test_changed_confirmed(self): self.bad(lambda d: d["aggregates"].update(newsletter_confirmed=1))
    def test_changed_unconfirmed(self): self.bad(lambda d: d["aggregates"].update(newsletter_unconfirmed=0))
    def test_changed_email(self): self.bad(lambda d: d["aggregates"].update(stats_email=2))
    def test_changed_wpcom(self): self.bad(lambda d: d["aggregates"].update(stats_wpcom=0))
    def test_malformed_counts(self): self.bad(lambda d: d["aggregates"].update(stats_email="0"))
    def test_extra_pii_field(self): self.bad(lambda d: d["aggregates"].update(email_address="redacted"))
    def test_no_number_values(self): self.bad(lambda d: d["aggregates"].update(newsletter_total=-1))
    def test_count_is_bool(self): self.bad(lambda d: d["aggregates"].update(newsletter_total=True))
    def test_no_issues(self): self.bad(lambda d: d.update(issues=[]))
    def test_swap_commercial(self): self.bad(lambda d: d["issues"][0].update(kind="commercial"))
    def test_swap_edition_number(self): self.bad(lambda d: d["issues"][4].update(number=1))
    def test_fake_live_cta(self): self.bad(lambda d: d["issues"][2].update(cta_live=True))
    def test_evidence_nonbool(self): self.bad(lambda d: d["evidence"]["native_jetpack_email_preview"].update(verified="true"))
    def test_attestation_without_ref(self): self.bad(lambda d: d["evidence"]["qualified_final_vestige_postal_address"].update(verified=True))
    def test_email_in_ref(self): self.bad(lambda d: d["evidence"]["native_jetpack_email_preview"].update(proof_ref="someone@example.com"))
    def test_untrusted_url_ref(self): self.bad(lambda d: d["evidence"]["native_jetpack_email_preview"].update(proof_ref="https://example.com?token=x"))
    def test_extra_evidence(self): self.bad(lambda d: d["evidence"].update(customer_name={"verified":False,"proof_ref":None}))
    def test_missing_evidence(self): self.bad(lambda d: d["evidence"].pop("product_specific_email_permission"))
    def test_bad_evidence_ref_type(self): self.bad(lambda d: d["evidence"]["native_jetpack_email_preview"].update(proof_ref=14))
    def test_empty_evidence(self): self.bad(lambda d: d.update(evidence={}))
    def test_no_email_identifiers_stored(self):
        raw = (ROOT / "proofs.json").read_text(encoding="utf-8")
        self.assertNotIn("@", raw)
        self.assertNotIn("mailto:", raw)
        self.assertNotIn("?utm_", raw)
        self.assertNotIn("https://", raw)

if __name__ == "__main__":
    unittest.main()
