"""R74: adversarial hidden-content guards. All messages are synthetic.

A normal HTMLParser exposes source text, not the rendered inbox. Hidden
legal notices, hidden disclosures and hidden opt-out labels must not be
counted as visible evidence. Real rendering still needs founder authorization.
"""
from email.message import EmailMessage
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "r70-received-mime"

def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

inspector = load("fv_r74_mime", "inspect_received_eml.py")
renderer = load("fv_r74_mime_report", "render_report.py")
POSTAL = "123 Fictional Lane, Example City, CA 90000"
UNSUB = "https://unsubscribe.example.invalid/t/SYNTHETIC"
DISCLOSURE = "Final Vestige may receive a commission for an optional purchase."
SUBJECT = "Synthetic publisher review, never send"

def audit(html, plain=None, edition="03"):
    msg = EmailMessage()
    msg["Subject"] = SUBJECT
    msg["From"] = "Fictional Publisher <noreply@wordpress.com>"
    msg["To"] = "private@example.invalid"
    if plain is None:
        msg.set_content(html, subtype="html")
    else:
        msg.set_content(plain)
        msg.add_alternative(html, subtype="html")
    return inspector.audit_bytes(msg.as_bytes(), edition=edition,
            expected_subject=SUBJECT, publisher_postal_address=POSTAL)

def plain():
    return DISCLOSURE + "\n" + POSTAL + "\nUnsubscribe: " + UNSUB

def h(opening=DISCLOSURE, postal=POSTAL, link=True):
    return ("<html lang='en'><body><p>" + opening + "</p><p>" +
            postal + "</p>" +
            ("<a href='" + UNSUB + "'>Unsubscribe</a>" if link else "") +
            "</body></html>")

