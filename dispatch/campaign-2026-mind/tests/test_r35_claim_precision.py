"""R35 original research-method fidelity, email-safe static candidate, and fail-closed release tests."""
import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILE = ROOT / "r35-diary-study" / "validate_candidate.py"
spec = importlib.util.spec_from_file_location("fv_r35_claim_validator", FILE)
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

class R35SourcePrecision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = V.packet()

    def reject(self, mutate):
        p = copy.deepcopy(self.original)
        mutate(p)
        r = V.validate_packet(p)
        self.assertFalse(r["static_integrity"], r)
        self.assertEqual(r["release_status"], "HOLD_UNSENT")
        self.assertFalse(r["email_sent_or_authorized"])

    def test_original_static_integrity_is_true_but_not_send_approval(self):
        r = V.validate_packet(self.original)
        self.assertTrue(r["static_integrity"], r)
        self.assertEqual(r["release_status"], "HOLD_UNSENT")
        self.assertFalse(r["real_jetpack_render_verified"])

    def test_paper_observation_not_conflated_with_mental_efficacy(self):
        m = self.original["markdown"].lower()
        self.assertIn("binder", m)
        self.assertIn("it did not independently read the words", m)
        self.assertIn("not meditation", m)

    def test_research_link_is_primary_open_access_2002(self):
        self.assertIn("pmc.ncbi.nlm.nih.gov/articles/PMC111114", self.original["markdown"])
        self.assertIn("bmj", self.original["markdown"].lower())
        self.assertNotIn("2003", self.original["markdown"])

    def test_one_noncommercial_cta(self):
        h = self.original["html"]
        parser = V.Links()
        parser.feed(h)
        self.assertEqual(parser.links, [V.CTA, V.SOURCE])

    def test_subject_truncation_rejected(self):
        self.reject(lambda p: p.__setitem__("markdown", p["markdown"].replace(V.SUBJECT, "A miracle seven days")))

    def test_preheader_drift_rejected(self):
        self.reject(lambda p: p.__setitem__("plaintext", p["plaintext"].replace(V.PREHEADER, "Guaranteed total focus now")))

    def test_html_subject_drift_rejected(self):
        self.reject(lambda p: p.__setitem__("html", p["html"].replace(V.SUBJECT, "How to get rich quickly")))

    def test_html_preheader_removed_rejected(self):
        self.reject(lambda p: p.__setitem__("html", p["html"].replace(V.PREHEADER, "")))

    def test_11_percent_fact_removed_rejected(self):
        self.reject(lambda p: p.__setitem__("markdown", p["markdown"].replace("11%", ""))
    )
    def test_90_percent_fact_removed_rejected(self):
        self.reject(lambda p: p.__setitem__("plaintext", p["plaintext"].replace("90%", "")))

    def test_30_min_window_removed_rejected(self):
        self.reject(lambda p: p.__setitem__("html", p["html"].replace("30-minute", "")))

    def test_paper_group_removed_rejected(self):
        self.reject(lambda p: p.__setitem__("markdown", p["markdown"].replace("40 participants", "four people")))

    def test_binder_measure_removed_rejected(self):
        self.reject(lambda p: p.__setitem__("plaintext", p["plaintext"].replace("binder", "file")))

    def test_wrong_2003_study_rejected(self):
        self.reject(lambda p: p.__setitem__("html", p["html"].replace("2002", "2003")))

    def test_unverified_efficacy_guarantee_rejected(self):
        self.reject(lambda p: p.__setitem__("markdown", p["markdown"] + "\nGuaranteed improvement in attention."))

    def test_email_unapproved_merchant_url_rejected(self):
        self.reject(lambda p: p.__setitem__("html", p["html"].replace(V.CTA, "https://zen12.com/buy")))

    def test_markdown_unapproved_merchant_url_rejected(self):
        self.reject(lambda p: p.__setitem__("markdown", p["markdown"] + "\nhttps://hypnosislive.com/mental-skills/total-focus"))

    def test_html_script_rejected(self):
        self.reject(lambda p: p.__setitem__("html", p["html"] + "<script>alert(1)</script>"))

    def test_unlisted_html_link_rejected(self):
        self.reject(lambda p: p.__setitem__("html", p["html"].replace("</body>", '<a href="https://example.org/">Buy</a></body>')))

    def test_plaintext_unsubscribe_removed_rejected(self):
        self.reject(lambda p: p.__setitem__("plaintext", p["plaintext"].replace(V.UNSUB, "")))

    def test_html_postal_placeholder_removed_rejected(self):
        self.reject(lambda p: p.__setitem__("html", p["html"].replace(V.ADDRESS, "")))

    def test_markdown_warning_removed_rejected(self):
        self.reject(lambda p: p.__setitem__("markdown", p["markdown"].replace("DO NOT SEND", "reviewed")))

    def test_ledger_sendready_forgery_rejected(self):
        self.reject(lambda p: p["ledger"].__setitem__("release_state", "SEND_READY"))

    def test_candidate_assumed_approved_rejected(self):
        self.reject(lambda p: p["ledger"]["review_candidate"].__setitem__("state", "APPROVED"))

    def test_fake_unique_count_rejected(self):
        self.reject(lambda p: p["ledger"]["verified_wp_read_only"].__setitem__("unique_eligible_recipients", 4))

    def test_fake_received_welcome_rejected(self):
        self.reject(lambda p: p["ledger"]["verified_wp_read_only"].__setitem__("welcome_received", True))

    def test_six_issue_mix_must_not_shift(self):
        self.reject(lambda p: p["manifest"]["issues"][0].__setitem__("kind", "commercial-review-pending"))

    def test_activated_merchant_manifest_rejected(self):
        self.reject(lambda p: p["manifest"]["issues"][2].__setitem__("merchant_affiliate_url", "https://zen12.com/checkout?aff=1"))

    def test_scheduling_manifest_rejected(self):
        self.reject(lambda p: p["manifest"].__setitem__("status", "SCHEDULED"))

    def test_unapproved_replaces_canonical_rejected(self):
        self.reject(lambda p: p["ledger"]["review_candidate"].__setitem__("replaces_canonical", True))

if __name__ == "__main__":
    unittest.main()
