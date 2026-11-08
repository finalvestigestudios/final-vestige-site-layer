"""R56: synthetic-only adversarial acceptance checks for redacted MIME triage."""
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import unittest
from email.message import EmailMessage

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATH = ROOT / "r56-mime-evidence" / "mime_inspector.py"
spec = importlib.util.spec_from_file_location("fv_dispatch_r56_mime", PATH)
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
POSTAL = "Authorized Business Postal Address, Suite 200, Sacramento CA 95814"
UNSUB = "https://wordpress.com/unsubscribe/?token=FAKE_FOR_UNIT_TEST_ONLY"
DOC = "This is an independently prepared editorial introduction. "
DISCLOSE = "Final Vestige may earn a commission if you later buy through a qualifying guide link."
GOOD_BODY = DOC + DISCLOSE + " " + POSTAL + " Unsubscribe any time."


def fabricate(*, issue=3, body=GOOD_BODY, html=None, subject=None,
              from_name="Final Vestige", header=True, attachment=False) -> bytes:
    msg = EmailMessage()
    msg["From"] = f"{from_name} <donotreply@wordpress.com>"
    msg["To"] = "private.recipient@example.test"
    msg["Subject"] = subject if subject is not None else MANIFEST["issues"][issue - 1]["subject"]
    if header:
        msg["List-Unsubscribe"] = f"<{UNSUB}>, <mailto:remove@example.test>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.set_content(body)
    if html is not None:
        msg.add_alternative(html, subtype="html")
    if attachment:
        msg.add_attachment(b"NOT A MESSAGE BODY", maintype="application",
                           subtype="octet-stream", filename="hidden.bin")
    return msg.as_bytes()


def scan(raw, issue=3, *, postal=POSTAL, origin="synthetic"):
    return inspector.inspect_bytes(
        raw, MANIFEST["issues"][issue - 1], postal_address=postal, origin=origin
    )