class HiddenEvidenceCannotPass(unittest.TestCase):
    def test_original_html_metadata_never_counts_as_visible_disclosure(self):
        x = audit("<html lang='en'><head><title>" + DISCLOSURE +
                  "</title></head><body><p>Some seller language.</p></body></html>",
                  plain())
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])
        self.assertIn("COMMERCIAL_DISCLOSURE_MIME_ALTERNATIVES_MISMATCH", x["blockers"])

    def test_hidden_attribute_suppresses_disclosure(self):
        x = audit(h("<span hidden>" + DISCLOSURE + "</span>Seller information"), plain())
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])
        self.assertTrue(x["signals"]["html_hidden_node_encountered"])

    def test_inline_display_none_suppresses_disclosure(self):
        x = audit(h("<span style='display: none'>" + DISCLOSURE +
                    "</span>Seller information"), plain())
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])

    def test_inline_visibility_hidden_suppresses_disclosure(self):
        x = audit(h("<span style='visibility: hidden'>" + DISCLOSURE +
                    "</span>Seller information"), plain())
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])

    def test_inline_opacity_zero_suppresses_disclosure(self):
        x = audit(h("<span style='opacity:0'>" + DISCLOSURE +
                    "</span>Seller information"), plain())
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])

    def test_inline_font_size_zero_suppresses_disclosure(self):
        x = audit(h("<span style='font-size:0px'>" + DISCLOSURE +
                    "</span>Seller information"), plain())
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])

    def test_aria_hidden_suppresses_a11y_disclosure(self):
        x = audit(h("<span aria-hidden='true'>" + DISCLOSURE +
                    "</span>Seller information"), plain())
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])

    def test_template_content_is_not_visible_disclosure(self):
        x = audit(h("<template>" + DISCLOSURE + "</template>Seller information"), plain())
        self.assertFalse(x["signals"]["commercial_early_disclosure_html"])

    def test_hidden_html_publisher_address_not_a_match(self):
        x = audit(h(DISCLOSURE, "<span style='display:none'>" + POSTAL + "</span>"), plain())
        self.assertFalse(x["signals"]["html_part_postal_matches_private_reference"])
        self.assertFalse(x["signals"]["postal_text_matches_private_publisher_reference"])
        self.assertIn("PUBLISHER_ADDRESS_MISSING_IN_A_MIME_ALTERNATIVE", x["blockers"])

    def test_aria_hidden_html_publisher_address_not_a_match(self):
        x = audit(h(DISCLOSURE, "<span aria-hidden='true'>" + POSTAL + "</span>"), plain())
        self.assertFalse(x["signals"]["html_part_postal_matches_private_reference"])

    def test_hidden_html_unsubscribe_anchor_not_detected(self):
        x = audit("<html><body><a hidden href='" + UNSUB +
                  "'>Unsubscribe</a></body></html>", edition="01")
        self.assertFalse(x["signals"]["unsubscribe_labeled_https_link_present"])
        self.assertIn("NO_VISIBLE_OPT_OUT_DESTINATION_DETECTED", x["blockers"])

    def test_style_hidden_html_unsubscribe_anchor_not_detected(self):
        x = audit("<html><body><a style='display:none' href='" + UNSUB +
                  "'>Unsubscribe</a></body></html>", edition="01")
        self.assertFalse(x["signals"]["unsubscribe_labeled_https_link_present"])

    def test_invisible_label_inside_visible_anchor_not_detected(self):
        x = audit("<html><body><a href='" + UNSUB + "'><span hidden>" +
                  "Unsubscribe</span><span>Read Fieldbook</span></a></body></html>",
                  edition="01")
        self.assertFalse(x["signals"]["unsubscribe_labeled_https_link_present"])

    def test_visible_optout_after_hidden_link_is_still_detected(self):
        x = audit("<html><body><a hidden href='" + UNSUB +
                  "'>Unsubscribe</a><a href='" + UNSUB +
                  "'>Unsubscribe</a></body></html>",edition="01")
        self.assertTrue(x["signals"]["unsubscribe_labeled_https_link_present"])

    def test_visible_disclosure_after_hidden_head_still_detected(self):
        x = audit("<html><head><title>Not content</title></head><body><p>" +
                  DISCLOSURE + "</p></body></html>", plain())
        self.assertTrue(x["signals"]["commercial_early_disclosure_html"])

    def test_void_element_does_not_hide_following_text(self):
        x = audit("<html lang='en'><body><img src='cid:synthetic'>" +
                  "<p>" + DISCLOSURE + "</p></body></html>", plain())
        self.assertTrue(x["signals"]["commercial_early_disclosure_html"])

    def test_stylesheet_marks_uncertainty_and_remains_hold(self):
        x = audit("<html><head><style>.notice{display:none}</style></head>"
                  "<body><p class='notice'>" + DISCLOSURE +
                  "</p></body></html>", plain())
        self.assertTrue(x["signals"]["html_css_visibility_ambiguous"])
        self.assertFalse(x["send_allowed"])
        self.assertIn("WORDPRESS_EXCERPT_AND_PREHEADER_REQUIRE_NATIVE_INBOX_REVIEW", x["blockers"])

    def test_hidden_only_body_is_not_visible_content(self):
        x = audit("<html><body><p hidden>Hidden record</p></body></html>",edition="01")
        self.assertFalse(x["signals"]["visible_body_present"])
        self.assertIn("SUBJECT_OR_VISIBLE_BODY_MISSING", x["blockers"])

    def test_renderer_discloses_visibility_limiter_without_private_values(self):
        x = audit(h("<span hidden>" + DISCLOSURE + "</span>Seller information"), plain())
        view = renderer.html_report(x) + renderer.text_report(x)
        self.assertIn("Hidden/non-body HTML detected", view)
        self.assertIn("HOLD_UNSENT", view)
        self.assertNotIn(POSTAL, view)
        self.assertNotIn(UNSUB, view)

    def test_invariant_never_sends_and_never_claims_inbox_provenance(self):
        x = audit(h(), plain())
        self.assertEqual(x["release_status"], "HOLD_UNSENT")
        self.assertFalse(x["send_allowed"])
        self.assertEqual(x["evidence_level"], "UNAUTHENTICATED_LOCAL_MIME_INSPECTION_ONLY")
        self.assertFalse(x["message_sent_by_this_tool"])
        self.assertFalse(x["unsubscribe_executed_by_this_tool"])

if __name__ == "__main__":
    unittest.main()
