"""R57: adversarial synthetic MIME probes for the R56 receive-only inspector.

Synthetic fixtures only. Zero live subscribers, messages, affiliate URLs, or sends.
The inspector deliberately NEVER certifies legal compliance or authorization.
"""
from __future__ import annotations

import importlib.util
import json
from email.message import EmailMessage
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "r56-mime-evidence" / "mime_inspector.py"
spec = importlib.util.spec_from_file_location("fv_r57_r56_under_test", MOD)
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
DISCLOSURE = "Final Vestige may earn a commission from a qualifying purchase."
POSTAL = "Dummy Postal Address 12, Suite 4, Fictional City 90000"
UNSUB = "https://wordpress.com/unsubscribe/?token=SYNTHETIC_TOKEN"
SELLER = "https://zen12.com/hnp"


def fabricate(html=None, *, issue=3, plain="Synthetic editorial example.", header=False):
    mail = EmailMessage()
    mail["From"] = "Final Vestige <no-reply@wordpress.com>"
    mail["To"] = "fake-only@example.invalid"
    mail["Subject"] = MANIFEST["issues"][issue - 1]["subject"]
    if header:
        mail["List-Unsubscribe"] = "<" + UNSUB + ">"
    mail.set_content(plain)
    if html is not None:
        mail.add_alternative(html, subtype="html")
    return mail.as_bytes()


def scan(html=None, *, issue=3, plain="Synthetic editorial example.", header=False):
    return inspector.inspect_bytes(
        fabricate(html, issue=issue, plain=plain, header=header),
        MANIFEST["issues"][issue - 1], origin="synthetic", postal_address=POSTAL
    )


class MalformedURLRobustness(unittest.TestCase):
    def test_01_invalid_ipv6_href_does_not_raise(self):
        x = scan('<p>Unsubscribe</p><a href="https://[broken">See info</a>')
        self.assertEqual(x["malformed_link_count"], 1)

    def test_02_invalid_ipv6_is_an_explicit_hold(self):
        self.assertIn("MALFORMED_LINK_HUMAN_REVIEW",
                      scan('<a href="https://[broken">Click</a>')["holds"])

    def test_03_malformed_unsubscribe_is_not_an_optout_candidate(self):
        x = scan('<a href="https://[broken/unsubscribe">Unsubscribe</a>')
        self.assertFalse(x["visible_unsubscribe_link_candidate"])

    def test_04_malformed_and_valid_unsubscribe_do_not_crash(self):
        x = scan('<a href="https://[bad">Click</a><a href="' + UNSUB + '">Unsubscribe</a>')
        self.assertTrue(x["visible_unsubscribe_link_candidate"])
        self.assertEqual(x["malformed_link_count"], 1)

    def test_05_safe_link_scheme_rejects_invalid_ipv6(self):
        self.assertEqual(inspector.safe_url_scheme("https://[bad"), "")

    def test_06_safe_link_scheme_retains_https(self):
        self.assertEqual(inspector.safe_url_scheme("https://example.invalid/unsubscribe"), "https")

    def test_07_broken_href_does_not_leak_to_report(self):
        x = scan('<a href="https://[PRIVATE_TOKEN_HIDDEN">Unsubscribe</a>')
        self.assertNotIn("PRIVATE_TOKEN_HIDDEN", json.dumps(x))

    def test_08_empty_href_is_not_malformed_ipv6(self):
        x = scan('<a href="">Read</a>')
        self.assertEqual(x["malformed_link_count"], 0)