class ReceiptSafetyTests(unittest.TestCase):
    def test_01_manifest_six_issues_expected(self):
        self.assertEqual([e["number"] for e in MANIFEST["issues"]], list(range(1, 7)))

    def test_02_fabricated_email_matches_subject(self):
        self.assertTrue(scan(fabricate())["subject_equals_canonical"])

    def test_03_subject_mismatch_is_a_hold(self):
        r = scan(fabricate(subject="Miracle cure guaranteed!"))
        self.assertIn("SUBJECT_MISMATCH", r["holds"])

    def test_04_sender_display_is_checked_without_exposing_address(self):
        r = scan(fabricate(from_name="Wrong Publisher"))
        self.assertFalse(r["from_display_equals_final_vestige"])
        self.assertIn("SENDER_DISPLAY_MISMATCH", r["holds"])
        self.assertNotIn("donotreply@", json.dumps(r))

    def test_05_no_private_recipient_or_token_in_report(self):
        r = scan(fabricate())
        value = json.dumps(r)
        for secret in ("private.recipient", "FAKE_FOR_UNIT_TEST_ONLY",
                       "remove@example", "example.test"):
            self.assertNotIn(secret, value)

    def test_06_commercial_early_disclosure_visible_plaintext(self):
        r = scan(fabricate())
        self.assertTrue(r["disclosure_in_visible_first_85_words"])
        self.assertTrue(r["disclosure_in_visible_body"])

    def test_07_late_disclosure_is_not_early_disclosure(self):
        late = ("Facts and source method. " * 95) + DISCLOSE + " " + POSTAL
        r = scan(fabricate(body=late))
        self.assertFalse(r["disclosure_in_visible_first_85_words"])
        self.assertTrue(r["disclosure_in_visible_body"])
        self.assertIn("EARLY_COMMERCIAL_DISCLOSURE_MISSING", r["holds"])

    def test_08_hidden_html_disclosure_cannot_satisfy_visibility(self):
        html = ('<html><body><div style="display:none">' + DISCLOSE
                + '</div><p>Editorial only.</p><p>' + POSTAL
                + '</p><a href="' + UNSUB + '">Unsubscribe</a></body></html>')
        r = scan(fabricate(html=html))
        self.assertFalse(r["disclosure_in_visible_body"])
        self.assertFalse(r["disclosure_in_visible_first_85_words"])

    def test_09_visible_html_disclosure_is_detected(self):
        html = ('<html><body><p>' + DISCLOSE + '</p><p>' + POSTAL
                + '</p><a href="' + UNSUB + '">Unsubscribe</a></body></html>')
        r = scan(fabricate(html=html))
        self.assertTrue(r["disclosure_in_visible_first_85_words"])

    def test_10_postal_value_required_without_emitting_it(self):
        r = scan(fabricate(), postal=None)
        self.assertFalse(r["postal_exact_match_to_local_private_value"])
        self.assertIn("VERIFIED_FINAL_VESTIGE_POSTAL_ADDRESS_NOT_PRESENT", r["holds"])

    def test_11_valid_postal_matches_but_still_no_legal_signoff(self):
        r = scan(fabricate())
        self.assertTrue(r["postal_exact_match_to_local_private_value"])
        self.assertFalse(r["legal_compliance_certified"])
        self.assertFalse(r["send_allowed"])
        self.assertNotIn(POSTAL, json.dumps(r))

    def test_12_placeholder_never_counts_as_postal(self):
        r = scan(fabricate(body="[[VALID_POSTAL_ADDRESS_REQUIRED]]"), postal="[[VALID_POSTAL_ADDRESS_REQUIRED]]")
        self.assertFalse(r["postal_exact_match_to_local_private_value"])
        self.assertTrue(r["unreplaced_placeholder_in_visible_body"])

    def test_13_valid_unsubscribe_header_is_not_functionality_proof(self):
        r = scan(fabricate())
        self.assertTrue(r["list_unsubscribe_header_candidate"])
        self.assertFalse(r["unsubscription_functionally_verified"])

    def test_14_no_unsubscribe_candidate_is_flagged(self):
        r = scan(fabricate(body="Editorial copy without an unsubscribe option.", header=False))
        self.assertIn("UNSUBSCRIBE_MARKUP_CANDIDATE_ABSENT", r["holds"])

    def test_15_visible_unsubscribe_anchor_only_structural(self):
        html = '<html><body><p>' + DISCLOSE + '</p><a href="' + UNSUB + '">Unsubscribe here</a></body></html>'
        r = scan(fabricate(html=html, header=False))
        self.assertTrue(r["visible_unsubscribe_link_candidate"])
        self.assertFalse(r["unsubscription_functionally_verified"])

    def test_16_zen12_direct_seller_anchor_is_quarantined(self):
        html = '<body><p>' + DISCLOSE + '</p><a href="https://zen12.com/hnp">Seller</a></body>'
        r = scan(fabricate(body="No external seller", html=html))
        self.assertEqual(r["direct_seller_link_count"], 1)
        self.assertIn("DIRECT_MERCHANT_LINK_BYPASSES_REVIEWED_GUIDE", r["holds"])

    def test_17_tricky_merchant_subdomain_detected_not_fake_prefix(self):
        self.assertTrue(inspector.domain_is_seller("https://support.zen12.com/extra"))
        self.assertFalse(inspector.domain_is_seller("https://notzen12.com/"))
        self.assertFalse(inspector.domain_is_seller("https://zen12.com.evil.example/"))

    def test_18_unsafe_javascript_anchor_detected(self):
        html = '<body><a href="javascript:alert(1)">Unsubscribe</a></body>'
        r = scan(fabricate(body="ordinary words", html=html))
        self.assertEqual(r["unsafe_link_scheme_count"], 1)
        self.assertIn("UNSAFE_LINK_SCHEME", r["holds"])

    def test_19_tracking_image_is_observed_but_never_loaded(self):
        html = '<body><img src="https://example.test/track.gif"></body>'
        r = scan(fabricate(body="ordinary words", html=html))
        self.assertEqual(r["remote_image_count"], 1)

    def test_20_attachment_ignored_as_body(self):
        r = scan(fabricate(body="No disclosure", attachment=True))
        self.assertFalse(r["disclosure_in_visible_body"])
        self.assertFalse(r["has_text_html"])

    def test_21_even_received_origin_never_authorizes_sending(self):
        r = scan(fabricate(), origin="received")
        self.assertEqual(r["sample_origin_declared_by_operator"], "received")
        self.assertFalse(r["source_is_received_message_independently_attested"])
        self.assertFalse(r["send_allowed"])

    def test_22_synthetic_origin_explicitly_lacks_receipt_evidence(self):
        self.assertIn("NO_ACTUAL_RECEIVED_EMAIL_EVIDENCE",
                      scan(fabricate())["holds"])

    def test_23_noncommercial_editorial_still_on_hold(self):
        r = scan(fabricate(issue=1), issue=1)
        self.assertFalse(r["commercial_slot"])
        self.assertFalse(r["send_allowed"])
        self.assertNotIn("HOLD_MERCHANT_GUIDE_AND_TRACKING_UNVERIFIED", r["holds"])

    def test_24_only_third_and_fifth_are_commercial_slots(self):
        for number in range(1, 7):
            r = scan(fabricate(issue=number), issue=number)
            self.assertEqual(r["commercial_slot"], number in (3, 5))

    def test_25_oversized_mail_rejected_before_parse(self):
        with self.assertRaisesRegex(ValueError, "MESSAGE_TOO_LARGE"):
            scan(b"x" * (inspector.MAX_BYTES + 1))

    def test_26_invalid_origin_rejected(self):
        with self.assertRaisesRegex(ValueError, "UNRECOGNIZED_ORIGIN"):
            scan(fabricate(), origin="sent_by_me")

    def test_27_unknown_edition_rejected(self):
        bad = copy.deepcopy(MANIFEST["issues"][0])
        bad["number"] = 7
        with self.assertRaisesRegex(ValueError, "EDITION_NOT_IN_CAMPAIGN"):
            inspector.inspect_bytes(fabricate(issue=1), bad)

    def test_28_no_network_or_mail_sender_imports(self):
        src = PATH.read_text(encoding="utf-8")
        for forbidden in ("import smtplib", "import requests", "import socket",
                          "urlopen(", "requests.get(", "send_message(", "sendmail("):
            self.assertNotIn(forbidden, src)

    def test_29_untrusted_email_content_not_echoed_as_observation(self):
        body = "SECRET_PROFILE_ID_999 " + GOOD_BODY
        self.assertNotIn("SECRET_PROFILE_ID_999", json.dumps(scan(fabricate(body=body))))

    def test_30_report_keys_never_include_recipients_or_raw_content(self):
        r = scan(fabricate())
        self.assertFalse(any(k in r for k in ("to", "from", "body", "headers", "raw")))
        self.assertTrue(all(isinstance(h, str) and "@" not in h for h in r["holds"]))

    def test_31_missing_mime_parts_remains_hold(self):
        r = scan(b"From: Final Vestige <donotreply@wordpress.com>\nSubject: Test\n\n")
        self.assertFalse(r["has_text_plain"])
        self.assertFalse(r["has_text_html"])
        self.assertFalse(r["send_allowed"])

    def test_32_marker_in_html_comment_not_read_as_disclosure(self):
        html = '<body><!-- ' + DISCLOSE + ' --><p>Other stuff.</p></body>'
        r = scan(fabricate(html=html))
        self.assertFalse(r["disclosure_in_visible_body"])

    def test_33_reveal_pii_not_in_tests_or_checkout(self):
        r = scan(fabricate(html='<p><a href="https://zen12.com/hnp?email=SECRET123">Buy</a></p>'))
        self.assertNotIn("SECRET123", json.dumps(r))
        self.assertFalse(r["merchant_email_permission_verified"])


if __name__ == "__main__":
    unittest.main()
