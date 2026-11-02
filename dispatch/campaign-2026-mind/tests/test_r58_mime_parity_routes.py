"""R58 conservative, strictly synthetic received-email triage regressions.

No network, WordPress writes, live recipients, product links, or mail sends.
All fixtures use .invalid test addresses; no function grants send permission.
"""
from __future__ import annotations

import importlib.util
import json
import unittest
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "r56-mime-evidence" / "mime_inspector.py"
spec = importlib.util.spec_from_file_location("fv_r58_inspector", MODULE)
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)
ISSUES = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))["issues"]
DISCLOSE = "Final Vestige may earn a commission from a qualifying purchase."
POSTAL = "Invented Example Address 123, Test City 00000"
UNSUB = "https://wordpress.com/subscriptions/unsubscribe?token=NEVER_REAL"
SELLER = "https://zen12.com/hnp"
FOCUS_SELLER = "https://hypnosislive.com/mental-skills/total-focus"


def craft(*, issue=3, plain="Plain editorial example.", html=None, unsub=None):
    m = EmailMessage()
    m["From"] = "Final Vestige <example@sender.invalid>"
    m["To"] = "not-an-actual-recipient@example.invalid"
    m["Subject"] = ISSUES[issue - 1]["subject"]
    if unsub:
        m["List-Unsubscribe"] = "<" + unsub + ">"
    m.set_content(plain)
    if html is not None:
        m.add_alternative(html, subtype="html")
    return m.as_bytes()


def scan(*, issue=3, plain="Plain editorial example.", html=None, unsub=None):
    return inspector.inspect_bytes(
        craft(issue=issue, plain=plain, html=html, unsub=unsub),
        ISSUES[issue - 1], origin="synthetic", postal_address=POSTAL
    )