class HiddenRouteCoverage(unittest.TestCase):
    def test_09_hidden_display_none_seller_anchor_is_counted(self):
        x = scan('<div style="display:none"><a href="' + SELLER + '">Buy</a></div>')
        self.assertEqual(x["direct_seller_link_count"], 1)

    def test_10_hidden_visibility_seller_anchor_is_counted(self):
        x = scan('<div style="visibility:hidden"><a href="' + SELLER + '">Buy</a></div>')
        self.assertEqual(x["direct_seller_link_count"], 1)

    def test_11_hidden_opacity_seller_anchor_is_counted(self):
        x = scan('<div style="opacity:0"><a href="' + SELLER + '">Buy</a></div>')
        self.assertEqual(x["direct_seller_link_count"], 1)

    def test_12_hidden_font_size_seller_anchor_is_counted(self):
        x = scan('<span style="font-size:0px"><a href="' + SELLER + '">Buy</a></span>')
        self.assertEqual(x["direct_seller_link_count"], 1)

    def test_13_hidden_seller_still_causes_commercial_hold(self):
        x = scan('<div hidden><a href="' + SELLER + '">Buy</a></div>')
        self.assertIn("DIRECT_MERCHANT_LINK_BYPASSES_REVIEWED_GUIDE", x["holds"])

    def test_14_hidden_javascript_anchor_is_unsafe(self):
        x = scan('<div hidden><a href="javascript:alert(1)">Unsubscribe</a></div>')
        self.assertEqual(x["unsafe_link_scheme_count"], 1)

    def test_15_hidden_javascript_is_hold(self):
        x = scan('<a style="display:none" href="javascript:alert(1)">Open</a>')
        self.assertIn("UNSAFE_LINK_SCHEME", x["holds"])

    def test_16_hidden_optout_does_not_count_as_visible(self):
        x = scan('<p>Unsubscribe</p><div hidden><a href="' + UNSUB + '">Unsubscribe</a></div>')
        self.assertFalse(x["visible_unsubscribe_link_candidate"])

    def test_17_valid_visible_optout_remains_candidate_not_proof(self):
        x = scan('<a href="' + UNSUB + '">Unsubscribe</a>')
        self.assertTrue(x["visible_unsubscribe_link_candidate"])
        self.assertFalse(x["unsubscription_functionally_verified"])

    def test_18_seller_spoof_suffix_is_not_seller(self):
        x = scan('<a href="https://zen12.com.evil.example/unsubscribe">See</a>')
        self.assertEqual(x["direct_seller_link_count"], 0)

    def test_19_seller_subdomain_is_seller(self):
        x = scan('<a href="https://support.zen12.com/help">See</a>')
        self.assertEqual(x["direct_seller_link_count"], 1)

    def test_20_hypnosislive_specific_product_is_seller(self):
        x = scan('<a href="https://hypnosislive.com/mental-skills/total-focus">See</a>')
        self.assertEqual(x["direct_seller_link_count"], 1)

    def test_21_inspire3_catalog_link_is_seller(self):
        x = scan('<a href="https://inspire3.com/">See</a>')
        self.assertEqual(x["direct_seller_link_count"], 1)

    def test_22_plaintext_seller_source_link_is_counted(self):
        x = scan(plain="See https://zen12.com/hnp in the source record.")
        self.assertEqual(x["direct_seller_link_count"], 1)


class InvisibleDisclosureAndTracking(unittest.TestCase):
    def test_23_css_opacity_zero_cannot_satisfy_disclosure(self):
        x = scan('<p style="opacity:0">' + DISCLOSURE + '</p><p>Nothing visible.</p>')
        self.assertFalse(x["disclosure_in_visible_body"])

    def test_24_css_opacity_decimal_zero_cannot_satisfy_disclosure(self):
        x = scan('<p style="opacity: 0.0">' + DISCLOSURE + '</p><p>Visible facts.</p>')
        self.assertFalse(x["disclosure_in_visible_first_85_words"])

    def test_25_css_font_zero_cannot_satisfy_disclosure(self):
        x = scan('<span style="font-size:0px">' + DISCLOSURE + '</span><p>Visible facts.</p>')
        self.assertFalse(x["disclosure_in_visible_body"])

    def test_26_css_font_zero_percent_cannot_satisfy_disclosure(self):
        x = scan('<span style="font-size:0%">' + DISCLOSURE + '</span><p>Visible facts.</p>')
        self.assertFalse(x["disclosure_in_visible_body"])

    def test_27_aria_hidden_whitespace_cannot_satisfy_disclosure(self):
        x = scan('<p aria-hidden=" true ">' + DISCLOSURE + '</p><p>Visible facts.</p>')
        self.assertFalse(x["disclosure_in_visible_body"])

    def test_28_half_opacity_is_not_automatically_hidden(self):
        x = scan('<p style="opacity:0.5">' + DISCLOSURE + '</p>')
        self.assertTrue(x["disclosure_in_visible_body"])

    def test_29_nonzero_font_is_not_automatically_hidden(self):
        x = scan('<p style="font-size:0.5rem">' + DISCLOSURE + '</p>')
        self.assertTrue(x["disclosure_in_visible_first_85_words"])

    def test_30_visible_disclosure_is_still_detected(self):
        x = scan('<p>' + DISCLOSURE + '</p>')
        self.assertTrue(x["disclosure_in_visible_first_85_words"])

    def test_31_remote_img_counted(self):
        x = scan('<img src="https://example.invalid/pixel.gif" alt="">')
        self.assertGreaterEqual(x["remote_image_count"], 1)

    def test_32_hidden_remote_img_still_counted(self):
        x = scan('<div hidden><img src="https://example.invalid/pixel.gif" alt=""></div>')
        self.assertGreaterEqual(x["remote_image_count"], 1)

    def test_33_css_remote_background_counted(self):
        x = scan('<td style="background-image:url(https://example.invalid/pixel.gif)">Hello</td>')
        self.assertGreaterEqual(x["remote_image_count"], 1)

    def test_34_css_quoted_remote_background_counted(self):
        x = scan("<td style=\"background:url('https://example.invalid/pixel.gif')\">Hello</td>")
        self.assertGreaterEqual(x["remote_image_count"], 1)

    def test_35_no_remote_image_when_none_present(self):
        x = scan('<p>' + DISCLOSURE + '</p>')
        self.assertEqual(x["remote_image_count"], 0)


