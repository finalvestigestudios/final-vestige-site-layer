"""Synthetic EML tests ONLY. Never treat fixtures as a real Jetpack send."""
import unittest
from email.message import EmailMessage
from received_email_inspector import inspect_bytes, HOLD

P = "Record. Final Vestige Studios, 123 Test Street, Town, CA 90000. Unsubscribe: https://finalvestige.com/unsubscribe/abc"
H = '<html><body><p>Record. Final Vestige Studios, 123 Test Street, Town, CA 90000.</p><a href="https://finalvestige.com/unsubscribe/abc">Unsubscribe</a><p><a href="https://finalvestige.com/focus/">Read more</a></p></body></html>'

def sample(p=P, h=H, subject="Evidence matters", header=True):
    m = EmailMessage()
    m["From"] = "Final Vestige <donotreply@wordpress.com>"
    m["To"] = "Subscriber <reader@example.org>"
    m["Date"] = "Wed, 11 Nov 2026 12:00:00 +0000"
    m["Message-ID"] = "<fixture@wordpress.com>"
    m["Subject"] = subject
    if header: m["List-Unsubscribe"] = "<https://finalvestige.com/unsubscribe/abc>"
    m.set_content(p)
    m.add_alternative(h, subtype="html")
    return m.as_bytes()

class PrivateMIME(unittest.TestCase):
    def test_positive_is_still_hold(self):
        x = inspect_bytes(sample())
        self.assertTrue(x["structural_checks_pass"])
        self.assertEqual(x["release_state"], HOLD)
        self.assertFalse(x["actual_jetpack_receipt_verified"])
    def test_no_pii_in_report(self):
        x = str(inspect_bytes(sample()))
        for secret in ("reader@", "donotreply@", "123 Test", "fixture@"):
            self.assertNotIn(secret, x)
    def test_placeholder_blocked(self):
        x = inspect_bytes(sample(p=P.replace("123 Test Street", "[[REQUIRED]]")))
        self.assertFalse(x["checks"]["no_release_placeholders"])
    def test_missing_optout_body_label(self):
        x = inspect_bytes(sample(p=P.replace("Unsubscribe:", "Options:"), h=H.replace(">Unsubscribe<", ">Options<")))
        self.assertFalse(x["checks"]["visible_optout_instruction"])
    def test_unsafe_html_rejected(self):
        x = inspect_bytes(sample(h=H+"<script>bad()</script>"))
        self.assertFalse(x["checks"]["no_html_script_iframe_form"])
    def test_missing_postal_rejected(self):
        x = inspect_bytes(sample(p=P.replace("123 Test Street", "UNKNOWN"), h=H.replace("123 Test Street", "UNKNOWN")))
        self.assertFalse(x["checks"]["postal_candidate_in_visible_body"])
    def test_missing_unsub_target_rejected(self):
        x = inspect_bytes(sample(h=H.replace("https://finalvestige.com/unsubscribe/abc", "#dummy")))
        self.assertFalse(x["checks"]["https_optout_link_candidate"])
    def test_header_cannot_replace_body(self):
        x = inspect_bytes(sample(h=H.replace("https://finalvestige.com/unsubscribe/abc", "#dummy")))
        self.assertTrue(x["checks"]["list_unsubscribe_header_present"])
        self.assertFalse(x["checks"]["https_optout_link_candidate"])
    def test_missing_header_reported(self):
        self.assertFalse(inspect_bytes(sample(header=False))["checks"]["list_unsubscribe_header_present"])
    def test_oversize_rejected(self):
        with self.assertRaises(ValueError): inspect_bytes(b"x" * 2_000_001)
    def test_invalid_type_rejected(self):
        with self.assertRaises(ValueError): inspect_bytes("not bytes")
    def test_subject_placeholder_rejected(self):
        self.assertFalse(inspect_bytes(sample(subject="[[SUBJECT_REQUIRED]]"))["checks"]["subject_present"])

if __name__ == "__main__":
    unittest.main()