class MimeAlternativeParity(unittest.TestCase):
    def test_01_html_disclosure_does_not_clean_plaintext(self):
        x = scan(html="<p>" + DISCLOSE + "</p>")
        self.assertTrue(x["disclosure_in_text_html_first_85_words"])
        self.assertFalse(x["disclosure_in_text_plain_first_85_words"])
        self.assertFalse(x["commercial_disclosure_parity_across_mime_alternatives"])
        self.assertIn("EARLY_DISCLOSURE_NOT_PRESENT_IN_BOTH_MIME_ALTERNATIVES", x["holds"])

    def test_02_both_alternatives_have_disclosure(self):
        x = scan(plain=DISCLOSE, html="<p>" + DISCLOSE + "</p>")
        self.assertTrue(x["commercial_disclosure_parity_across_mime_alternatives"])
        self.assertNotIn("EARLY_DISCLOSURE_NOT_PRESENT_IN_BOTH_MIME_ALTERNATIVES", x["holds"])

    def test_03_plain_only_disclosure_not_enough_for_html(self):
        x = scan(plain=DISCLOSE, html="<p>Only a marketing story here.</p>")
        self.assertFalse(x["commercial_disclosure_parity_across_mime_alternatives"])
        self.assertIn("EARLY_DISCLOSURE_NOT_PRESENT_IN_BOTH_MIME_ALTERNATIVES", x["holds"])

    def test_04_plain_only_with_disclosure_is_not_a_mismatch(self):
        x = scan(plain=DISCLOSE)
        self.assertTrue(x["commercial_disclosure_parity_across_mime_alternatives"])
        self.assertTrue(x["disclosure_in_text_plain_first_85_words"])
        self.assertFalse(x["has_text_html"])

    def test_05_plain_only_without_disclosure_gets_primary_hold(self):
        x = scan(plain="Not disclosed.")
        self.assertIn("EARLY_COMMERCIAL_DISCLOSURE_MISSING", x["holds"])

    def test_06_both_missing_disclosure_has_primary_and_parity_hold(self):
        x = scan(plain="Undisclosed plain.", html="<p>Undisclosed HTML.</p>")
        self.assertIn("EARLY_COMMERCIAL_DISCLOSURE_MISSING", x["holds"])
        self.assertIn("EARLY_DISCLOSURE_NOT_PRESENT_IN_BOTH_MIME_ALTERNATIVES", x["holds"])

    def test_07_one_html_disclosure_and_empty_plain_no_parity_hold(self):
        x = scan(plain="", html="<p>" + DISCLOSE + "</p>")
        self.assertTrue(x["commercial_disclosure_parity_across_mime_alternatives"])

    def test_08_same_rules_on_fifth_issue(self):
        x = scan(issue=5, html="<p>" + DISCLOSE + "</p>")
        self.assertIn("EARLY_DISCLOSURE_NOT_PRESENT_IN_BOTH_MIME_ALTERNATIVES", x["holds"])

    def test_09_editorial_issue_is_not_commercial_mismatch(self):
        x = scan(issue=1, html="<p>Historical evidence.</p>")
        self.assertTrue(x["commercial_disclosure_parity_across_mime_alternatives"])
        self.assertNotIn("EARLY_DISCLOSURE_NOT_PRESENT_IN_BOTH_MIME_ALTERNATIVES", x["holds"])

    def test_10_late_plaintext_disclosure_is_not_early(self):
        x = scan(plain=("word " * 95) + DISCLOSE, html="<p>" + DISCLOSE + "</p>")
        self.assertFalse(x["disclosure_in_text_plain_first_85_words"])
        self.assertFalse(x["commercial_disclosure_parity_across_mime_alternatives"])

    def test_11_late_html_disclosure_is_not_early(self):
        x = scan(plain=DISCLOSE, html="<p>" + ("word " * 95) + "</p><p>" + DISCLOSE + "</p>")
        self.assertFalse(x["disclosure_in_text_html_first_85_words"])
        self.assertFalse(x["commercial_disclosure_parity_across_mime_alternatives"])

    def test_12_early_both_alternatives_still_cannot_send(self):
        x = scan(plain=DISCLOSE, html="<p>" + DISCLOSE + "</p>")
        self.assertFalse(x["send_allowed"])
        self.assertFalse(x["legal_compliance_certified"])

    def test_13_received_label_cannot_assert_attestation(self):
        x = inspector.inspect_bytes(craft(plain=DISCLOSE), ISSUES[2], origin="received")
        self.assertFalse(x["source_is_received_message_independently_attested"])

    def test_14_no_product_permission_autofill(self):
        x = scan(plain=DISCLOSE, html="<p>" + DISCLOSE + "</p>")
        self.assertFalse(x["merchant_email_permission_verified"])
        self.assertFalse(x["founder_final_send_approval"])


