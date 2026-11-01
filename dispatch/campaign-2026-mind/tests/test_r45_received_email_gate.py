"""R45: synthetic RFC 5322 EML tests only. No actual mail is sent or stored."""
from email.message import EmailMessage
import importlib.util
import json
from pathlib import Path
import sys
import unittest

CODE = Path(__file__).resolve().parents[1] / "r45-received-proof" / "received_email_gate.py"
SPEC = importlib.util.spec_from_file_location("dispatch_r45_gate", CODE)
GATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GATE
SPEC.loader.exec_module(GATE)

FAKE_POSTAL = "PO Box 12345 Exampleville CA 99999"
BODY = ("History teaches us to separate evidence from promises. "
        "If you buy through a link on the linked guide, Final Vestige may earn "
        "a commission. " + FAKE_POSTAL + ". Unsubscribe anytime.")

def eml(plain=BODY, html=None, sender="Final Vestige <donotreply@wordpress.com>",
        subject="TEST ONLY historical record", unsub=True):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = "SENSITIVE_FAKE_RECIPIENT@example.invalid"
    msg["Subject"] = subject
    if unsub:
        msg["List-Unsubscribe"] = "<https://wordpress.com/unsubscribe/?token=SENSITIVE_FAKE_TOKEN>"
    msg.set_content(plain)
    if html is not None:
        msg.add_alternative(html, subtype="html")
    return msg.as_bytes()

def run(edition=3, content=None, guide="https://finalvestige.com/mind/zen12-guide/"):
    return GATE.inspect_eml(
        content if content is not None else eml(),
        edition,
        expected_subject="TEST ONLY historical record",
        expected_guide=guide,
        expected_postal_address=FAKE_POSTAL
    )

