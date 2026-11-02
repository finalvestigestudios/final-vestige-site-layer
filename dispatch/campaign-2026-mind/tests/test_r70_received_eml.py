"""Native, synthetic-only adversarial validation of the R70 .eml inspector.

No real subscriber addresses, actual MIME, merchant links, secrets, or tokens.
Run: python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -p test_r70_received_eml.py -v
"""
from email.message import EmailMessage
import importlib.util
import json
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "r70-received-mime" / "inspect_received_eml.py"
spec = importlib.util.spec_from_file_location("fv_dispatch_r70_received_eml", SOURCE)
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)

ADDRESS = "P.O. Box 123, Example City, CA 90000"  # NON-REAL TEST PLACEHOLDER
SUBJECT = "A source is not a verdict"
DISCLOSURE = "Final Vestige may earn a commission if you purchase through a link in the guide."

def sample(
    plain="A useful historical note.\nUnsubscribe: https://newsletter.example.invalid/unsubscribe/TOKEN\n"
          + ADDRESS,
    html=None,
    subject=SUBJECT,
    header=False,
    sender="Final Vestige <donotreply@wordpress.com>",
    recipient="supersecret@example.invalid",
):
    m = EmailMessage()
    if subject is not None:
        m["Subject"] = subject
    m["From"] = sender
    m["To"] = recipient
    if header:
        m["List-Unsubscribe"] = "<https://newsletter.example.invalid/unsubscribe/TOKEN>"
        m["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    m.set_content(plain)
    if html is not None:
        m.add_alternative(html, subtype="html")
    return m.as_bytes()

def inspect(raw=None, edition="01", subject=SUBJECT, address=ADDRESS):
    return auditor.audit_bytes(
        raw if raw is not None else sample(), edition=edition,
        expected_subject=subject, publisher_postal_address=address
    )

class ReceivedMimeContract(unittest.TestCase):
    def test_original_suite_is_not_replaced(self):
        self.assertTrue((SOURCE.parents[1] / "tests" / "test_campaign.py").is_file())

    def test_plain_mail_reports_limited_evidence(self):
        x = inspect()
        self.assertTrue(x["signals"]["subject_present"])
        self.assertTrue(x["signals"]["plain_text_part_present"])
        self.assertIs(x["signals"]["postal_text_matches_private_publisher_reference"], True)
        self.assertIs(x["send_allowed"], False)
        self.assertEqual(x["release_status"], "HOLD_UNSENT")

    def test_never_claims_actual_delivery_from_bytes(self):
        x = inspect()
        self.assertEqual(x["evidence_level"], "UNAUTHENTICATED_LOCAL_MIME_INSPECTION_ONLY")
        self.assertTrue(x["synthetic_or_real_not_determined"])
        self.assertIn("RECEIPT_PROVENANCE_NOT_AUTHENTICATED_BY_LOCAL_PARSER", x["blockers"])

    def test_unsubscribe_found_does_not_remove_functional_hold(self):
        x = inspect()
        self.assertTrue(x["signals"]["plain_text_optout_and_https_present"])
        self.assertIn("OPT_OUT_REACHABILITY_AND_SUCCESS_REQUIRE_AUTHORIZED_HUMAN_TEST", x["blockers"])

    def test_one_click_header_is_not_functional_proof(self):
        x = inspect(sample(header=True))
        self.assertTrue(x["signals"]["list_unsubscribe_post_one_click_declared"])
        self.assertTrue(x["signals"]["list_unsubscribe_header_present"])
        self.assertFalse(x["send_allowed"])

    def test_html_anchor_has_visible_label(self):
        html = '<html lang="en"><body><p>Research first.</p><a href="https://newsletter.example.invalid/u/TOKEN">Unsubscribe</a><p>' + ADDRESS + '</p></body></html>'
        x = inspect(sample(html=html))
        self.assertTrue(x["signals"]["unsubscribe_labeled_https_link_present"])
        self.assertTrue(x["signals"]["html_lang_en_present"])
        self.assertFalse(x["signals"]["html_interactive_markup_detected"])

    def test_link_without_unsubscribe_label_not_pass(self):
        html = '<html lang="en"><body><a href="https://newsletter.example.invalid/u/TOKEN">Click</a></body></html>'
        x = inspect(sample(plain="Hi", html=html))
        self.assertFalse(x["signals"]["unsubscribe_labeled_https_link_present"])
        self.assertFalse(x["signals"]["plain_text_optout_and_https_present"])
        self.assertIn("NO_VISIBLE_OPT_OUT_DESTINATION_DETECTED", x["blockers"])

    def test_http_unsubscribe_not_counted_as_https(self):
        html = '<html><body><a href="http://newsletter.example.invalid/u">Unsubscribe</a></body></html>'
        x = inspect(sample(plain="Hi", html=html))
        self.assertFalse(x["signals"]["unsubscribe_labeled_https_link_present"])

    def test_invalid_url_malformed_credentials_rejected(self):
        self.assertFalse(auditor.valid_url("https://login:password@mailer.example.invalid/u"))
        self.assertFalse(auditor.valid_url("javascript:alert(1)"))
        self.assertFalse(auditor.valid_url("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"))

    def test_no_address_reference_is_null_and_hold(self):
        x = inspect(address=None)
        self.assertIsNone(x["signals"]["postal_text_matches_private_publisher_reference"])
        self.assertIn("PUBLISHER_ADDRESS_NOT_MATCHED_IN_RECEIVED_BODY", x["blockers"])

    def test_wrong_address_is_false(self):
        x = inspect(address="999 No Such St, Nowhere, NY 10000")
        self.assertIs(x["signals"]["postal_text_matches_private_publisher_reference"], False)

    def test_address_match_not_legal_ownership_proof(self):
        x = inspect()
        self.assertIn("POSTAL_ADDRESS_OWNERSHIP_AND_LEGAL_VALIDITY_REQUIRE_HUMAN_PROOF", x["blockers"])

    def test_early_disclosure_can_be_detected_without_approval(self):
        x = inspect(sample(plain=DISCLOSURE + " Content and an ordinary guide."), edition="03")
        self.assertTrue(x["signals"]["commercial_disclosure_within_first_55_visible_words"])
        self.assertIn("MERCHANT_EMAIL_CHANNEL_ACCEPTANCE_NOT_VERIFIED", x["blockers"])
        self.assertFalse(x["send_allowed"])

    def test_disclosure_after_fifty_five_words_fails(self):
        x = inspect(sample(plain=("evidence " * 60) + DISCLOSURE), edition="05")
        self.assertFalse(x["signals"]["commercial_disclosure_within_first_55_visible_words"])
        self.assertIn("DISCLOSURE_NOT_DETECTED_IN_FIRST_55_WORDS", x["blockers"])

    def test_editorial_issue_does_not_demand_commercial_disclosure(self):
        x = inspect()
        self.assertIsNone(x["signals"]["commercial_disclosure_within_first_55_visible_words"])
        self.assertNotIn("MERCHANT_EMAIL_CHANNEL_ACCEPTANCE_NOT_VERIFIED", x["blockers"])

    def test_current_merchant_sales_link_is_flagged_not_approved(self):
        x = inspect(sample(plain=DISCLOSURE + " Read https://zen12.com/hnp for seller claims."), edition="03")
        self.assertTrue(x["signals"]["merchant_domain_link_detected"])
        self.assertIn("MERCHANT_DOMAIN_LINK_REQUIRES_MANUAL_APPROVAL", x["blockers"])

    def test_html_merchant_url_detected_but_not_emitted(self):
        html = '<html lang="en"><a href="https://hypnosislive.com/mental-skills/total-focus?secret=TOKEN">Seller</a></html>'
        x = inspect(sample(plain=DISCLOSURE, html=html), edition="05")
        self.assertTrue(x["signals"]["merchant_domain_link_detected"])
        self.assertNotIn("TOKEN", json.dumps(x))

    def test_detects_placeholder(self):
        x = inspect(sample(plain="[[VALID_POSTAL_ADDRESS_REQUIRED]] and nothing else"))
        self.assertTrue(x["signals"]["hard_stop_placeholder_detected"])
        self.assertIn("UNRESOLVED_HARD_STOP_PLACEHOLDER_IN_BODY", x["blockers"])

    def test_detects_script_and_event_handler(self):
        html = '<html><body><a onclick="bad()" href="https://newsletter.example.invalid/u">unsubscribe</a><script>evil()</script></body></html>'
        x = inspect(sample(plain="Hi", html=html))
        self.assertTrue(x["signals"]["html_interactive_markup_detected"])
        self.assertIn("UNSAFE_OR_UNEXPECTED_HTML_ELEMENTS", x["blockers"])
        self.assertNotIn("evil()", json.dumps(x))

    def test_remote_image_is_not_delivery_evidence(self):
        html = '<html lang="en"><img src="https://tracker.example.invalid/pixel.png" width="1" height="1"></html>'
        x = inspect(sample(html=html))
        self.assertTrue(x["signals"]["remote_image_present"])
        self.assertFalse(x["send_allowed"])

    def test_privacy_no_address_subject_token_or_path_in_report(self):
        x = inspect(sample(subject="PRIVATE_SUBJECT_DONT_ECHO", recipient="personal.private@example.invalid",
                           plain="https://newsletter.example.invalid/unsubscribe/DO_NOT_ECHO\n" + ADDRESS),
                    subject=None)
        flat = json.dumps(x)
        for secret in ("PRIVATE_SUBJECT_DONT_ECHO", "personal.private", "DO_NOT_ECHO", ADDRESS):
            self.assertNotIn(secret, flat)
        self.assertIs(x["signals"]["subject_matches_selected_copy"], None)

    def test_incorrect_subject_is_flagged(self):
        x = inspect(sample(subject="Different headline"))
        self.assertFalse(x["signals"]["subject_matches_selected_copy"])
        self.assertIn("FINAL_SUBJECT_NOT_VERIFIED", x["blockers"])

    def test_bad_editions_are_rejected(self):
        for value in ("03-extra", "07", "0", "04\n"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                inspect(edition=value)

    def test_bad_inputs_rejected_without_echo(self):
        for raw in (b"", b"x" * (auditor.MAX_BYTES + 1), "not bytes"):
            with self.subTest(type=type(raw).__name__), self.assertRaises(ValueError):
                inspect(raw=raw)

    def test_html_only_can_still_be_reviewed(self):
        m = EmailMessage()
        m["Subject"] = SUBJECT
        m["From"] = "donotreply@wordpress.com"
        m.set_content('<html lang="en"><body>Visible text</body></html>', subtype="html")
        x = inspect(raw=m.as_bytes())
        self.assertFalse(x["signals"]["plain_text_part_present"])
        self.assertTrue(x["signals"]["html_part_present"])
        self.assertTrue(x["signals"]["visible_body_present"])

    def test_missing_visible_body_is_flagged(self):
        x = inspect(sample(plain=""))
        self.assertIn("SUBJECT_OR_VISIBLE_BODY_MISSING", x["blockers"])

    def test_synthetic_approval_never_unlocks(self):
        # This inspector has no mutable attestation state and no send operation.
        for issue in ("01", "02", "03", "04", "05", "06"):
            with self.subTest(issue=issue):
                x = inspect(edition=issue)
                self.assertFalse(x["send_allowed"])
                self.assertEqual(x["release_status"], "HOLD_UNSENT")

if __name__ == "__main__":
    unittest.main()