class NavigationRouteAudit(unittest.TestCase):
    def test_15_form_action_is_seller_route(self):
        self.assertEqual(scan(html='<form action="' + SELLER + '">Buy</form>')["direct_seller_link_count"], 1)

    def test_16_button_formaction_is_seller_route(self):
        self.assertEqual(scan(html='<button formaction="' + SELLER + '">Buy</button>')["direct_seller_link_count"], 1)

    def test_17_input_formaction_is_seller_route(self):
        self.assertEqual(scan(html='<input type="submit" formaction="' + SELLER + '">')["direct_seller_link_count"], 1)

    def test_18_image_map_area_is_seller_route(self):
        self.assertEqual(scan(html='<map><area href="' + SELLER + '"></map>')["direct_seller_link_count"], 1)

    def test_19_iframe_src_is_seller_route(self):
        self.assertEqual(scan(html='<iframe src="' + SELLER + '"></iframe>')["direct_seller_link_count"], 1)

    def test_20_object_data_is_seller_route(self):
        self.assertEqual(scan(html='<object data="' + SELLER + '"></object>')["direct_seller_link_count"], 1)

    def test_21_meta_refresh_is_seller_route(self):
        x = scan(html='<meta http-equiv="refresh" content="0; url=' + SELLER + '">')
        self.assertEqual(x["direct_seller_link_count"], 1)

    def test_22_meta_refresh_quoted_is_seller_route(self):
        x = scan(html="<meta http-equiv='refresh' content=\"0; URL='" + SELLER + "'\">")
        self.assertEqual(x["direct_seller_link_count"], 1)

    def test_23_hidden_form_is_still_tracked(self):
        x = scan(html='<form hidden action="' + SELLER + '">Buy</form>')
        self.assertIn("DIRECT_MERCHANT_LINK_BYPASSES_REVIEWED_GUIDE", x["holds"])

    def test_24_specific_total_focus_non_anchor_is_tracked(self):
        x = scan(issue=5, html='<form action="' + FOCUS_SELLER + '"></form>')
        self.assertEqual(x["direct_seller_link_count"], 1)

    def test_25_nonmerchant_form_is_not_seller(self):
        x = scan(html='<form action="https://example.invalid/form"></form>')
        self.assertEqual(x["direct_seller_link_count"], 0)

    def test_26_spoofed_seller_suffix_is_not_seller(self):
        x = scan(html='<form action="https://zen12.com.attacker.invalid/hnp"></form>')
        self.assertEqual(x["direct_seller_link_count"], 0)

    def test_27_javascript_form_is_unsafe(self):
        x = scan(html='<form action="javascript:alert(1)"></form>')
        self.assertIn("UNSAFE_LINK_SCHEME", x["holds"])

    def test_28_data_iframe_is_unsafe(self):
        x = scan(html='<iframe src="data:text/html,malicious"></iframe>')
        self.assertEqual(x["unsafe_link_scheme_count"], 1)

    def test_29_bad_ipv6_form_is_a_hold_not_a_crash(self):
        x = scan(html='<form action="https://[broken"></form>')
        self.assertEqual(x["malformed_link_count"], 1)
        self.assertIn("MALFORMED_LINK_HUMAN_REVIEW", x["holds"])

    def test_30_repeated_identical_seller_route_count_is_unique(self):
        x = scan(html='<a href="' + SELLER + '">Buy</a><form action="' + SELLER + '"></form>')
        self.assertEqual(x["direct_seller_link_count"], 1)


