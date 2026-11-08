"""Synthetic-only adversarial checks. No real subscribers or network access."""
from email.message import EmailMessage
import unittest
from audit_received_email import audit_bytes, PDF_NAME


def make_mail(text="Hello", html=None, subject="Archive evidence", *, unsub=None, oneclick=False):
    m = EmailMessage()
    m["From"] = "PRIVATE <secret-sender@example.test>"
    m["To"] = "Private Person <secret-recipient@example.test>"
    m["Subject"] = subject
    if unsub:
        m["List-Unsubscribe"] = unsub
    if oneclick:
        m["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    m.set_content(text)
    if html is not None:
        m.add_alternative(html, subtype="html")
    return m.as_bytes()


class ReceivedMailEvidenceTests(unittest.TestCase):
    def test_no_pii_or_tokens_ever_appear_in_output(self):
        b = make_mail("https://foo.test/?subscriber=secret-123", "<a href='https://finalvestige.com/?token=supersecret'>Read</a>", unsub="<https://example.test/unsubscribe?secret=456>")
        r = str(audit_bytes(b, "editorial"))
        for word in ("secret-sender", "secret-recipient", "supersecret", "secret-123", "secret=456"):
            self.assertNotIn(word, r)

    def test_welcome_without_pdf_is_flagged(self):
        r = audit_bytes(make_mail("Welcome to our newsletter"), "welcome")
        self.assertIn("WELCOME_FIELD_BOOK_NOT_OBSERVED", r["review_flags"])

    def test_welcome_pdf_has_exact_filename(self):
        r = audit_bytes(make_mail("Get https://finalvestige.com/wp-content/uploads/2026/10/"+PDF_NAME), "welcome")
        self.assertTrue(r["has_fieldbook_pdf_reference"])
        self.assertNotIn("WELCOME_FIELD_BOOK_NOT_OBSERVED", r["review_flags"])

    def test_commercial_without_disclosure_is_flagged(self):
        r = audit_bytes(make_mail("Seller says works.", "<a href='https://finalvestige.com/mind/'>Read guide</a>"), "commercial")
        self.assertIn("COMMISSION_DISCLOSURE_NOT_OBSERVED_IN_EMAIL", r["review_flags"])

    def test_commercial_with_html_disclosure_visible(self):
        r = audit_bytes(make_mail("Read full review", "<p>If you buy through a link on the guide we may earn a commission.</p><a href='https://finalvestige.com/mind/'>Guide</a>"), "commercial")
        self.assertTrue(r["has_inline_commission_disclosure"])

    def test_header_unsubscribe_not_equivalent_to_functioning(self):
        r = audit_bytes(make_mail(unsub="<https://example.test/u?token=secret>",oneclick=True), "editorial")
        self.assertTrue(r["has_list_unsubscribe_header"])
        self.assertTrue(r["has_one_click_header_signal"])
        self.assertTrue(r["needs_live_unsubscribe_function_test"])

    def test_visible_unsubscribe_must_be_https(self):
        r = audit_bytes(make_mail(html="<a href='http://example.test/u'>Unsubscribe</a>"), "editorial")
        self.assertFalse(r["has_visible_https_unsubscribe_anchor"])

    def test_visible_https_unsubscribe_is_signal_only(self):
        r = audit_bytes(make_mail(html="<a href='https://example.test/unsubscribe?k=PRIVATE'>Unsubscribe</a>"), "editorial")
        self.assertTrue(r["has_visible_https_unsubscribe_anchor"])
        self.assertTrue(r["needs_live_unsubscribe_function_test"])

    def test_confirmation_not_welcome(self):
        r = audit_bytes(make_mail("Confirm subscription"), "confirmation")
        self.assertFalse(r["has_fieldbook_pdf_reference"])
        self.assertFalse(r["confirmed_signup_observable_from_email"])

    def test_no_html_flags_first_party_link(self):
        r = audit_bytes(make_mail("read site"), "editorial")
        self.assertIn("FIRST_PARTY_HTML_LINK_NOT_OBSERVED", r["review_flags"])

    def test_no_plaintext_part_flags_text(self):
        m = EmailMessage()
        m["Subject"] = "Draft"
        m.set_content("<p>HTML only</p>", subtype="html")
        r = audit_bytes(m.as_bytes(), "editorial")
        self.assertIn("NO_PLAINTEXT_PART", r["review_flags"])

    def test_attachment_is_never_interpreted_as_body(self):
        m = EmailMessage()
        m["Subject"] = "Welcome"
        m.set_content("Hello")
        m.add_attachment("https://finalvestige.com/"+PDF_NAME,subtype="plain",filename="payload.txt")
        r = audit_bytes(m.as_bytes(),"welcome")
        self.assertFalse(r["has_fieldbook_pdf_reference"])

    def test_refuse_oversize_input(self):
        with self.assertRaises(ValueError):
            audit_bytes(b"X"*3_000_001,"welcome")

    def test_refuse_invalid_expect(self):
        with self.assertRaises(ValueError):
            audit_bytes(make_mail(),"marketing")

    def test_never_ready_for_send(self):
        for typ in ("welcome","editorial","commercial","confirmation"):
            r = audit_bytes(make_mail("May earn a commission.","<a href='https://finalvestige.com'>Read</a>",unsub="<https://example.test/u>"),typ)
            self.assertEqual("HOLD_UNSENT",r["decision"])
            self.assertTrue(r["needs_verified_fv_postal_address"])
            self.assertFalse(r["actual_merchant_sale_observable_from_email"])


if __name__ == "__main__":
    unittest.main()
