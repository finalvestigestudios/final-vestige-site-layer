"""Adversarial R55: purpose triage is NOT legal, merchant or send authorization."""
from __future__ import annotations
import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "r55-primary-purpose" / "review.py"
spec = importlib.util.spec_from_file_location("dispatch_r55_review", MOD_PATH)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ExistingCampaignContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((ROOT / "r55-primary-purpose/merchant_evidence.json").read_text(encoding="utf-8"))
        cls.report = review.audit(ROOT)
        cls.docs = {}
        for e in cls.manifest["issues"]:
            cls.docs[e["number"]] = (ROOT / "issues" / f"{e['number']:02d}-{e['slug']}.md").read_text(encoding="utf-8")

    def test_01_six_canonical_editions(self):
        self.assertEqual([i["issue"] for i in self.report["issues"]], list(range(1, 7)))

    def test_02_four_editorial_two_commercial(self):
        kinds = [i["type"] for i in self.report["issues"]]
        self.assertEqual(kinds.count("editorial"), 4)
        self.assertEqual(kinds.count("commercial-review-pending"), 2)

    def test_03_commercial_editions_exact(self):
        self.assertEqual(self.report["commercial_slots"], [3, 5])

    def test_04_every_edition_send_closed(self):
        self.assertFalse(self.report["send_allowed"])
        self.assertTrue(all(not i["send_allowed"] for i in self.report["issues"]))

    def test_05_each_issue_requires_actual_mime(self):
        self.assertTrue(all("ACTUAL_RECEIVED_JETPACK_MIME_ABSENT" in i["hard_holds"]
                            for i in self.report["issues"]))

    def test_06_each_issue_requires_postal_and_unsubscribe(self):
        self.assertTrue(all("VALID_FINAL_VESTIGE_POSTAL_ADDRESS_UNVERIFIED" in i["hard_holds"]
                            and "FUNCTIONAL_RECEIVED_UNSUBSCRIBE_UNVERIFIED" in i["hard_holds"]
                            for i in self.report["issues"]))

    def test_07_disputed_subscriber_counters_not_added(self):
        self.assertEqual(self.report["observed_wordpress_counts"], {
            "total": 2, "confirmed": 2, "unconfirmed": 2
        })
        self.assertFalse(self.report["counts_are_additive"])
        self.assertIsNone(self.report["final_vestige_eligible_unique_audience"])

    def test_08_empty_recent_sends_not_lifetime_zero(self):
        self.assertTrue(self.report["recent_sends_empty_not_lifetime_zero"])

    def test_09_merchant_status_hold(self):
        self.assertEqual(self.report["merchant_status"], "BOTH_HOLD_MERCHANT")
        for i in (3, 5):
            self.assertIn("NAMED_PRODUCT_PUBLISHER_EMAIL_PERMISSION_UNVERIFIED",
                          self.report["issues"][i-1]["hard_holds"])

    def test_10_first_55_commercial_missing_disclosure(self):
        for i in (3, 5):
            self.assertFalse(self.report["issues"][i-1]
                             ["modeled_excerpt_discloses_financial_connection"])
            self.assertIn("MODELED_EXCERPT_HAS_NO_FINANCIAL_DISCLOSURE",
                          self.report["issues"][i-1]["hard_holds"])

    def test_11_full_commercial_letters_have_disclosure(self):
        for i in (3, 5):
            self.assertTrue(self.report["issues"][i-1]
                            ["full_manuscript_discloses_financial_connection"])

    def test_12_issue_three_direct_seller_citations_still_present(self):
        issue = self.report["issues"][2]
        self.assertGreaterEqual(issue["direct_merchant_link_occurrences_in_narrative"], 2)
        self.assertIn("DIRECT_SELLER_CITATIONS_BYPASS_UNAPPROVED_BUYER_GUIDE",
                      issue["hard_holds"])

    def test_13_six_canonical_issues_no_dollar_promises(self):
        self.assertFalse(any(i["unverified_price_quoted_in_narrative"]
                             for i in self.report["issues"]))

    def test_14_valid_original_source_no_mismatch(self):
        self.assertEqual(self.report["source_errors"], [])

    def test_15_preheaders_are_plainly_human_readable(self):
        for i in self.report["issues"]:
            self.assertGreaterEqual(len(i["preheader"]), 30)
            self.assertLessEqual(len(i["preheader"]), 200)

    def test_16_actual_received_email_never_approvable_from_source(self):
        self.assertTrue(all(not i["email_preview_is_received_mime"]
                            and not i["legal_compliance_verified"]
                            for i in self.report["issues"]))

    def test_17_no_merchant_purchase_link_activated_in_manifest(self):
        self.assertTrue(all(e["merchant_affiliate_url"] is None for e in self.manifest["issues"]))

    def test_18_neither_product_approved_anywhere(self):
        for p in self.registry["products"].values():
            for k in ("final_vestige_accepted","specific_email_channel_permission",
                      "approved_earning_url","final_checkout_verified",
                      "refund_applies_to_current_cart_verified",
                      "approved_creative_rights","approved_live_first_party_guide"):
                self.assertIs(p[k], False)

    def test_19_registry_has_product_specific_not_catalog_sources(self):
        self.assertIn("zen12.com/hnp", self.registry["products"]["Zen12"]["official_page"])
        self.assertIn("hypnosislive.com/mental-skills/total-focus",
                      self.registry["products"]["Total Focus"]["official_page"])

    def test_20_no_false_ab_results_or_payment_metrics(self):
        self.assertTrue(self.report["report_is_not_legal_or_deliverability_signoff"])
        self.assertNotIn("conversion_rate", self.report)
        self.assertNotIn("revenue", self.report)


class AdversarialSourceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.entry1 = cls.manifest["issues"][0]
        cls.entry3 = cls.manifest["issues"][2]
        cls.markdown1 = (ROOT / "issues/01-the-mind-is-not-a-camera.md").read_text(encoding="utf-8")
        cls.markdown3 = (ROOT / "issues/03-the-twelve-minute-question.md").read_text(encoding="utf-8")

    def test_21_royal_commission_is_not_financial_disclosure(self):
        self.assertFalse(review.has_disclosure("A royal commission of 1784 investigated testimony."))

    def test_22_actual_commission_statement_is_detected(self):
        self.assertTrue(review.has_disclosure("If you buy, we may earn a commission."))

    def test_23_mixed_case_disclosure_detected(self):
        self.assertTrue(review.has_disclosure("We MIGHT RECEIVE A COMMISSION."))

    def test_24_named_merchant_domains_detected(self):
        self.assertEqual(len(review.merchant_domains(
            "https://zen12.com/hnp and https://hypnosislive.com/mental-skills/total-focus"
        )), 2)

    def test_25_nonmerchant_sources_not_flagged_as_sellers(self):
        self.assertEqual(review.merchant_domains(
            "https://www.nasa.gov/ and https://www.nccih.nih.gov/health/hypnosis"
        ), [])

    def test_26_unapproved_price_detector(self):
        self.assertTrue(review.MONEY_AMOUNT.search("costs $17.95"))
        self.assertIsNone(review.MONEY_AMOUNT.search("17.1 seconds"))

    def test_27_first_words_limit(self):
        self.assertEqual(len(review.first_words(" ".join(str(i) for i in range(70))).split()), 55)

    def test_28_zero_word_limit_refused(self):
        with self.assertRaises(ValueError):
            review.first_words("a b c", 0)

    def test_29_missing_narrative_separator_refused(self):
        with self.assertRaises(ValueError):
            review.narrative_from_markdown("No narrative separator")

    def test_30_subject_mutation_detected(self):
        entry = copy.deepcopy(self.entry1)
        entry["subject"] = "Guaranteed memory powers"
        scan = review.scan_issue(entry, self.markdown1)
        self.assertIn("SUBJECT_NOT_CANONICAL", scan["source_errors"])
        self.assertFalse(scan["send_allowed"])

    def test_31_preheader_mutation_detected(self):
        entry = copy.deepcopy(self.entry1)
        entry["preheader"] = "Proven brainwaves forever"
        scan = review.scan_issue(entry, self.markdown1)
        self.assertIn("PREHEADER_NOT_CANONICAL", scan["source_errors"])

    def test_32_postal_placeholder_removed_detected(self):
        bad = self.markdown1.replace(review.POSTAL, "")
        self.assertIn("LEGAL_PLACEHOLDER_BROKEN",
                      review.scan_issue(self.entry1, bad)["source_errors"])

    def test_33_unsubscribe_placeholder_removed_detected(self):
        bad = self.markdown1.replace(review.UNSUB, "")
        self.assertIn("LEGAL_PLACEHOLDER_BROKEN",
                      review.scan_issue(self.entry1, bad)["source_errors"])

    def test_34_affiliate_link_activation_cannot_approve(self):
        entry = copy.deepcopy(self.entry3)
        entry["merchant_affiliate_url"] = "https://zen12.com/hnp?fake=1"
        outcome = review.scan_issue(entry, self.markdown3)
        self.assertIn("RELEASE_STATE_NOT_HELD", outcome["source_errors"])
        self.assertFalse(outcome["send_allowed"])

    def test_35_published_issue_flag_cannot_approve(self):
        entry = copy.deepcopy(self.entry1)
        entry["publish_state"] = "publish"
        outcome = review.scan_issue(entry, self.markdown1)
        self.assertIn("RELEASE_STATE_NOT_HELD", outcome["source_errors"])

    def test_36_active_unapproved_guide_refused(self):
        entry = copy.deepcopy(self.entry3)
        entry["editorial_cta"] = "https://finalvestige.com/mind/zen12-guide/"
        outcome = review.scan_issue(entry, self.markdown3)
        self.assertIn("MERCHANT_GUIDE_PLACEHOLDER_MISSING", outcome["source_errors"])

    def test_37_external_editorial_cta_refused(self):
        entry = copy.deepcopy(self.entry1)
        entry["editorial_cta"] = "https://unreviewed.example.test/"
        outcome = review.scan_issue(entry, self.markdown1)
        self.assertIn("EDITORIAL_CTA_NOT_FIRST_PARTY_HTTPS", outcome["source_errors"])

    def test_38_wrong_edition_type_detected(self):
        entry = copy.deepcopy(self.entry1)
        entry["kind"] = "commercial-review-pending"
        outcome = review.scan_issue(entry, self.markdown1)
        self.assertIn("EDITION_KIND_NOT_CANONICAL", outcome["source_errors"])

    def test_39_synthetic_seller_quote_not_a_source_approval(self):
        bad = self.markdown3.replace("**Read our independent Zen12 evaluation", "Price $2 today!\n\n**Read our independent Zen12 evaluation")
        scan = review.scan_issue(self.entry3, bad)
        self.assertTrue(scan["unverified_price_quoted_in_narrative"])
        self.assertFalse(scan["send_allowed"])

    def test_40_historic_dossier_not_auto_classed_transactional(self):
        self.assertEqual(review.classify_for_human_review(2),
                         "EDITORIAL_OR_MIXED_PRIMARY_PURPOSE_HUMAN_REVIEW")

    def test_41_product_email_not_auto_certified_commercial_legal(self):
        self.assertEqual(review.classify_for_human_review(3),
                         "COMMERCIAL_PRIMARY_PURPOSE_HUMAN_REVIEW")

    def test_42_unknown_edition_refused(self):
        with self.assertRaises(ValueError):
            review.classify_for_human_review(7)


if __name__ == "__main__":
    unittest.main()