class UnsubscribeCandidatePrecision(unittest.TestCase):
    def test_31_read_more_link_cannot_borrow_unsubscribe_text(self):
        x = scan(html='<p>Unsubscribe whenever you like.</p><a href="' + UNSUB + '">Read more</a>')
        self.assertFalse(x["visible_unsubscribe_link_candidate"])

    def test_32_valid_visible_subscribe_link_with_unsubscribe_text(self):
        x = scan(html='<a href="' + UNSUB + '">Unsubscribe</a>')
        self.assertTrue(x["visible_unsubscribe_link_candidate"])

    def test_33_nested_opt_out_anchor_text_is_detected(self):
        x = scan(html='<a href="' + UNSUB + '"><span>Opt out</span> of updates</a>')
        self.assertTrue(x["visible_unsubscribe_link_candidate"])

    def test_34_separate_href_and_label_cannot_cross_validate(self):
        x = scan(html='<a href="' + UNSUB + '">Read</a><a href="https://example.invalid/article">Unsubscribe</a>')
        self.assertFalse(x["visible_unsubscribe_link_candidate"])

    def test_35_hidden_unsubscribe_anchor_is_not_visible(self):
        x = scan(html='<a hidden href="' + UNSUB + '">Unsubscribe</a>')
        self.assertFalse(x["visible_unsubscribe_link_candidate"])

    def test_36_unsubscribe_word_on_seller_link_is_not_optout(self):
        x = scan(html='<a href="https://zen12.com/unsubscribe">Unsubscribe</a>')
        self.assertFalse(x["visible_unsubscribe_link_candidate"])

    def test_37_form_button_is_not_a_visible_unsubscribe_anchor(self):
        x = scan(html='<form action="' + UNSUB + '"><button>Unsubscribe</button></form>')
        self.assertFalse(x["visible_unsubscribe_link_candidate"])

    def test_38_bogus_list_unsubscribe_buy_url_is_rejected(self):
        x = scan(unsub="https://example.invalid/buy")
        self.assertFalse(x["list_unsubscribe_header_candidate"])

    def test_39_list_unsubscribe_mailto_candidate(self):
        x = scan(unsub="mailto:unsubscribe@example.invalid")
        self.assertTrue(x["list_unsubscribe_header_candidate"])

    def test_40_list_unsubscribe_wordpress_https_candidate(self):
        x = scan(unsub="https://wordpress.com/subscriptions/unsubscribe?token=SYNTHETIC")
        self.assertTrue(x["list_unsubscribe_header_candidate"])

    def test_41_list_unsubscribe_seller_url_is_not_optout(self):
        x = scan(unsub="https://zen12.com/unsubscribe")
        self.assertFalse(x["list_unsubscribe_header_candidate"])

    def test_42_plain_unsubscribe_sentence_is_not_a_link(self):
        x = scan(plain="You can unsubscribe.")
        self.assertFalse(x["visible_unsubscribe_link_candidate"])

    def test_43_javascript_unsubscribe_link_is_unsafe(self):
        x = scan(html='<a href="javascript:unsubscribe()">Unsubscribe</a>')
        self.assertFalse(x["visible_unsubscribe_link_candidate"])
        self.assertIn("UNSAFE_LINK_SCHEME", x["holds"])

    def test_44_case_insensitive_unsubscribe_text(self):
        x = scan(html='<a href="' + UNSUB + '">UNSUBSCRIBE</a>')
        self.assertTrue(x["visible_unsubscribe_link_candidate"])

    def test_45_unrelated_follow_link_is_not_optout(self):
        x = scan(html='<p>Unsubscribe any time.</p><a href="https://wordpress.com/follow/">Follow</a>')
        self.assertFalse(x["visible_unsubscribe_link_candidate"])


class CSSAndPrivacy(unittest.TestCase):
    def test_46_remote_image_inside_style_block_counted(self):
        x = scan(html='<style>.x{background:url(https://images.example.invalid/p.png)}</style>')
        self.assertEqual(x["remote_image_count"], 1)

    def test_47_no_remote_images_without_resources(self):
        x = scan(html="<p>Plain content</p>")
        self.assertEqual(x["remote_image_count"], 0)

    def test_48_does_not_report_a_token(self):
        x = scan(html='<a href="' + UNSUB + '">Unsubscribe</a>')
        report = json.dumps(x)
        self.assertNotIn("NEVER_REAL", report)
        self.assertNotIn("not-an-actual-recipient", report)

    def test_49_does_not_return_source_links_in_report(self):
        x = scan(html='<form action="' + SELLER + '"></form>')
        self.assertNotIn(SELLER, json.dumps(x))

    def test_50_publisher_postal_unverified_even_when_synthetic_present(self):
        x = scan(plain=POSTAL, html="<p>" + POSTAL + "</p>")
        self.assertFalse(x["legal_compliance_certified"])
        self.assertIn("POSTAL_AND_UNSUBSCRIBE_FUNCTION_REQUIRE_HUMAN_RECEIPT_QA", x["holds"])

    def test_51_campaign_preserved(self):
        self.assertEqual(len(ISSUES), 6)
        self.assertEqual([i["number"] for i in ISSUES if i["kind"] == "commercial-review-pending"], [3, 5])

    def test_52_no_network_or_mail_transmission_in_inspector(self):
        src = MODULE.read_text(encoding="utf-8")
        for bad in ("import requests", "import socket", "import smtplib", "urlopen(", "sendmail("):
            self.assertNotIn(bad, src)


if __name__ == "__main__":
    unittest.main()
