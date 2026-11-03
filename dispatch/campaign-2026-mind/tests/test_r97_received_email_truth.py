"""Synthetic-only MIME tests: no real subscribers or purchaser data in this suite."""
import importlib.util
from email.message import EmailMessage
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "r97-received-email" / "received_email_truth.py"
spec = importlib.util.spec_from_file_location("received_email_truth", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fake(subject="The Dispatch: Issue 03", plain="Zen12: we may earn a commission. Unsubscribe anytime. SAFE_POSTAL_FIXTURE", html=None, unsub=True):
    m = EmailMessage()
    m["From"] = "sender@example.invalid"
    m["To"] = "reader@example.invalid"
    m["Date"] = "Tue, 03 Nov 2026 12:00:00 -0800"
    m["Subject"] = subject
    if unsub:
        m["List-Unsubscribe"] = "<https://example.invalid/u?secret=NO_EXPORT>"
        m["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    m.set_content(plain)
    if html is not None:
        m.add_alternative(html, subtype="html")
    return m.as_bytes()


class InspectorTests(unittest.TestCase):
    def test_valid_synthetic_commercial_still_hold(self):
        r = module.inspect_bytes(fake(html="<p>Zen12: we may earn a commission. Unsubscribe anytime. SAFE_POSTAL_FIXTURE</p>"), "03", "SAFE_POSTAL_FIXTURE")
        self.assertTrue(r["disclosure_all_representations"])
        self.assertTrue(r["postal_phrase_visible_all_representations"])
        self.assertEqual(r["launch_decision"], "HOLD_UNSENT_HOLD_MERCHANT")
        self.assertFalse(r["functional_unsubscribe_verified"])
        self.assertFalse(r["postal_qualification_verified"])

    def test_missing_html_disclosure_fails(self):
        r = module.inspect_bytes(fake(html="<p>Zen12 Unsubscribe SAFE_POSTAL_FIXTURE</p>"), "03")
        self.assertFalse(r["disclosure_all_representations"])

    def test_missing_plain_disclosure_fails(self):
        r = module.inspect_bytes(fake(plain="Zen12 Unsubscribe", html="<p>Zen12: may earn a commission</p>"), "03")
        self.assertFalse(r["disclosure_all_representations"])

    def test_wrong_sku_fails(self):
        r = module.inspect_bytes(fake(plain="Zen12: may earn a commission"), "05")
        self.assertFalse(r["offer_identity_all_representations"])

    def test_confirmation_not_welcome(self):
        r = module.inspect_bytes(fake(subject="Confirm your subscription", plain="Confirm subscription. Automattic mailing address", unsub=False))
        self.assertEqual(r["classification"], "CONFIRMATION_NOT_WELCOME")
        self.assertFalse(r["list_unsubscribe_header_present"])

    def test_welcome_only_candidate(self):
        r = module.inspect_bytes(fake(subject="Welcome", plain="Here is the Focus Fieldbook"))
        self.assertEqual(r["classification"], "WELCOME_CANDIDATE_NOT_DELIVERY_PROOF")
        self.assertFalse(r["campaign_delivery_verified"])

    def test_no_unsubscribe_header_not_inferred(self):
        r = module.inspect_bytes(fake(unsub=False), "03")
        self.assertFalse(r["list_unsubscribe_header_url_format"])

    def test_visible_unsubscribe_not_same_as_functional(self):
        r = module.inspect_bytes(fake(unsub=False), "03")
        self.assertTrue(r["visible_unsubscribe_wording_all_representations"])
        self.assertFalse(r["functional_unsubscribe_verified"])

    def test_header_url_secrets_never_exported(self):
        r = module.inspect_bytes(fake(), "03")
        self.assertNotIn("NO_EXPORT", str(r))
        self.assertNotIn("reader@", str(r))
        self.assertNotIn("sender@", str(r))

    def test_html_href_secret_never_exported(self):
        r = module.inspect_bytes(fake(html="<a href='https://example.invalid/?customer_token=SECRETCODE'>Zen12 may earn a commission. Unsubscribe</a>"), "03")
        self.assertNotIn("SECRETCODE", str(r))

    def test_script_text_ignored(self):
        r = module.inspect_bytes(fake(plain="Zen12 may earn a commission. Unsubscribe", html="<script>Zen12 may earn a commission</script><p>Zen12 Unsubscribe</p>"), "03")
        self.assertFalse(r["disclosure_all_representations"])

    def test_no_plain_html_only(self):
        m = EmailMessage()
        m["From"] = "sender@example.invalid"
        m["Date"] = "Tue, 03 Nov 2026 12:00:00 -0800"
        m["Subject"] = "Test"
        m.set_content("<p>Unsubscribe</p>", subtype="html")
        r = module.inspect_bytes(m.as_bytes())
        self.assertEqual(r["representations_present"], ["html"])

    def test_plain_only(self):
        r = module.inspect_bytes(fake())
        self.assertEqual(r["representations_present"], ["plain"])

    def test_bad_issue_rejected(self):
        with self.assertRaises(ValueError):
            module.inspect_bytes(fake(), "99")

    def test_oversized_rejected(self):
        with self.assertRaises(ValueError):
            module.inspect_bytes(b"x" * 5_000_001)

    def test_no_postal_phrase_no_implied_compliance(self):
        r = module.inspect_bytes(fake(), "03")
        self.assertFalse(r["postal_phrase_visible_all_representations"])

    def test_automattic_address_not_publisher(self):
        r = module.inspect_bytes(fake(plain="Automattic, 60 29th St. Unsubscribe"), "03", "SAFE_POSTAL_FIXTURE")
        self.assertFalse(r["postal_phrase_visible_all_representations"])

    def test_editorial_issue_disclosure_not_required(self):
        r = module.inspect_bytes(fake(), "02")
        self.assertFalse(r["commercial_issue"])
        self.assertIsNone(r["disclosure_all_representations"])
        self.assertEqual(r["launch_decision"], "HOLD_UNSENT")

    def test_attachments_ignored(self):
        m = EmailMessage()
        m["From"] = "sender@example.invalid"
        m["Date"] = "Tue, 03 Nov 2026 12:00:00 -0800"
        m["Subject"] = "The Dispatch"
        m.set_content("Unsubscribe")
        m.add_attachment(b"Secret buyer@example.invalid", maintype="application", subtype="octet-stream", filename="subscribers.csv")
        r = module.inspect_bytes(m.as_bytes())
        self.assertNotIn("buyer@", str(r))


if __name__ == "__main__":
    unittest.main()
