"""Offline synthetic-only tests; DO NOT use subscriber email or live Jetpack."""
import importlib.util
import json
from email.message import EmailMessage
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "r33-received-mime-proof" / "native_mime_proof.py"
SPEC = importlib.util.spec_from_file_location("fv_native_mime_proof", MODULE_PATH)
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)

SUBJECT = "The mind is not a camera"
POSTAL = "123 Fictional Postal Lane, Test City, CA 00000"


def fake_eml(
    *, body="Read the archives. Unsubscribe: https://example.invalid/u/secret123",
    html=None, from_name="Final Vestige", subject=SUBJECT,
    header_url=True, one_click=True, disclosure=False,
):
    message = EmailMessage()
    message["From"] = f"{from_name} <donotreply@wordpress.com>"
    message["To"] = "private-recipient@example.invalid"
    message["Subject"] = subject
    if header_url:
        message["List-Unsubscribe"] = "<https://example.invalid/unsubscribe/secret123>"
    if one_click:
        message["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    if disclosure:
        body += " If you buy through our guide, we may earn a commission."
    message.set_content(body)
    if html is not None:
        message.add_alternative(html, subtype="html")
    return message.as_bytes()


def inspect(data=None, **kwargs):
    return proof.analyze_mime(fake_eml() if data is None else data, expected_subject=SUBJECT, **kwargs)


class ReceivedMimeCandidateTests(unittest.TestCase):
    def test_exact_subject(self):
        self.assertTrue(inspect()["subject_exact_match"])

    def test_wrong_subject_stays_hold(self):
        p = inspect(fake_eml(subject="Unrelated subject"))
        self.assertFalse(p["subject_exact_match"])
        self.assertEqual(p["release"], "HOLD_UNSENT")

    def test_sender_display(self):
        self.assertTrue(inspect()["sender_display_match"])

    def test_wrong_display_name(self):
        self.assertFalse(inspect(fake_eml(from_name="Imposter"))["sender_display_match"])

    def test_sender_is_not_authentication(self):
        self.assertFalse(inspect()["legitimate_delivery_proven"])

    def test_html_and_plain_detected(self):
        p = inspect(fake_eml(html="<p>Archive dispatch</p>"))
        self.assertTrue(p["has_plain_text"])
        self.assertTrue(p["has_html"])

    def test_plain_only(self):
        self.assertFalse(inspect()["has_html"])

    def test_header_link(self):
        self.assertTrue(inspect()["has_header_unsubscribe_https"])

    def test_missing_header_link(self):
        self.assertFalse(inspect(fake_eml(header_url=False))["has_header_unsubscribe_https"])

    def test_rfc8058_header_declaration(self):
        self.assertTrue(inspect()["has_rfc8058_one_click_declaration"])

    def test_one_click_cannot_exist_without_unsubscribe_link(self):
        self.assertFalse(inspect(fake_eml(header_url=False))["has_rfc8058_one_click_declaration"])

    def test_one_click_cannot_exist_without_declaration(self):
        self.assertFalse(inspect(fake_eml(one_click=False))["has_rfc8058_one_click_declaration"])

    def test_html_unsubscribe_link_with_visible_label(self):
        p = inspect(fake_eml(body="Archive dispatch", html='<a href="https://example.invalid/u/secret">Unsubscribe</a>'))
        self.assertTrue(p["has_body_unsubscribe_https"])

    def test_plaintext_unsubscribe_link(self):
        self.assertTrue(inspect()["has_body_unsubscribe_https"])

    def test_unlinked_unsubscribe_text_fails(self):
        self.assertFalse(inspect(fake_eml(body="Unsubscribe anytime."))["has_body_unsubscribe_https"])

    def test_javascript_unsubscribe_not_accepted(self):
        html = '<a href="javascript:alert(1)">Unsubscribe</a>'
        self.assertFalse(inspect(fake_eml(body="Read.", html=html))["has_body_unsubscribe_https"])

    def test_http_unsubscribe_not_accepted(self):
        html = '<a href="http://example.invalid/u">Unsubscribe</a>'
        self.assertFalse(inspect(fake_eml(body="Read.", html=html))["has_body_unsubscribe_https"])

    def test_email_password_url_not_accepted(self):
        html = '<a href="https://user:password@example.invalid/u">Unsubscribe</a>'
        self.assertFalse(inspect(fake_eml(body="Read.", html=html))["has_body_unsubscribe_https"])

    def test_postal_unknown_without_private_marker(self):
        self.assertIsNone(inspect()["founder_supplied_postal_marker_present"])

    def test_postal_marker_present_still_not_verified(self):
        p = inspect(fake_eml(body=POSTAL + "\nUnsubscribe: https://example.invalid/u"), postal_marker=POSTAL)
        self.assertTrue(p["founder_supplied_postal_marker_present"])
        self.assertFalse(p["postal_address_legally_verified"])

    def test_automattic_postal_does_not_verify_business_address(self):
        p = inspect(fake_eml(body="Automattic P.O. Box\nUnsubscribe: https://example.invalid/u"), postal_marker=POSTAL)
        self.assertFalse(p["founder_supplied_postal_marker_present"])
        self.assertFalse(p["postal_address_legally_verified"])

    def test_draft_sentinel_detected(self):
        self.assertTrue(inspect(fake_eml(body="DO NOT PUBLISH OR EMAIL — DRAFT ONLY"))["draft_or_inactive_placeholder_visible"])

    def test_disabled_guide_placeholder_detected(self):
        self.assertTrue(inspect(fake_eml(body="[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]"))["draft_or_inactive_placeholder_visible"])

    def test_clean_body_no_draft_sentinel(self):
        self.assertFalse(inspect()["draft_or_inactive_placeholder_visible"])

    def test_commercial_disclosure_present(self):
        self.assertTrue(inspect(fake_eml(disclosure=True), commercial=True)["commercial_disclosure_present"])

    def test_missing_commercial_disclosure(self):
        p = inspect(commercial=True)
        self.assertFalse(p["commercial_disclosure_present"])
        self.assertEqual(p["merchant_release"], "HOLD_MERCHANT")

    def test_editorial_disclosure_not_applicable(self):
        self.assertIsNone(inspect()["commercial_disclosure_present"])

    def test_commercial_always_merchant_hold_even_with_disclosure(self):
        p = inspect(fake_eml(disclosure=True), commercial=True)
        self.assertEqual(p["merchant_release"], "HOLD_MERCHANT")
        self.assertEqual(p["release"], "HOLD_UNSENT")

    def test_unsubscribe_shape_is_not_functional_proof(self):
        self.assertFalse(inspect()["unsubscribe_endpoint_functionally_tested"])

    def test_no_affiliate_permission_assumed(self):
        self.assertFalse(inspect(commercial=True)["affiliate_email_permission_verified"])

    def test_no_audience_consent_assumed(self):
        self.assertFalse(inspect()["consented_eligible_audience_verified"])

    def test_no_raw_pii_or_urls_in_report(self):
        rendered = json.dumps(inspect())
        for value in ["private-recipient", "donotreply@wordpress.com", "secret123", "example.invalid", POSTAL]:
            self.assertNotIn(value, rendered)

    def test_report_has_fingerprint(self):
        p = inspect()
        self.assertRegex(p["mime_sha256"], r"^[0-9a-f]{64}$")
        self.assertGreater(p["bytes"], 0)

    def test_empty_input_fails(self):
        with self.assertRaises(ValueError):
            inspect(b"")

    def test_oversized_input_fails(self):
        with self.assertRaises(ValueError):
            inspect(b"x" * (proof.MAX_MIME_BYTES + 1))

    def test_missing_from_header_fails(self):
        with self.assertRaises(ValueError):
            inspect(b"Subject: One\n\nBody")

    def test_missing_subject_header_fails(self):
        with self.assertRaises(ValueError):
            inspect(b"From: Final Vestige <test@example.invalid>\n\nBody")

    def test_no_expected_subject_fails(self):
        with self.assertRaises(ValueError):
            proof.analyze_mime(fake_eml(), expected_subject=" ")

    def test_attachment_not_used_as_postal_or_disclosure(self):
        msg = EmailMessage()
        msg["From"] = "Final Vestige <donotreply@wordpress.com>"
        msg["Subject"] = SUBJECT
        msg.set_content("Only an ordinary note")
        msg.add_attachment((POSTAL+" may earn a commission.").encode(), maintype="text", subtype="plain", filename="not-a-footer.txt")
        p = inspect(msg.as_bytes(), postal_marker=POSTAL, commercial=True)
        self.assertFalse(p["founder_supplied_postal_marker_present"])
        self.assertFalse(p["commercial_disclosure_present"])

    def test_cli_exit_code_is_always_nonzero_even_on_structural_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.eml"
            path.write_bytes(fake_eml(disclosure=True))
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), str(path), "--expected-subject", SUBJECT],
                capture_output=True, text=True, check=False, timeout=8,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn('"HOLD_UNSENT"', result.stdout)
            self.assertNotIn("private-recipient", result.stdout)

    def test_cli_report_contains_no_raw_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.eml"
            report = Path(tmp) / "safe.json"
            path.write_bytes(fake_eml())
            r = subprocess.run(
                [sys.executable, str(MODULE_PATH), str(path), "--expected-subject", SUBJECT,
                 "--report", str(report)],
                capture_output=True, text=True, timeout=8, check=False,
            )
            self.assertEqual(r.returncode, 2)
            self.assertEqual(r.stdout, "")
            self.assertEqual(json.loads(report.read_text())["release"], "HOLD_UNSENT")
            self.assertNotIn("private-recipient", report.read_text())


if __name__ == "__main__":
    unittest.main()
