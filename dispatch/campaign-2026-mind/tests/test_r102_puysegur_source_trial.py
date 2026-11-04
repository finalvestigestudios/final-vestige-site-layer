"""Native Python regression + adversarial tests for R102 historical editorial candidate."""
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "r102-puysegur-source-trial"
sys.path.insert(0, str(SRC))
from gate import inspect, EXPECTED_CTA

class PuységurReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((SRC / "source_and_release_ledger.json").read_text(encoding="utf-8"))
        cls.assets = {
            "md": (SRC / "02-puysegur-source-trial.md").read_text(encoding="utf-8"),
            "txt": (SRC / "02-puysegur-source-trial.txt").read_text(encoding="utf-8"),
            "html": (SRC / "02-puysegur-review.html").read_text(encoding="utf-8"),
        }

    def review(self, mutation=None, asset=None, replace=None):
        ledger = copy.deepcopy(self.ledger)
        assets = copy.deepcopy(self.assets)
        if mutation:
            mutation(ledger)
        if asset is not None:
            assets[asset] = replace
        return inspect(ledger, assets)

    def test_clean_editorial_candidate_passes_structural_checks_but_stays_unsent(self):
        report = self.review()
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["decision"], "HOLD_UNSENT")

    def test_six_master_issues_unmodified(self):
        source = ROOT / "manifest.json"
        master = json.loads(source.read_text(encoding="utf-8"))
        self.assertEqual([x["kind"] for x in master["issues"]].count("editorial"), 4)
        self.assertEqual([x["kind"] for x in master["issues"]].count("commercial-review-pending"), 2)
        self.assertEqual(master["status"], "DRAFT_UNSENT_NO_SCHEDULING")

    def test_invalid_campaign_rejected(self):
        self.assertIn("wrong_campaign", self.review(lambda d: d.update(issue=999))["errors"])

    def test_changed_master_sha_rejected(self):
        self.assertIn("wrong_master_commit", self.review(lambda d: d.update(master_sha="abcd"))["errors"])

    def test_fake_release_rejected(self):
        self.assertIn("release_state", self.review(lambda d: d.update(state="SEND_READY"))["errors"])

    def test_affiliate_flag_rejected(self):
        self.assertIn("commercial_or_live_cta", self.review(lambda d: d["cta"].update(is_affiliate=True))["errors"])

    def test_outbound_link_rejected(self):
        self.assertIn("commercial_or_live_cta", self.review(lambda d: d["cta"].update(url="https://inspire3.com/"))["errors"])

    def test_missing_published_cta_rejected(self):
        self.assertIn("commercial_or_live_cta", self.review(lambda d: d["cta"].update(status="PENDING"))["errors"])

    def test_fake_founder_approval_rejected(self):
        self.assertIn("unverified_approvals", self.review(lambda d: d["hold"].update(founder_final_approval=True))["errors"])

    def test_fake_eligible_recipients_rejected(self):
        self.assertIn("unverified_approvals", self.review(lambda d: d["hold"].update(eligible_recipients_verified=True))["errors"])

    def test_fake_merchant_permission_rejected(self):
        self.assertIn("unverified_approvals", self.review(lambda d: d["hold"].update(affiliate_email_permission_verified=True))["errors"])

    def test_fake_received_email_rejected(self):
        self.assertIn("fake_jetpack_mime", self.review(lambda d: d["delivery"].update(html_preview_is_received_email=True))["errors"])

    def test_fake_native_preheader_rejected(self):
        self.assertIn("fake_jetpack_mime", self.review(lambda d: d["delivery"].update(native_jetpack_preheader_field_verified=True))["errors"])

    def test_unknown_excerpt_setting_rejected(self):
        self.assertIn("missing_excerpt_mode", self.review(lambda d: d["delivery"].update(excerpt_mode_on=False))["errors"])

    def test_missing_bnf_source_rejected(self):
        self.assertIn("source_provenance", self.review(lambda d: d.update(sources=[x for x in d["sources"] if "bnf" not in x["url"]]))["errors"])

    def test_missing_html_postal_stop_rejected(self):
        html = self.assets["html"].replace("[[VALID_POSTAL_ADDRESS_REQUIRED]]", "123 Fake St")
        self.assertIn("missing_legal_stop_html", self.review(asset="html", replace=html)["errors"])

    def test_missing_text_unsubscribe_rejected(self):
        txt = self.assets["txt"].replace("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", "https://example.com")
        self.assertIn("missing_legal_stop_txt", self.review(asset="txt", replace=txt)["errors"])

    def test_script_injection_rejected(self):
        html = self.assets["html"] + "<script>alert(1)</script>"
        self.assertIn("unsafe_html", self.review(asset="html", replace=html)["errors"])

    def test_event_handler_rejected(self):
        html = self.assets["html"] + '<div onclick="run()">x</div>'
        self.assertIn("unsafe_html", self.review(asset="html", replace=html)["errors"])

    def test_external_image_rejected(self):
        html = self.assets["html"] + '<img src="https://tracker.example/pixel">'
        self.assertIn("unsafe_html", self.review(asset="html", replace=html)["errors"])

    def test_email_leak_rejected(self):
        txt = self.assets["txt"] + "\nsubscriber@example.com"
        self.assertIn("email_leak_txt", self.review(asset="txt", replace=txt)["errors"])

    def test_pseudo_affiliate_html_rejected(self):
        html = self.assets["html"] + '<a href="https://hypnosislive.com/example">buy</a>'
        self.assertIn("merchant_href_html", self.review(asset="html", replace=html)["errors"])

    def test_misleading_promise_rejected(self):
        md = self.assets["md"] + "\nThis is clinically proven!"
        self.assertIn("misleading_purchase", self.review(asset="md", replace=md)["errors"])

    def test_not_a_real_received_email(self):
        self.assertIn("NOT AN ACTUAL JETPACK EMAIL", self.assets["html"])
        self.assertEqual(self.ledger["delivery"]["html_preview_is_received_email"], False)

    def test_source_keys_all_present(self):
        for item in self.ledger["sources"]:
            self.assertIn(item["url"], self.assets["md"])
            self.assertIn(item["url"], self.assets["txt"])
            self.assertIn(item["url"], self.assets["html"])

    def test_subject_and_excerpt_not_fake_jetpack_fields(self):
        self.assertLessEqual(len(self.ledger["subject_candidate"]), 70)
        self.assertLessEqual(len(self.ledger["preheader_candidate"]), 100)
        self.assertLessEqual(len(self.ledger["custom_excerpt_candidate"]), 300)

    def test_no_new_list_or_website_writes(self):
        self.assertFalse(self.ledger["hold"]["wp_writes"])
        self.assertFalse(self.ledger["hold"]["emails_sent"])
        self.assertFalse(self.ledger["hold"]["founder_final_approval"])

    def test_only_one_primary_button(self):
        self.assertEqual(self.assets["html"].count(">Examine the surviving file</a>"), 1)
        self.assertEqual(self.ledger["cta"]["url"], EXPECTED_CTA)

if __name__ == "__main__":
    unittest.main()
