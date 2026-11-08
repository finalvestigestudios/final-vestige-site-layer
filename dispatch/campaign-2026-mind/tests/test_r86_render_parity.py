"""Synthetic-only R86 regression tests: never open a real inbox or email anybody."""
from email.message import EmailMessage
import importlib.util
import json
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / "r86-mime-parity" / "audit_render_parity.py"
SPEC = importlib.util.spec_from_file_location("r86_render_parity", SRC)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
CTA = "https://finalvestige.com/reviewer-only-fixture/"
POSTAL = "EXAMPLE PUBLISHER MAIL STOP 123, TEST CITY"
DISC = "Final Vestige may earn a commission."
UNSUB = "https://wordpress.com/subscriptions/example-fixture"


def default_plain():
    return DISC + "\nOpen this review: " + CTA + "\n" + POSTAL + "\nUnsubscribe: " + UNSUB


def default_html():
    return ('<html><body><p>' + DISC + '</p><p><a href="' + CTA +
            '">Open the guide</a></p><p>' + POSTAL + '</p><p><a href="' +
            UNSUB + '">Unsubscribe</a></p></body></html>')


def mail(plain=None, html=None, subject="Evidence before the offer"):
    msg = EmailMessage()
    msg["From"] = "synthetic@example.invalid"
    msg["To"] = "fixture@example.invalid"
    msg["Subject"] = subject
    msg["List-Unsubscribe"] = "<https://wordpress.com/subscriptions/fixture>"
    if plain is not False:
        msg.set_content(default_plain() if plain is None else plain)
    if html is not False:
        if plain is False:
            msg.set_content(default_html() if html is None else html, subtype="html")
        else:
            msg.add_alternative(default_html() if html is None else html, subtype="html")
    return msg.as_bytes()


def check(raw, *, commercial=True, postal=POSTAL, cta=CTA):
    return MOD.audit_bytes(raw, expected_subject="Evidence before the offer",
                           expected_cta=cta, commercial=commercial, postal_address=postal)


