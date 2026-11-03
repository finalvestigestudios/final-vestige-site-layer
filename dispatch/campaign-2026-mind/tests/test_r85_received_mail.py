"""R85: locally generated, NON-SENT synthetic MIME; no private inbox data."""
from email.message import EmailMessage
import importlib.util
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "r85-received-mail-proof" / "audit_received_eml.py"
SPEC = importlib.util.spec_from_file_location("fv_dispatch_received_eml", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CTA = "https://finalvestige.com/2026/11/02/change-blindness/"
SUBJECT = "The person changed. The conversation went on."
ADDRESS = "Publisher Designated Mailbox, 123 Test Lane, Fiction, ZZ 00000"
DISCLOSURE = ("If you buy through a link on the linked guide, "
              "Final Vestige may earn a commission.")


def make_mail(*, plain=None, html=None, subject=SUBJECT, from_header="Final Vestige <newsletter@example.org>",
              unsub_header=True, one_click=True, address=ADDRESS):
    msg = EmailMessage()
    msg["From"] = from_header
    msg["To"] = "test.recipient@example.org"
    msg["Subject"] = subject
    if unsub_header:
        msg["List-Unsubscribe"] = "<https://example.org/opaque-sensitive-identifier>"
    if one_click:
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    plain = plain if plain is not None else (
        "A record, an observation, and a test you can try. " + DISCLOSURE
        + " " + CTA + " " + address + " Unsubscribe here."
    )
    msg.set_content(plain)
    if html is not None:
        msg.add_alternative(html, subtype="html")
    return msg.as_bytes()


def scan(raw, *, commercial=True, expected=SUBJECT, cta=CTA, address=ADDRESS):
    return MODULE.audit_bytes(raw, expected_subject=expected, expected_cta=cta,
                              commercial=commercial, postal_address=address)


class ReceivedMailAudit(unittest.TestCase):
    def test_authorized_synthetic_message_remains_hold(self):
        html = ('<html><body><p>' + DISCLOSURE + '</p><a href="' + CTA
                + '">Read the actual evidence</a><p>' + ADDRESS
                + '</p><a href="https://wordpress.com/unsubscribe/x">Unsubscribe</a></body></html>')
        result = scan(make_mail(html=html))
        self.assertEqual(result["decision"], "HOLD_UNSENT_REQUIRES_HUMAN_VERIFICATION")
        self.assertTrue(all(x is True for x in result["checks"].values()))

    def test_no_personal_data_is_emitted(self):
        html = ('<p>' + DISCLOSURE + '</p><a href="' + CTA
                + '">Read</a><a href="https://wordpress.com/unsubscribe/TOKEN_SECRET">Unsubscribe</a>'
                + '<p>' + ADDRESS + '</p>')
        report = json.dumps(scan(make_mail(html=html)))
        for prohibited in ("test.recipient", "newsletter@example", "TOKEN_SECRET",
                           "123 Test Lane", "https://finalvestige.com", SUBJECT, "example.org"):
            self.assertNotIn(prohibited, report)

    def test_subject_requires_exact_match(self):
        self.assertTrue(scan(make_mail())["checks"]["subject_matches_expected"])
        for candidate in ("The person changed", "Another subject", SUBJECT + "!!"):
            self.assertFalse(scan(make_mail(subject=candidate))["checks"]["subject_matches_expected"])

    def test_commercial_requires_disclosure_observation(self):
        raw = make_mail(plain=CTA + " " + ADDRESS + " Unsubscribe.")
        self.assertFalse(scan(raw)["checks"]["commission_disclosure_present"])
        self.assertIsNone(scan(raw, commercial=False)["checks"]["commission_disclosure_present"])

    def test_disclosure_beyond_350_not_falsely_early(self):
        raw = make_mail(plain=("word " * 100) + DISCLOSURE + " " + CTA + " " + ADDRESS)
        self.assertTrue(scan(raw)["checks"]["commission_disclosure_present"])
        self.assertFalse(scan(raw)["checks"]["commission_disclosure_in_first_350_visible_chars"])

    def test_html_disclosure_first_350_visible_chars(self):
        html = '<p>' + DISCLOSURE + '</p><a href="' + CTA + '">Read</a>'
        self.assertTrue(scan(make_mail(plain="short", html=html))["checks"][
            "commission_disclosure_in_first_350_visible_chars"])

    def test_html_script_and_style_are_not_counted(self):
        html = ('<style>.x{content:"Final Vestige may earn a commission"}</style>'
                '<script>Final Vestige may earn a commission</script><p>Nothing advertised here.</p>'
                '<a href="' + CTA + '">Read</a>')
        raw = make_mail(plain="No disclosure. " + CTA, html=html)
        self.assertFalse(scan(raw)["checks"]["commission_disclosure_present"])

    def test_html_unsubscribe_labeled_link_detected(self):
        html = '<a href="https://wordpress.com/unsubscribe/x">Unsubscribe from newsletter</a>'
        self.assertTrue(scan(make_mail(html=html, plain="no unsubscribe here"))["checks"][
            "body_unsubscribe_instruction_or_link_seen"])

    def test_unsubscribe_header_is_presence_not_function(self):
        r = scan(make_mail(unsub_header=True, one_click=True))
        self.assertTrue(r["checks"]["list_unsubscribe_header_seen"])
        self.assertTrue(r["checks"]["list_unsubscribe_one_click_header_seen"])
        self.assertIn("Header presence does not prove unsubscribe works", r["limitations"])
        r2 = scan(make_mail(unsub_header=False, one_click=False, plain=CTA))
        self.assertFalse(r2["checks"]["list_unsubscribe_header_seen"])
        self.assertFalse(r2["checks"]["body_unsubscribe_instruction_or_link_seen"])

    def test_missing_postal_address(self):
        self.assertFalse(scan(make_mail(address="Unrelated Address"))["checks"][
            "postal_address_string_present"])
        self.assertFalse(scan(make_mail(), address=None)["checks"]["postal_address_string_present"])

    def test_postal_address_supplied_is_not_ownership_proof(self):
        r = scan(make_mail())
        self.assertTrue(r["checks"]["postal_address_string_present"])
        self.assertTrue(any("ownership" in s for s in r["limitations"]))

    def test_first_party_url_required(self):
        for bad in ("http://finalvestige.com/x", "https://example.org/x",
                    "javascript:alert(1)", "https://finalvestige.com:444/x",
                    "https://foo@finalvestige.com/x",
                    "https://finalvestige.com/x?email=secret",
                    "https://finalvestige.com/x#fragment",
                    "", "https://"):
            with self.subTest(url=bad), self.assertRaises(ValueError):
                scan(make_mail(), cta=bad)

    def test_exact_cta_in_plaintext(self):
        self.assertTrue(scan(make_mail())["checks"]["expected_first_party_cta_present"])
        self.assertFalse(scan(make_mail(plain="No matching URL"))["checks"][
            "expected_first_party_cta_present"])

    def test_exact_cta_in_html(self):
        html = '<a href="' + CTA + '">Explore</a>'
        r = scan(make_mail(plain="Read the study.", html=html))
        self.assertTrue(r["checks"]["expected_first_party_cta_present"])

    def test_fake_lookalike_cta_not_accepted(self):
        wrong = "https://finalvestige.com.evil.example/2026/11/02/change-blindness/"
        self.assertFalse(scan(make_mail(plain=wrong))["checks"][
            "expected_first_party_cta_present"])

    def test_non_anchored_href_stays_unrecognized(self):
        html = '<p data-href="' + CTA + '">This is not a link.</p>'
        self.assertFalse(scan(make_mail(plain="Nothing.", html=html))["checks"][
            "expected_first_party_cta_present"])

    def test_zero_size_or_oversize_rejected(self):
        for raw in (b"", b"nonsense", b"x" * (MODULE.MAX_BYTES + 1)):
            with self.subTest(size=len(raw)), self.assertRaises(ValueError):
                scan(raw)

    def test_invalid_expected_subject_and_address_rejected(self):
        for subject in ("", "   "):
            with self.assertRaises(ValueError):
                scan(make_mail(), expected=subject)
        for postal in ("", "X"):
            with self.assertRaises(ValueError):
                scan(make_mail(), address=postal)

    def test_missing_mime_headers_rejected(self):
        raw = b"Subject: Testing\n\nHello."
        with self.assertRaises(ValueError):
            scan(raw)

    def test_no_body_rejected(self):
        raw = b"From: sender@example.org\nSubject: Hello\nContent-Type: application/octet-stream\n\nzz"
        with self.assertRaises(ValueError):
            scan(raw)

    def test_no_sender_addresses_or_click_tokens_in_report(self):
        raw = make_mail(from_header="Private Name <private+identifier@example.com>")
        s = json.dumps(scan(raw))
        for needle in ("Private Name", "private+identifier@example.com", "test.recipient@example.org", "example.com"):
            self.assertNotIn(needle, s)

    def test_read_only_contract_does_not_offer_ready_state(self):
        for mode in (True, False):
            r = scan(make_mail(), commercial=mode)
            self.assertNotIn("READY", r["decision"])
            self.assertNotIn("send", r["checks"])
            self.assertIn("Final founder approval of each send, audience and timing",
                          r["requires_external_evidence"])

    def test_commercial_has_additional_partner_gates(self):
        r = scan(make_mail(), commercial=True)
        self.assertTrue(any("affiliate approval" in s for s in r["requires_external_evidence"]))
        e = scan(make_mail(), commercial=False)
        self.assertFalse(any("affiliate approval" in s for s in e["requires_external_evidence"]))


if __name__ == "__main__":
    unittest.main()