class StructuralSafety(unittest.TestCase):
    def test_36_commercial_all_hold_even_with_disclosure(self):
        x = scan('<p>' + DISCLOSURE + '</p>')
        self.assertFalse(x["send_allowed"])
        self.assertFalse(x["legal_compliance_certified"])

    def test_37_received_label_is_not_independent_attestation(self):
        raw = fabricate('<p>' + DISCLOSURE + '</p>')
        x = inspector.inspect_bytes(raw, MANIFEST["issues"][2], origin="received")
        self.assertFalse(x["source_is_received_message_independently_attested"])

    def test_38_merchant_permissions_never_promoted(self):
        x = scan('<p>' + DISCLOSURE + '</p>')
        self.assertFalse(x["merchant_email_permission_verified"])
        self.assertFalse(x["approved_first_party_product_guide_live"])

    def test_39_source_is_unchanged_six_issue_four_two(self):
        items = MANIFEST["issues"]
        self.assertEqual([x["number"] for x in items], [1, 2, 3, 4, 5, 6])
        self.assertEqual([x["number"] for x in items if x["kind"]=="commercial-review-pending"], [3, 5])

    def test_40_report_does_not_expose_test_recipient_or_token(self):
        x = scan('<a href="' + UNSUB + '">Unsubscribe</a>')
        out = json.dumps(x)
        self.assertNotIn("fake-only", out)
        self.assertNotIn("SYNTHETIC_TOKEN", out)

    def test_41_no_socket_or_email_sending_imports(self):
        src = MOD.read_text(encoding="utf-8")
        for forbidden in ("import smtplib", "import requests", "import socket", "sendmail(", "urlopen("):
            self.assertNotIn(forbidden, src)

    def test_42_oversize_remains_hard_failure(self):
        with self.assertRaisesRegex(ValueError, "MESSAGE_TOO_LARGE"):
            inspector.inspect_bytes(b"0"*(inspector.MAX_BYTES+1), MANIFEST["issues"][2])

    def test_43_unreplaced_postal_placeholder_stays_on_hold(self):
        x = scan(plain="[[VALID_POSTAL_ADDRESS_REQUIRED]]")
        self.assertIn("UNREPLACED_RELEASE_PLACEHOLDER", x["holds"])

    def test_44_no_claim_of_received_preview_from_synthetic(self):
        x = scan('<p>' + DISCLOSURE + '</p>')
        self.assertIn("NO_ACTUAL_RECEIVED_EMAIL_EVIDENCE", x["holds"])
        self.assertFalse(x["founder_final_send_approval"])

    def test_45_legal_footer_cannot_be_replaced_by_merchant_address(self):
        x = scan(plain="The seller's address is 20-22 Wenlock Street, London.")
        self.assertFalse(x["postal_exact_match_to_local_private_value"])

    def test_46_missing_real_business_address_stays_on_hold(self):
        x = inspector.inspect_bytes(fabricate(), MANIFEST["issues"][2], postal_address=None)
        self.assertIn("VERIFIED_FINAL_VESTIGE_POSTAL_ADDRESS_NOT_PRESENT", x["holds"])


if __name__ == "__main__":
    unittest.main()