class RenderParityTests(unittest.TestCase):
    def test_synthetic_complete_parts_are_observed_not_certified(self):
        result = check(mail())
        self.assertEqual(result["decision"], "HOLD_UNSENT_REQUIRES_HUMAN_VERIFICATION")
        self.assertEqual(result["risk_flags"], [])
        self.assertTrue(all(v is True for v in result["checks"].values()))

    def test_html_disclosure_missing_even_if_plaintext_present(self):
        html = default_html().replace(DISC, "A reviewed offer is discussed.")
        d = check(mail(html=html))
        self.assertIn("COMMERCIAL_DISCLOSURE_RENDER_PARITY_FAILED", d["risk_flags"])
        self.assertTrue(d["checks"]["plain_commission_visible_early"])
        self.assertFalse(d["checks"]["html_commission_visible_early"])

    def test_plain_disclosure_missing_even_if_html_present(self):
        plain = default_plain().replace(DISC, "An optional guide.")
        d = check(mail(plain=plain))
        self.assertFalse(d["checks"]["plain_commission_visible_early"])
        self.assertIn("COMMERCIAL_DISCLOSURE_RENDER_PARITY_FAILED", d["risk_flags"])

    def test_html_disclosure_hidden_by_inline_css(self):
        html = default_html().replace(DISC, '<span style="display:none">' + DISC + "</span>")
        self.assertFalse(check(mail(html=html))["checks"]["html_commission_visible_early"])

    def test_html_disclosure_hidden_by_aria(self):
        html = default_html().replace(DISC, '<div aria-hidden="true">' + DISC + "</div>")
        self.assertFalse(check(mail(html=html))["checks"]["html_commission_visible_early"])

    def test_html_disclosure_hidden_attribute(self):
        html = default_html().replace(DISC, '<div hidden>' + DISC + "</div>")
        self.assertFalse(check(mail(html=html))["checks"]["html_commission_visible_early"])

    def test_html_disclosure_too_late(self):
        html = default_html().replace(DISC, "A" * 355 + DISC)
        self.assertFalse(check(mail(html=html))["checks"]["html_commission_visible_early"])

    def test_html_disclosure_not_next_to_cta(self):
        html = default_html().replace(DISC, DISC + " " + ("filler " * 60))
        self.assertFalse(check(mail(html=html))["checks"]["html_disclosure_precedes_and_near_cta"])

    def test_html_disclosure_after_cta_is_not_near(self):
        html = default_html().replace(DISC, "")
        html = html.replace("Open the guide</a>", "Open the guide</a>" + DISC)
        self.assertFalse(check(mail(html=html))["checks"]["html_disclosure_precedes_and_near_cta"])

    def test_html_cta_missing_plain_present(self):
        html = default_html().replace(CTA, "https://finalvestige.com/another-fixture/")
        d = check(mail(html=html))
        self.assertIn("CTA_NOT_VISIBLE_IN_BOTH_RENDITIONS", d["risk_flags"])
        self.assertTrue(d["checks"]["plain_expected_cta"])
        self.assertFalse(d["checks"]["html_expected_cta"])

    def test_plain_cta_missing_html_present(self):
        d = check(mail(plain=default_plain().replace(CTA, "https://elsewhere.example/test")))
        self.assertIn("CTA_NOT_VISIBLE_IN_BOTH_RENDITIONS", d["risk_flags"])
        self.assertFalse(d["checks"]["plain_expected_cta"])

    def test_hidden_html_cta_does_not_count(self):
        html = default_html().replace('<a href="' + CTA + '">', '<a hidden href="' + CTA + '">')
        self.assertFalse(check(mail(html=html))["checks"]["html_expected_cta"])

    def test_empty_anchor_label_does_not_count_as_cta(self):
        html = default_html().replace("Open the guide</a>", "</a>")
        self.assertFalse(check(mail(html=html))["checks"]["html_expected_cta"])

    def test_postal_plain_only_not_compliant(self):
        d = check(mail(html=default_html().replace(POSTAL, "")))
        self.assertIn("PUBLISHER_POSTAL_UNVERIFIED_IN_RENDITIONS", d["risk_flags"])

    def test_postal_html_only_not_compliant(self):
        d = check(mail(plain=default_plain().replace(POSTAL, "")))
        self.assertFalse(d["checks"]["plain_publisher_postal_string"])

    def test_postal_unverified_even_if_fake_string_is_present(self):
        d = check(mail(), postal=None)
        self.assertIn("PUBLISHER_POSTAL_UNVERIFIED_IN_RENDITIONS", d["risk_flags"])

    def test_unsubscribe_plain_only_not_compliant(self):
        html = default_html().replace("Unsubscribe</a>", "Account details</a>")
        d = check(mail(html=html))
        self.assertIn("UNSUBSCRIBE_INDICATOR_RENDER_PARITY_FAILED", d["risk_flags"])

    def test_unsubscribe_html_only_not_compliant(self):
        plain = default_plain().replace("Unsubscribe:", "Manage:")
        d = check(mail(plain=plain))
        self.assertIn("UNSUBSCRIBE_INDICATOR_RENDER_PARITY_FAILED", d["risk_flags"])

    def test_list_unsubscribe_header_not_optout_functionality(self):
        html = default_html().replace("Unsubscribe</a>", "Preferences</a>")
        plain = default_plain().replace("Unsubscribe:", "Manage:")
        d = check(mail(plain=plain, html=html))
        self.assertTrue(d["checks"]["list_unsubscribe_header_indicator"])
        self.assertIn("UNSUBSCRIBE_INDICATOR_RENDER_PARITY_FAILED", d["risk_flags"])

    def test_subject_mismatch_is_flagged(self):
        d = check(mail(subject="Not what reader expected"))
        self.assertIn("SUBJECT_MISMATCH", d["risk_flags"])

    def test_html_only_reports_missing_mime(self):
        d = check(mail(plain=False))
        self.assertIn("MIME_PART_MISSING_OR_UNOBSERVED", d["risk_flags"])

    def test_plain_only_reports_missing_mime(self):
        d = check(mail(html=False))
        self.assertIn("MIME_PART_MISSING_OR_UNOBSERVED", d["risk_flags"])

    def test_editorial_has_no_commercial_requirements(self):
        d = check(mail(), commercial=False)
        self.assertIsNone(d["checks"]["html_commission_visible_early"])
        self.assertNotIn("COMMERCIAL_DISCLOSURE_RENDER_PARITY_FAILED", d["risk_flags"])

    def test_strict_first_party_cta(self):
        for cta in ("http://finalvestige.com/guide", "https://other.example/guide",
                    "https://finalvestige.com/guide?affiliate=1",
                    "https://user:pass@finalvestige.com/guide",
                    "https://finalvestige.com:443/guide"):
            with self.subTest(cta=cta):
                with self.assertRaises(ValueError):
                    check(mail(), cta=cta)

    def test_plain_punctuation_stripped(self):
        raw = mail(plain=default_plain().replace(CTA, CTA + "."))
        self.assertTrue(check(raw)["checks"]["plain_expected_cta"])

    def test_rejects_invalid_input_and_missing_header(self):
        for raw in (b"", b"hello", b"a" * (MOD.MAX_BYTES + 1)):
            with self.subTest(length=len(raw)), self.assertRaises(ValueError):
                check(raw)

    def test_does_not_echo_private_identity_or_links(self):
        d = json.dumps(check(mail()))
        for secret in ("synthetic@example.invalid", "fixture@example.invalid",
                       "reviewer-only-fixture", "TEST CITY", "subscriptions/example-fixture"):
            self.assertNotIn(secret, d)

    def test_all_synthetic_passes_remain_hard_hold(self):
        d = check(mail())
        self.assertEqual(d["risk_flags"], [])
        self.assertEqual(d["decision"], "HOLD_UNSENT_REQUIRES_HUMAN_VERIFICATION")


if __name__ == "__main__":
    unittest.main()