class TestReceivedEvidenceSafety(unittest.TestCase):
    def test_all_six_always_hold(self):
        for edition in range(1, 7):
            self.assertIn("HOLD_UNSENT", run(edition)["release"])

    def test_commercial_extra_hold(self):
        for edition in (3, 5):
            self.assertEqual(run(edition)["release"], "HOLD_UNSENT_AND_MERCHANT")

    def test_plain_content_detected(self):
        self.assertTrue(run()["mime_has_renderable_body"])

    def test_display_name_is_not_provider_domain(self):
        self.assertTrue(run()["sender_display_matches"])

    def test_wrong_sender_detected(self):
        self.assertFalse(run(content=eml(sender="Unknown <donotreply@wordpress.com>"))
                         ["sender_display_matches"])

    def test_exact_subject_matches(self):
        self.assertTrue(run()["expected_subject_matches"])

    def test_wrong_subject_detected(self):
        self.assertFalse(run(content=eml(subject="Different!"))["expected_subject_matches"])

    def test_no_expected_subject_not_inferred(self):
        self.assertFalse(GATE.inspect_eml(eml(), 2)["expected_subject_matches"])

    def test_unsubscribe_header_not_functional_verification(self):
        r = run()
        self.assertEqual(r["unsubscribe"], "PRESENT_NOT_FUNCTIONALLY_TESTED")
        self.assertFalse(r["unsubscribe_function_verified"])

    def test_missing_unsubscribe_identified(self):
        r = run(content=eml(plain="Nothing about opting out.", unsub=False))
        self.assertEqual(r["unsubscribe"], "NOT_FOUND")

    def test_unsubscribe_in_body_only_not_functionally_verified(self):
        r = run(content=eml(plain="Unsubscribe here", unsub=False))
        self.assertEqual(r["unsubscribe"], "PRESENT_NOT_FUNCTIONALLY_TESTED")
        self.assertFalse(r["unsubscribe_function_verified"])

    def test_address_match_not_verified_ownership(self):
        r = run()
        self.assertEqual(r["physical_address"], "TEXT_MATCH_NOT_VERIFIED_OWNERSHIP")
        self.assertFalse(r["postal_ownership_verified"])

    def test_automattic_address_not_final_vestige_address(self):
        r = run(content=eml(plain="20-22 Wenlock Street London N1 7GU. Unsubscribe."))
        self.assertEqual(r["physical_address"], "UNVERIFIED")

    def test_missing_expected_address_not_inferred(self):
        r = GATE.inspect_eml(eml(), 3)
        self.assertEqual(r["physical_address"], "UNVERIFIED")

    def test_commercial_disclosure_found(self):
        self.assertTrue(run()["commercial_disclosure_present"])

    def test_commercial_missing_disclosure(self):
        self.assertFalse(run(content=eml(plain="No affiliate terms."))["commercial_disclosure_present"])

    def test_editorial_not_commercial_classification(self):
        self.assertIsNone(run(edition=1)["commercial_disclosure_present"])

    def test_zen12_direct_merchant_link_detected(self):
        r = run(content=eml(plain=BODY+" https://zen12.com/hnp"))
        self.assertGreater(r["blocked_merchant_or_active_href_count"], 0)

    def test_totalfocus_direct_merchant_link_detected(self):
        r = run(content=eml(html='<a href="https://hypnosislive.com/mental-skills/total-focus">Audio</a>'))
        self.assertGreater(r["blocked_merchant_or_active_href_count"], 0)

    def test_inspire3_subdomain_detected(self):
        r = run(content=eml(html='<a href="https://affiliates.inspire3.com/offer">Affiliate</a>'))
        self.assertGreater(r["blocked_merchant_or_active_href_count"], 0)

    def test_encoded_merchant_redirect_detected(self):
        r = run(content=eml(html='<a href="https://finalvestige.com/go?redirect_url=https%3A%2F%2Fzen12.com%2Fhnp">Route</a>'))
        self.assertGreater(r["blocked_merchant_or_active_href_count"], 0)

    def test_script_href_detected(self):
        r = run(content=eml(html='<a href="javascript:alert(1)">Action</a>'))
        self.assertGreater(r["blocked_merchant_or_active_href_count"], 0)

    def test_safe_focus_url_not_a_seller(self):
        r = run(content=eml(plain=BODY+" https://finalvestige.com/focus/"))
        self.assertEqual(r["blocked_merchant_or_active_href_count"], 0)

    def test_first_party_guide_unpublished_cannot_unlock(self):
        r = run(content=eml(html='<a href="https://finalvestige.com/mind/zen12-guide/">Guide</a>'))
        self.assertTrue(r["guide_url_present"])
        self.assertFalse(r["actual_received_message_verified"])
        self.assertIn("HOLD", r["release"])

    def test_missing_guide_kept_unverified(self):
        self.assertFalse(run()["guide_url_present"])

    def test_vendor_guide_rejected(self):
        r = run(guide="https://zen12.com/hnp")
        self.assertFalse(r["guide_url_first_party"])

    def test_html_only_disclosure_is_detected(self):
        r = run(content=eml(plain="A bare text variant.",html="<p>Final Vestige may earn a commission.</p>"))
        self.assertTrue(r["commercial_disclosure_present"])

    def test_hidden_script_does_not_provide_disclosure(self):
        r = run(content=eml(plain="None",html="<script>may earn a commission</script><p>Hi</p>"))
        self.assertFalse(r["commercial_disclosure_present"])

    def test_detect_tiny_image_without_claiming_tracking(self):
        r = run(content=eml(html='<img width="1" height="1" src="https://pixel.invalid/a">'))
        self.assertEqual(r["possible_remote_1px_image_count"], 1)

    def test_draft_internal_warning_detected(self):
        r = run(content=eml(plain=BODY+" DO NOT PUBLISH OR EMAIL"))
        self.assertTrue(r["draft_instruction_banner_found"])

    def test_do_not_expose_recipients_tokens_or_subject(self):
        data = json.dumps(run())
        for secret in ("SENSITIVE_FAKE_RECIPIENT", "SENSITIVE_FAKE_TOKEN",
                       "TEST ONLY historical record", "Exampleville"):
            self.assertNotIn(secret, data)

    def test_no_raw_merchant_link_in_report(self):
        data = json.dumps(run(content=eml(plain=BODY+" https://zen12.com/hnp")))
        self.assertNotIn("https://zen12.com/hnp", data)

    def test_no_received_claim(self):
        self.assertFalse(run()["actual_received_message_verified"])

    def test_no_native_preheader_claim(self):
        self.assertFalse(run()["native_preheader_verified"])

    def test_no_audience_claim(self):
        self.assertFalse(run()["eligible_audience_verified"])

    def test_no_merchant_permission_claim(self):
        self.assertFalse(run()["merchant_email_permission_verified"])

    def test_no_final_approval_claim(self):
        self.assertFalse(run()["final_founder_send_approval"])

    def test_empty_eml_rejected(self):
        with self.assertRaises(ValueError):
            GATE.inspect_eml(b"", 1)

    def test_huge_eml_rejected(self):
        with self.assertRaises(ValueError):
            GATE.inspect_eml(b"x"*2_000_001, 1)

    def test_invalid_editions_rejected(self):
        for n in (-1, 0, 7):
            with self.assertRaises(ValueError):
                GATE.inspect_eml(eml(), n)

    def test_no_network_sending_code(self):
        s = CODE.read_text(encoding="utf-8")
        for forbidden in ("smtplib", "SMTP(", "sendmail(", "requests.post(", "send_message("):
            self.assertNotIn(forbidden, s)

    def test_output_json_serializable(self):
        self.assertIsInstance(json.loads(json.dumps(run())), dict)

    def test_both_mime_parts_disclosure_present(self):
        r = run(content=eml(plain=BODY, html="<p>"+BODY+"</p>"))
        self.assertTrue(r["commercial_disclosure_in_each_present_alternative"])

    def test_mime_plain_missing_disclosure_cannot_hide_behind_html(self):
        r = run(content=eml(plain="Just the story.", html="<p>Final Vestige may earn a commission.</p>"))
        self.assertTrue(r["commercial_disclosure_present"])
        self.assertFalse(r["commercial_disclosure_in_each_present_alternative"])

    def test_mime_html_missing_disclosure_cannot_hide_behind_plain(self):
        r = run(content=eml(plain=BODY, html="<p>Just the story</p>"))
        self.assertFalse(r["commercial_disclosure_in_each_present_alternative"])

    def test_postal_in_only_one_mime_part_not_sufficient(self):
        r = run(content=eml(plain=BODY, html="<p>No postal address</p>"))
        self.assertEqual(r["physical_address"], "TEXT_MATCH_NOT_VERIFIED_OWNERSHIP")
        self.assertFalse(r["postal_text_in_each_present_alternative"])

    def test_unsubscribe_text_only_in_one_mime_part(self):
        r = run(content=eml(plain=BODY, html="<p>No opt-out details</p>"))
        self.assertFalse(r["unsubscribe_text_in_each_present_alternative"])

    def test_mime_part_presence_audited(self):
        r = run(content=eml(plain=BODY, html="<p>"+BODY+"</p>"))
        self.assertTrue(r["mime_plain_present"])
        self.assertTrue(r["mime_html_present"])

    def test_plain_only_is_available_alternative(self):
        r = run(content=eml())
        self.assertTrue(r["mime_plain_present"])
        self.assertFalse(r["mime_html_present"])
        self.assertTrue(r["commercial_disclosure_in_each_present_alternative"])

if __name__ == "__main__":
    unittest.main()
