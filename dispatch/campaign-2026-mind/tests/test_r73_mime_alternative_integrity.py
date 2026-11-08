"""R73: synthetic MIME adversarial tests for REAL release-blocker defects.

No actual emails, customer addresses, opt-out actions, WordPress writes, or
external requests. All message addresses and URLs use reserved .invalid.
"""
from email.message import EmailMessage
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "r70-received-mime"
def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

inspector = load("fv_r73_inspector", "inspect_received_eml.py")
renderer = load("fv_r73_renderer", "render_report.py")

POSTAL = "P.O. Box 123, Example City, CA 90000"  # Invented test string.
UNSUB = "https://unsubscribe.example.invalid/u/SYNTHETIC_TOKEN"
DISCLOSURE = "Final Vestige may receive a commission from an optional qualifying purchase."
HEADLINE = "A forensic exercise — synthetic only"

def eml(plain, html=None, *, header=None, post_one_click=False, subject=HEADLINE):
    m = EmailMessage()
    m["Subject"] = subject
    m["From"] = "Example Publisher <noreply@wordpress.com>"
    m["To"] = "private.reviewer@example.invalid"
    if header is not None:
        m["List-Unsubscribe"] = header
    if post_one_click:
        m["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    if plain is None:
        m.set_content(html, subtype="html")
    else:
        m.set_content(plain)
        if html is not None:
            m.add_alternative(html, subtype="html")
    return m.as_bytes()

def inspect(plain, html=None, *, edition="03", postal=POSTAL, header=None, post_one_click=False):
    return inspector.audit_bytes(
        eml(plain, html, header=header, post_one_click=post_one_click),
        edition=edition, expected_subject=HEADLINE, publisher_postal_address=postal
    )

def html_body(text="", *, postal=True, unsub=True):
    return '<html lang="en"><body><p>' + text + '</p>' + (
        '<p>' + POSTAL + '</p>' if postal else ''
    ) + ('<a href="' + UNSUB + '">Unsubscribe</a>' if unsub else '') + '</body></html>'

def plain_body(text="", *, postal=True, unsub=True):
    return text + '\n' + (POSTAL if postal else '') + (
        '\nUnsubscribe: ' + UNSUB if unsub else ''
    )

class MimeAlternativeIntegrity(unittest.TestCase):
    def test_detected_values_never_override_release_hold(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE))
        self.assertEqual(x["release_status"], "HOLD_UNSENT")
        self.assertFalse(x["send_allowed"])
        self.assertTrue(x["synthetic_or_real_not_determined"])
        self.assertEqual(x["schema"], "fv-dispatch-received-eml-readonly-v2")

    def test_unsubscribe_word_plus_unrelated_https_url_is_NOT_an_optout(self):
        x = inspect("Unsubscribe anytime. Read the investigation at https://finalvestige.com/focus/", edition="01")
        self.assertFalse(x["signals"]["plain_text_optout_and_https_present"])
        self.assertIn("NO_VISIBLE_OPT_OUT_DESTINATION_DETECTED", x["blockers"])

    def test_unsubscribe_label_plus_real_syntax_candidate(self):
        x = inspect("Unsubscribe: " + UNSUB, edition="01")
        self.assertTrue(x["signals"]["plain_text_optout_and_https_present"])
        self.assertFalse(x["send_allowed"])

    def test_optout_label_on_line_above_url(self):
        x = inspect("Unsubscribe:\n" + UNSUB, edition="01")
        self.assertTrue(x["signals"]["plain_text_optout_and_https_present"])

    def test_optout_http_does_not_count_as_https(self):
        x = inspect("Unsubscribe: http://unsubscribe.example.invalid/u/token", edition="01")
        self.assertFalse(x["signals"]["plain_text_optout_and_https_present"])

    def test_optout_mailto_is_not_https_candidate(self):
        x = inspect("Unsubscribe: mailto:remove@example.invalid", edition="01")
        self.assertFalse(x["signals"]["plain_text_optout_and_https_present"])

    def test_unrelated_link_on_next_line_not_counted(self):
        x = inspect("Unsubscribe from this campaign.\nVisit https://finalvestige.com/focus/", edition="01")
        self.assertFalse(x["signals"]["plain_text_optout_and_https_present"])

    def test_plain_optout_does_not_conceal_missing_html_optout(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE, unsub=False))
        self.assertTrue(x["signals"]["plain_text_optout_and_https_present"])
        self.assertFalse(x["signals"]["unsubscribe_labeled_https_link_present"])
        self.assertIn("OPT_OUT_REFERENCE_MISSING_IN_A_MIME_ALTERNATIVE", x["blockers"])

    def test_html_optout_does_not_conceal_missing_plain_optout(self):
        x = inspect(plain_body(DISCLOSURE, unsub=False), html_body(DISCLOSURE))
        self.assertFalse(x["signals"]["plain_text_optout_and_https_present"])
        self.assertTrue(x["signals"]["unsubscribe_labeled_https_link_present"])
        self.assertIn("OPT_OUT_REFERENCE_MISSING_IN_A_MIME_ALTERNATIVE", x["blockers"])

    def test_both_optout_candidates_do_not_remove_functional_hold(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE))
        self.assertNotIn("OPT_OUT_REFERENCE_MISSING_IN_A_MIME_ALTERNATIVE", x["blockers"])
        self.assertIn("OPT_OUT_REACHABILITY_AND_SUCCESS_REQUIRE_AUTHORIZED_HUMAN_TEST", x["blockers"])

    def test_html_only_unsubscribe_candidate_reports_no_fake_plain_part(self):
        x = inspect(None, html_body(DISCLOSURE), edition="01")
        self.assertTrue(x["signals"]["unsubscribe_labeled_https_link_present"])
        self.assertFalse(x["signals"]["plain_text_part_present"])
        self.assertNotIn("OPT_OUT_REFERENCE_MISSING_IN_A_MIME_ALTERNATIVE", x["blockers"])

    def test_missing_html_postal_cannot_be_hidden_by_plain_postal(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE, postal=False))
        self.assertTrue(x["signals"]["plain_part_postal_matches_private_reference"])
        self.assertFalse(x["signals"]["html_part_postal_matches_private_reference"])
        self.assertFalse(x["signals"]["postal_text_matches_private_publisher_reference"])
        self.assertIn("PUBLISHER_ADDRESS_MISSING_IN_A_MIME_ALTERNATIVE", x["blockers"])

    def test_missing_plain_postal_cannot_be_hidden_by_html_postal(self):
        x = inspect(plain_body(DISCLOSURE, postal=False), html_body(DISCLOSURE))
        self.assertFalse(x["signals"]["plain_part_postal_matches_private_reference"])
        self.assertTrue(x["signals"]["html_part_postal_matches_private_reference"])
        self.assertFalse(x["signals"]["postal_text_matches_private_publisher_reference"])
        self.assertIn("PUBLISHER_ADDRESS_MISSING_IN_A_MIME_ALTERNATIVE", x["blockers"])

    def test_postal_both_variants_is_syntax_only_not_ownership(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE))
        self.assertTrue(x["signals"]["postal_text_matches_private_publisher_reference"])
        self.assertNotIn("PUBLISHER_ADDRESS_MISSING_IN_A_MIME_ALTERNATIVE", x["blockers"])
        self.assertIn("POSTAL_ADDRESS_OWNERSHIP_AND_LEGAL_VALIDITY_REQUIRE_HUMAN_PROOF", x["blockers"])

    def test_no_private_postal_reference_remains_unknown(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE), postal=None)
        self.assertIsNone(x["signals"]["postal_text_matches_private_publisher_reference"])
        self.assertIsNone(x["signals"]["plain_part_postal_matches_private_reference"])
        self.assertIsNone(x["signals"]["html_part_postal_matches_private_reference"])

    def test_plain_disclosure_cannot_mask_missing_html_disclosure(self):
        x = inspect(plain_body(DISCLOSURE), html_body("Seller advertises a product."))
        self.assertTrue(x["signals"]["commercial_early_disclosure_plain"])
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])
        self.assertFalse(x["signals"]["commercial_disclosure_within_first_55_visible_words"])
        self.assertIn("COMMERCIAL_DISCLOSURE_MIME_ALTERNATIVES_MISMATCH", x["blockers"])

    def test_html_disclosure_cannot_mask_missing_plain_disclosure(self):
        x = inspect(plain_body("Seller advertises a product."), html_body(DISCLOSURE))
        self.assertFalse(x["signals"]["commercial_early_disclosure_plain"])
        self.assertTrue(x["signals"]["commercial_early_disclosure_html"])
        self.assertFalse(x["signals"]["commercial_disclosure_within_first_55_visible_words"])
        self.assertIn("COMMERCIAL_DISCLOSURE_MIME_ALTERNATIVES_MISMATCH", x["blockers"])

    def test_commission_may_receive_writing_is_recognized(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE))
        self.assertTrue(x["signals"]["commercial_disclosure_within_first_55_visible_words"])

    def test_commission_may_earn_writing_is_also_recognized(self):
        d = "Final Vestige may earn a commission from qualifying purchases."
        x = inspect(plain_body(d), html_body(d))
        self.assertTrue(x["signals"]["commercial_disclosure_within_first_55_visible_words"])

    def test_disclosure_after_55_words_in_html_is_blocked(self):
        x = inspect(plain_body(DISCLOSURE), html_body(("historical evidence " * 36) + DISCLOSURE))
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])
        self.assertFalse(x["signals"]["commercial_disclosure_within_first_55_visible_words"])
        self.assertIn("DISCLOSURE_NOT_DETECTED_IN_FIRST_55_WORDS", x["blockers"])

    def test_disclosure_both_early_does_not_mean_merchant_permission(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE), edition="05")
        self.assertTrue(x["signals"]["commercial_disclosure_within_first_55_visible_words"])
        self.assertIn("MERCHANT_EMAIL_CHANNEL_ACCEPTANCE_NOT_VERIFIED", x["blockers"])

    def test_plain_only_commercial_can_have_detected_disclosure(self):
        x = inspect(plain_body(DISCLOSURE), html=None)
        self.assertTrue(x["signals"]["commercial_early_disclosure_plain"])
        self.assertIsNone(x["signals"]["commercial_early_disclosure_html"])

    def test_html_only_commercial_can_have_detected_disclosure(self):
        x = inspect(None, html_body(DISCLOSURE))
        self.assertIsNone(x["signals"]["commercial_early_disclosure_plain"])
        self.assertTrue(x["signals"]["commercial_early_disclosure_html"])

    def test_declared_one_click_without_list_unsubscribe_https_is_not_counted(self):
        x = inspect(plain_body(DISCLOSURE), header=None, post_one_click=True)
        self.assertFalse(x["signals"]["list_unsubscribe_post_one_click_declared"])

    def test_one_click_mailto_only_is_not_counted(self):
        x = inspect(plain_body(DISCLOSURE), header="<mailto:remove@example.invalid>", post_one_click=True)
        self.assertFalse(x["signals"]["list_unsubscribe_post_one_click_declared"])

    def test_one_click_http_only_is_not_counted(self):
        x = inspect(plain_body(DISCLOSURE), header="<http://unsubscribe.example.invalid/u/token>", post_one_click=True)
        self.assertFalse(x["signals"]["list_unsubscribe_post_one_click_declared"])

    def test_one_click_header_with_https_is_syntax_only(self):
        x = inspect(plain_body(DISCLOSURE), header="<" + UNSUB + ">", post_one_click=True)
        self.assertTrue(x["signals"]["list_unsubscribe_post_one_click_declared"])
        self.assertIn("OPT_OUT_REACHABILITY_AND_SUCCESS_REQUIRE_AUTHORIZED_HUMAN_TEST", x["blockers"])

    def test_hidden_script_does_not_count_as_html_disclosure(self):
        h = '<html lang="en"><body><script>' + DISCLOSURE + '</script><p>Visible product story.</p></body></html>'
        x = inspect(plain_body(DISCLOSURE), h)
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])
        self.assertIn("UNSAFE_OR_UNEXPECTED_HTML_ELEMENTS", x["blockers"])

    def test_all_reports_are_privacy_redacted_and_non_sending(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE), header="<"+UNSUB+">", post_one_click=True)
        flat = json.dumps(x)
        for secret in (POSTAL, "private.reviewer", "SYNTHETIC_TOKEN", HEADLINE, "unsubscribe.example.invalid"):
            self.assertNotIn(secret, flat)
        self.assertFalse(x["send_allowed"])
        self.assertFalse(x["message_sent_by_this_tool"])
        self.assertFalse(x["unsubscribe_executed_by_this_tool"])

    def test_renderer_surfaces_per_variant_without_private_values(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE, postal=False, unsub=False))
        html = renderer.html_report(x)
        text = renderer.text_report(x)
        self.assertIn("Postal reference appears in EVERY present MIME rendition", html)
        self.assertIn("Commercial disclosure appears early in HTML", text)
        self.assertIn("HOLD_UNSENT", html)
        for bad in ("private.reviewer", "SYNTHETIC_TOKEN", POSTAL):
            self.assertNotIn(bad, html + text)

    def test_reviewer_rejects_boolean_payload_spoofing(self):
        x = inspect(plain_body(DISCLOSURE), html_body(DISCLOSURE))
        x["signals"]["commercial_early_disclosure_html"] = "true and safe"
        with self.assertRaises(ValueError):
            renderer.clean(x)

    def test_scope_is_offline_and_original_campaign_still_present(self):
        code = (ROOT / "inspect_received_eml.py").read_text(encoding="utf-8")
        for dangerous in ("smtplib", "requests.post", "urllib.request", "send_message(", "sendmail("):
            self.assertNotIn(dangerous, code)
        self.assertTrue((ROOT.parent / "issues" / "03-the-twelve-minute-question.md").exists())
        self.assertTrue((ROOT.parent / "issues" / "05-before-you-press-play.md").exists())

if __name__ == "__main__":
    unittest.main()
