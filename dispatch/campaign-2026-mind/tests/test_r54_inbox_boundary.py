"""Adversarial read-only checks for R54: no newsletter, merchant, or site writes."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "r54-inbox-boundary" / "inbox_boundary.py"
spec = importlib.util.spec_from_file_location("fv_inbox_boundary_r54", MOD_PATH)
guard = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(guard)
AUDIT = guard.build_audit()


class ExtractionAndDisclosureTests(unittest.TestCase):
    def test_extract_isolates_canonical_narrative(self):
        raw = (ROOT / "issues" / guard.ISSUE_FILENAMES[0]).read_text(encoding="utf-8")
        value = guard.editable_body(raw)
        self.assertTrue(value.startswith("A stranger stops"))
        self.assertNotIn("VALID_POSTAL_ADDRESS_REQUIRED", value)

    def test_extract_rejects_missing_separator(self):
        with self.assertRaises(ValueError):
            guard.editable_body("draft without separators")

    def test_extract_rejects_multiple_separator_traps(self):
        with self.assertRaises(ValueError):
            guard.editable_body("header\n---\na\n---\nb\n---\nc")

    def test_extract_rejects_leaked_legal_footer(self):
        with self.assertRaises(ValueError):
            guard.editable_body("header\n---\nPre-send compliance block\n---\nlegal")

    def test_visible_text_preserves_link_labels(self):
        self.assertEqual(guard.visible_text("[A record](https://example.org) **matters**"), "A record matters")

    def test_visible_text_drops_markdown_lists(self):
        self.assertEqual(guard.visible_text("- **Observe:** Evidence"), "Observe: Evidence")

    def test_visible_text_drops_extraneous_spaces(self):
        self.assertEqual(guard.visible_text("One\n\n    two"), "One two")

    def test_fallback_max_55(self):
        self.assertEqual(len(guard.fallback_preview("word " * 80).split()), 55)

    def test_fallback_shorter_narrative(self):
        self.assertEqual(guard.fallback_preview("Just three words."), "Just three words.")

    def test_fallback_disallows_zero_word_budget(self):
        with self.assertRaises(ValueError):
            guard.fallback_preview("Sample", 0)

    def test_royal_commission_not_financial_disclosure(self):
        self.assertFalse(guard.financial_disclosure_visible("The royal commission investigated Mesmer."))

    def test_commissioner_not_financial_disclosure(self):
        self.assertFalse(guard.financial_disclosure_visible("The commissioner signed a document."))

    def test_commercial_disclosure_label_is_detected(self):
        self.assertTrue(guard.financial_disclosure_visible("Commercial disclosure: not an endorsement."))

    def test_affiliate_evaluation_label_is_detected(self):
        self.assertTrue(guard.financial_disclosure_visible("Affiliate evaluation: editorial copy."))

    def test_may_earn_a_commission_is_detected(self):
        self.assertTrue(guard.financial_disclosure_visible("We may earn a commission."))

    def test_seller_reference_is_not_a_financial_disclosure(self):
        self.assertFalse(guard.financial_disclosure_visible("The product page describes one 47 MB file."))

    def test_disclosure_position_counts_words(self):
        self.assertEqual(guard.disclosure_word_position("Here is proof. Commercial disclosure: test"), 3)

    def test_disclosure_position_missing_returns_none(self):
        self.assertIsNone(guard.disclosure_word_position("Evidence is not a guarantee."))

    def test_merchant_link_counter_rejects_plain_mentions(self):
        self.assertEqual(guard.merchant_link_count("Visit zen12.com/hnp (not a Markdown link)."), 0)

    def test_merchant_link_counter_counts_clickable_seller(self):
        self.assertEqual(guard.merchant_link_count("[seller](https://zen12.com/hnp)"), 1)

    def test_merchant_link_counter_counts_hypnosislive(self):
        self.assertEqual(guard.merchant_link_count("[seller](https://hypnosislive.com/mental-skills/total-focus)"), 1)

    def test_merchant_link_counter_excludes_independent_source(self):
        self.assertEqual(guard.merchant_link_count("[NCCIH](https://www.nccih.nih.gov/health/hypnosis)"), 0)


class ExactCampaignContractTests(unittest.TestCase):
    def test_six_issues(self):
        self.assertEqual(len(AUDIT["editions"]), 6)

    def test_source_mix(self):
        self.assertEqual([x["kind"] for x in AUDIT["editions"]].count("editorial"), 4)
        self.assertEqual([x["kind"] for x in AUDIT["editions"]].count("commercial-review-pending"), 2)

    def test_all_issues_hold(self):
        self.assertEqual({x["release_state"] for x in AUDIT["editions"]}, {"HOLD_UNSENT"})

    def test_named_commercial_hold_only(self):
        held = [x["number"] for x in AUDIT["editions"] if x["merchant_state"] == "HOLD_MERCHANT"]
        self.assertEqual(held, [3, 5])

    def test_rehearsal_not_actual_email(self):
        self.assertEqual(AUDIT["identity"], "OFFLINE_APPROXIMATION_ONLY_NOT_AN_EMAIL")
        self.assertFalse(AUDIT["received_jetpack_email_inspected"])
        self.assertFalse(AUDIT["native_preview_performed"])

    def test_no_custom_excerpt_installed(self):
        self.assertFalse(AUDIT["custom_excerpts_installed"])

    def test_no_known_unique_audience(self):
        self.assertIsNone(AUDIT["real_unique_eligible_audience"])

    def test_all_fallbacks_55_words(self):
        for edition in AUDIT["editions"]:
            with self.subTest(edition=edition["number"]):
                self.assertEqual(edition["fallback_word_count"], 55)

    def test_direct_cta_not_in_any_fallback(self):
        for edition in AUDIT["editions"]:
            with self.subTest(edition=edition["number"]):
                self.assertFalse(edition["first_55_words_contains_primary_cta"])

    def test_two_commercial_fallbacks_lack_disclosure(self):
        for n in (3, 5):
            self.assertFalse(AUDIT["editions"][n-1]["fallback_contains_explicit_financial_disclosure"])

    def test_two_proposed_custom_excerpts_disclose(self):
        for n in (3, 5):
            self.assertTrue(AUDIT["editions"][n-1]["proposed_contains_explicit_financial_disclosure"])

    def test_royal_1784_commission_not_an_affiliate_claim(self):
        edition = AUDIT["editions"][1]
        self.assertIn("commission", edition["proposed_custom_excerpt_not_installed"].lower())
        self.assertFalse(edition["proposed_contains_explicit_financial_disclosure"])

    def test_commercial_disclosure_occurs_after_55_word_cutoff(self):
        for n in (3, 5):
            self.assertGreater(AUDIT["editions"][n-1]["first_explicit_disclosure_zero_based_word"], 55)

    def test_issue03_canonical_direct_seller_links_are_still_present(self):
        self.assertEqual(AUDIT["editions"][2]["clickable_seller_citations_in_original"], 2)

    def test_five_other_canonical_issues_no_seller_links(self):
        for n in (1, 2, 4, 5, 6):
            self.assertEqual(AUDIT["editions"][n-1]["clickable_seller_citations_in_original"], 0)

    def test_no_native_preheader_claim(self):
        self.assertTrue(all(not e["native_preheader_verified"] for e in AUDIT["editions"]))

    def test_no_received_message_claim(self):
        self.assertTrue(all(not e["native_received_email_verified"] for e in AUDIT["editions"]))

    def test_excerpts_are_marked_optional_not_installed(self):
        for edition in AUDIT["editions"]:
            self.assertGreater(len(edition["proposed_custom_excerpt_not_installed"]), 120)

    def test_official_provider_documented_rule_is_cited(self):
        self.assertEqual(AUDIT["underlying_official_rule"], "https://wordpress.com/support/newsletter-settings/")

    def test_live_state_is_only_a_dated_snapshot(self):
        self.assertEqual(AUDIT["observed_mode"], "excerpt")
        self.assertIn("2026-11-02", AUDIT["current_settings_as_of"])

    def test_old_legal_placeholders_not_reader_excerpt(self):
        for e in AUDIT["editions"]:
            self.assertNotIn("[[", e["first_55_words_fallback_model"])
            self.assertNotIn("[[", e["proposed_custom_excerpt_not_installed"])

    def test_regression_on_issue04_precision(self):
        e = AUDIT["editions"][3]
        self.assertIn("17.1 seconds", e["first_55_words_fallback_model"])

    def test_regression_on_issue01_1998(self):
        self.assertIn("1998", AUDIT["editions"][0]["first_55_words_fallback_model"])

    def test_six_unique_subjects(self):
        self.assertEqual(len({x["subject"] for x in AUDIT["editions"]}), 6)


class WordPressSendInterlockTests(unittest.TestCase):
    def setUp(self):
        self.safe = dict(status="draft", send_to_subscribers=False,
                         scheduled_at=None, test_email_sent=False,
                         audience="NONE", native_received_email=False,
                         founder_send_approval=False)

    def test_draft_preview_mode_is_not_publish_approval(self):
        self.assertTrue(guard.safe_editor_rehearsal(self.safe))
        self.assertEqual(AUDIT["readiness"], "HOLD_UNSENT")

    def test_manual_send_toggle_on_is_rejected(self):
        self.safe["send_to_subscribers"] = True
        self.assertFalse(guard.safe_editor_rehearsal(self.safe))

    def test_unknown_manual_toggle_is_rejected(self):
        self.safe.pop("send_to_subscribers")
        self.assertFalse(guard.safe_editor_rehearsal(self.safe))

    def test_publish_state_is_rejected(self):
        self.safe["status"] = "publish"
        self.assertFalse(guard.safe_editor_rehearsal(self.safe))

    def test_future_scheduled_post_is_rejected(self):
        self.safe["status"] = "future"
        self.assertFalse(guard.safe_editor_rehearsal(self.safe))

    def test_scheduled_at_is_rejected(self):
        self.safe["scheduled_at"] = "2026-11-08T09:00:00-08:00"
        self.assertFalse(guard.safe_editor_rehearsal(self.safe))

    def test_test_send_is_rejected(self):
        self.safe["test_email_sent"] = True
        self.assertFalse(guard.safe_editor_rehearsal(self.safe))

    def test_any_real_audience_is_rejected(self):
        self.safe["audience"] = "subscribers"
        self.assertFalse(guard.safe_editor_rehearsal(self.safe))

    def test_claimed_received_mime_is_rejected(self):
        self.safe["native_received_email"] = True
        self.assertFalse(guard.safe_editor_rehearsal(self.safe))

    def test_founder_send_approval_is_a_separate_gate(self):
        self.safe["founder_send_approval"] = True
        self.assertFalse(guard.safe_editor_rehearsal(self.safe))

    def test_missing_approval_field_fails_closed(self):
        self.safe.pop("founder_send_approval")
        self.assertFalse(guard.safe_editor_rehearsal(self.safe))


class SnapshotAndArtifactTests(unittest.TestCase):
    def test_no_subscriber_addresses_in_snapshot(self):
        record = json.loads((ROOT / "r54-inbox-boundary" / "snapshot.json").read_text(encoding="utf-8"))
        raw = json.dumps(record).lower()
        self.assertNotIn("@gmail.", raw)
        self.assertNotIn("@yahoo.", raw)
        self.assertNotIn("@outlook.", raw)

    def test_subscriber_count_conflict_is_not_resolved_by_guess(self):
        record = guard.load_json(ROOT / "r54-inbox-boundary" / "snapshot.json")
        c = record["subscriber_counts"]
        self.assertEqual([c["total"], c["confirmed"], c["unconfirmed"]], [2, 2, 2])
        self.assertIsNone(c["unique_eligible_recipients"])

    def test_off_default_is_not_global_send_lock(self):
        record = guard.load_json(ROOT / "r54-inbox-boundary" / "snapshot.json")
        self.assertFalse(record["jetpack"]["email_new_posts_by_default"])
        self.assertTrue(record["jetpack"]["site_can_send"])

    def test_original_focus_welcome_not_claimed_delivered(self):
        record = guard.load_json(ROOT / "r54-inbox-boundary" / "snapshot.json")
        self.assertTrue(record["jetpack"]["configured_welcome_includes_52_page_focus_fieldbook"])
        self.assertFalse(record["jetpack"]["actual_welcome_delivery_verified"])

    def test_exact_parent_commit_documented(self):
        record = guard.load_json(ROOT / "r54-inbox-boundary" / "snapshot.json")
        self.assertEqual(record["source_sha_before_this_sprint"],
                         "e128015d8dd07c1faa4beaeebec7a46846263380")

    def test_no_email_or_publishing_in_snapshot(self):
        record = guard.load_json(ROOT / "r54-inbox-boundary" / "snapshot.json")
        self.assertTrue(record["no_site_changes"])
        self.assertTrue(record["no_subscriber_data_exposed"])

    def test_static_review_board_does_not_have_form_or_script(self):
        board = (ROOT / "r54-inbox-boundary" / "review.html").read_text(encoding="utf-8").lower()
        self.assertNotIn("<script", board)
        self.assertNotIn("<form", board)
        self.assertNotIn("http-equiv=\"refresh\"", board)

    def test_static_review_board_is_readable_and_status_clear(self):
        board = (ROOT / "r54-inbox-boundary" / "review.html").read_text(encoding="utf-8")
        self.assertIn('lang="en"', board)
        self.assertIn('id="main-content"', board)
        self.assertIn("OFFLINE REHEARSAL", board)
        self.assertIn("NOT A SENT EMAIL", board)
        self.assertIn("HOLD_UNSENT", board)

    def test_static_review_board_includes_all_six_subjects(self):
        board = (ROOT / "r54-inbox-boundary" / "review.html").read_text(encoding="utf-8")
        for e in AUDIT["editions"]:
            self.assertIn(e["subject"], board)

    def test_static_review_board_does_not_link_seller(self):
        board = (ROOT / "r54-inbox-boundary" / "review.html").read_text(encoding="utf-8")
        self.assertNotIn('href="https://zen12.com/', board)
        self.assertNotIn('href="https://hypnosislive.com/', board)


if __name__ == "__main__":
    unittest.main()
