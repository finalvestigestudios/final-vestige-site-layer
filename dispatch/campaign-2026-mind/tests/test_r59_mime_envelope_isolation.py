"""R59: attached/forwarded MIME content cannot satisfy release evidence.

Synthetic only. No network, subscriber data, sends, publishing or live mail.
"""
from __future__ import annotations

import importlib.util
import json
import unittest
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "r56-mime-evidence" / "mime_inspector.py"
spec = importlib.util.spec_from_file_location("fv_r59_inspector", MODULE)
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)
ISSUES = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))["issues"]
DISCLOSE = "Final Vestige may earn a commission from a qualifying purchase."
POSTAL = "123 Example Lane, Fictionville, ZZ 00000"
SELLER = "https://zen12.com/hnp"
UNSUB = "https://wordpress.com/subscriptions/unsubscribe?dummy=NOT_REAL"


def message(issue=3, root="A reader-facing letter without a financial disclosure.", html=None):
    msg = EmailMessage()
    msg["From"] = "Final Vestige <sender@example.invalid>"
    msg["To"] = "nonexistent@example.invalid"
    msg["Subject"] = ISSUES[issue - 1]["subject"]
    msg.set_content(root)
    if html is not None:
        msg.add_alternative(html, subtype="html")
    return msg


def forwarded(*, plain=DISCLOSE, html=None):
    msg = EmailMessage()
    msg["From"] = "Different Publisher <unknown@example.invalid>"
    msg["To"] = "nobody@example.invalid"
    msg["Subject"] = "Attached, not sent by Final Vestige"
    msg.set_content(plain)
    if html is not None:
        msg.add_alternative(html, subtype="html")
    return msg


def inspect(msg, issue=3, *, source="synthetic"):
    return inspector.inspect_bytes(
        msg.as_bytes(), ISSUES[issue - 1], origin=source,
        postal_address=POSTAL
    )


class EnvelopeIsolation(unittest.TestCase):
    def test_01_attached_forwarded_disclosure_not_root(self):
        msg = message()
        msg.add_attachment(forwarded())
        data = inspect(msg)
        self.assertFalse(data["disclosure_in_text_plain_first_85_words"])
        self.assertFalse(data["disclosure_in_visible_body"])
        self.assertIn("EARLY_COMMERCIAL_DISCLOSURE_MISSING", data["holds"])

    def test_02_forwarded_html_disclosure_not_root(self):
        msg = message(html="<p>Nothing is disclosed here.</p>")
        msg.add_attachment(forwarded(html="<p>" + DISCLOSE + "</p>"))
        data = inspect(msg)
        self.assertFalse(data["disclosure_in_text_html_first_85_words"])
        self.assertFalse(data["disclosure_in_text_plain_first_85_words"])
        self.assertEqual(data["ignored_attachment_or_named_part_count"], 1)

    def test_03_attached_postal_not_a_valid_root_footer(self):
        msg = message()
        msg.add_attachment(forwarded(plain=POSTAL))
        data = inspect(msg)
        self.assertFalse(data["postal_exact_match_to_local_private_value"])
        self.assertIn("VERIFIED_FINAL_VESTIGE_POSTAL_ADDRESS_NOT_PRESENT", data["holds"])

    def test_04_attached_unsubscribe_not_root(self):
        msg = message()
        msg.add_attachment(forwarded(html='<a href="' + UNSUB + '">Unsubscribe</a>'))
        data = inspect(msg)
        self.assertFalse(data["visible_unsubscribe_link_candidate"])
        self.assertIn("UNSUBSCRIBE_MARKUP_CANDIDATE_ABSENT", data["holds"])

    def test_05_attached_merchant_link_not_reader_body_link(self):
        msg = message()
        msg.add_attachment(forwarded(html='<a href="' + SELLER + '">Buy</a>'))
        data = inspect(msg)
        self.assertEqual(data["direct_seller_link_count"], 0)
        self.assertIn("ATTACHMENT_PRESENT_HUMAN_REVIEW", data["holds"])

    def test_06_forwarded_message_content_suppressed_everywhere(self):
        msg = message(root="A clear original letter.")
        msg.add_attachment(forwarded(
            plain=DISCLOSE + " " + POSTAL,
            html='<p>' + DISCLOSE + ' ' + POSTAL + '</p><a href="' + SELLER + '">Go</a>'
        ))
        data = inspect(msg)
        self.assertFalse(data["disclosure_in_visible_body"])
        self.assertFalse(data["postal_exact_match_to_local_private_value"])
        self.assertEqual(data["direct_seller_link_count"], 0)
        self.assertEqual(data["remote_image_count"], 0)

    def test_07_inline_forwarded_message_skipped(self):
        msg = message()
        msg.add_attachment(forwarded())
        attachment = list(msg.iter_attachments())[0]
        attachment.replace_header("Content-Disposition", "inline")
        data = inspect(msg)
        self.assertEqual(data["ignored_inline_forwarded_message_count"], 1)
        self.assertFalse(data["disclosure_in_visible_body"])
        self.assertIn("INLINE_FORWARDED_MESSAGE_IGNORED", data["holds"])

    def test_08_attached_plaintext_named_file_skipped(self):
        msg = message()
        msg.add_attachment(DISCLOSE.encode("utf-8"), maintype="text",
                           subtype="plain", filename="attached-note.txt")
        data = inspect(msg)
        self.assertFalse(data["disclosure_in_text_plain_first_85_words"])
        self.assertEqual(data["top_level_text_plain_part_count"], 1)

    def test_09_inline_filename_text_is_not_root(self):
        msg = message()
        msg.add_attachment(DISCLOSE.encode("utf-8"), maintype="text",
                           subtype="plain", filename="disclosure.txt")
        attached = list(msg.iter_attachments())[0]
        attached.replace_header("Content-Disposition",
                                'inline; filename="disclosure.txt"')
        data = inspect(msg)
        self.assertFalse(data["disclosure_in_text_plain_first_85_words"])
        self.assertEqual(data["ignored_attachment_or_named_part_count"], 1)

    def test_10_attached_html_named_file_skipped(self):
        msg = message(html="<p>Original content</p>")
        msg.add_attachment(('<p>' + DISCLOSE + '</p>').encode("utf-8"),
                           maintype="text", subtype="html", filename="notice.html")
        data = inspect(msg)
        self.assertFalse(data["disclosure_in_text_html_first_85_words"])
        self.assertEqual(data["top_level_text_html_part_count"], 1)

    def test_11_attached_remote_pixel_not_root_visual(self):
        msg = message()
        msg.add_attachment(b'<img src="https://pixels.example.invalid/track">',
                           maintype="text", subtype="html", filename="mail.html")
        data = inspect(msg)
        self.assertEqual(data["remote_image_count"], 0)
        self.assertIn("ATTACHMENT_PRESENT_HUMAN_REVIEW", data["holds"])

    def test_12_attachment_only_email_no_readable_body(self):
        msg = EmailMessage()
        msg["From"] = "Final Vestige <sender@example.invalid>"
        msg["To"] = "nobody@example.invalid"
        msg["Subject"] = ISSUES[2]["subject"]
        msg.add_attachment(DISCLOSE.encode("utf-8"),
                           maintype="text", subtype="plain", filename="letter.txt")
        data = inspect(msg)
        self.assertFalse(data["has_text_plain"])
        self.assertFalse(data["has_text_html"])
        self.assertIn("NO_READABLE_TOP_LEVEL_MESSAGE_BODY", data["holds"])

    def test_13_regular_multipart_alternative_still_parses(self):
        msg = message(root=DISCLOSE, html="<p>" + DISCLOSE + "</p>")
        data = inspect(msg)
        self.assertTrue(data["has_text_plain"])
        self.assertTrue(data["has_text_html"])
        self.assertTrue(data["commercial_disclosure_parity_across_mime_alternatives"])
        self.assertEqual(data["top_level_text_plain_part_count"], 1)
        self.assertEqual(data["top_level_text_html_part_count"], 1)

    def test_14_plain_only_real_disclosure_visible(self):
        data = inspect(message(root=DISCLOSE))
        self.assertTrue(data["disclosure_in_text_plain_first_85_words"])
        self.assertNotIn("EARLY_COMMERCIAL_DISCLOSURE_MISSING", data["holds"])

    def test_15_html_only_real_disclosure_visible(self):
        msg = message()
        msg.set_content("<p>" + DISCLOSE + "</p>", subtype="html")
        data = inspect(msg)
        self.assertTrue(data["disclosure_in_text_html_first_85_words"])
        self.assertTrue(data["commercial_disclosure_parity_across_mime_alternatives"])

    def test_16_ordinary_body_postal_not_legal_certificate(self):
        data = inspect(message(root=POSTAL))
        self.assertTrue(data["postal_exact_match_to_local_private_value"])
        self.assertFalse(data["legal_compliance_certified"])
        self.assertFalse(data["send_allowed"])

    def test_17_multiple_inline_plain_bodies_ambiguous(self):
        msg = message(root=DISCLOSE)
        msg.make_mixed()
        another = EmailMessage()
        another.set_content("A second undisclosed body.")
        msg.attach(another)
        data = inspect(msg)
        self.assertEqual(data["top_level_text_plain_part_count"], 2)
        self.assertIn("AMBIGUOUS_MULTIPLE_MIME_BODY_PARTS", data["holds"])
        self.assertFalse(data["commercial_disclosure_parity_across_mime_alternatives"])

    def test_18_multiple_html_alternatives_ambiguous(self):
        msg = message(root=DISCLOSE, html="<p>" + DISCLOSE + "</p>")
        msg.add_alternative("<p>Another HTML version without disclosure.</p>", subtype="html")
        data = inspect(msg)
        self.assertEqual(data["top_level_text_html_part_count"], 2)
        self.assertIn("AMBIGUOUS_MULTIPLE_MIME_BODY_PARTS", data["holds"])
        self.assertFalse(data["commercial_disclosure_parity_across_mime_alternatives"])

    def test_19_multiple_html_even_if_both_disclose_ambiguous(self):
        msg = message(root=DISCLOSE, html="<p>" + DISCLOSE + "</p>")
        msg.add_alternative("<div>" + DISCLOSE + "</div>", subtype="html")
        data = inspect(msg)
        self.assertIn("AMBIGUOUS_MULTIPLE_MIME_BODY_PARTS", data["holds"])

    def test_20_multiple_plain_editorial_also_hold(self):
        msg = message(issue=1, root="First body")
        msg.make_mixed()
        more = EmailMessage()
        more.set_content("Second body")
        msg.attach(more)
        data = inspect(msg, issue=1)
        self.assertIn("AMBIGUOUS_MULTIPLE_MIME_BODY_PARTS", data["holds"])

    def test_21_duplicate_subject_header_triggers_review(self):
        msg = message()
        raw = b"Subject: Unexpected duplicate\r\n" + msg.as_bytes()
        data = inspector.inspect_bytes(raw, ISSUES[2])
        self.assertEqual(data["duplicate_relevant_header_count"], 1)
        self.assertIn("AMBIGUOUS_DUPLICATE_MESSAGE_HEADERS", data["holds"])

    def test_22_duplicate_sender_header_triggers_review(self):
        msg = message()
        raw = b"From: Other Sender <not-real@example.invalid>\r\n" + msg.as_bytes()
        data = inspector.inspect_bytes(raw, ISSUES[2])
        self.assertIn("AMBIGUOUS_DUPLICATE_MESSAGE_HEADERS", data["holds"])

    def test_23_duplicate_list_unsubscribe_headers_trigger_review(self):
        msg = message()
        raw = (b"List-Unsubscribe: <https://wordpress.com/subscriptions/unsubscribe?example=1>\r\n"
               b"List-Unsubscribe: <https://wordpress.com/subscriptions/unsubscribe?example=2>\r\n"
               + msg.as_bytes())
        data = inspector.inspect_bytes(raw, ISSUES[2])
        self.assertIn("AMBIGUOUS_DUPLICATE_MESSAGE_HEADERS", data["holds"])

    def test_24_empty_root_commercial_has_early_hold(self):
        data = inspect(message(root=""))
        self.assertIn("NO_READABLE_TOP_LEVEL_MESSAGE_BODY", data["holds"])
        self.assertIn("EARLY_COMMERCIAL_DISCLOSURE_MISSING", data["holds"])

    def test_25_empty_root_editorial_unreadable(self):
        data = inspect(message(issue=1, root=""), issue=1)
        self.assertIn("NO_READABLE_TOP_LEVEL_MESSAGE_BODY", data["holds"])

    def test_26_real_vendor_in_root_still_detected(self):
        data = inspect(message(root=DISCLOSE + " " + SELLER))
        self.assertGreaterEqual(data["direct_seller_link_count"], 1)
        self.assertIn("DIRECT_MERCHANT_LINK_BYPASSES_REVIEWED_GUIDE", data["holds"])

    def test_27_offline_origin_not_received_evidence(self):
        data = inspect(message(root=DISCLOSE))
        self.assertFalse(data["source_is_received_message_independently_attested"])
        self.assertIn("NO_ACTUAL_RECEIVED_EMAIL_EVIDENCE", data["holds"])

    def test_28_claiming_received_does_not_grant_send(self):
        data = inspect(message(root=DISCLOSE), source="received")
        self.assertFalse(data["send_allowed"])
        self.assertFalse(data["founder_final_send_approval"])
        self.assertFalse(data["unsubscription_functionally_verified"])
        self.assertFalse(data["legal_compliance_certified"])

    def test_29_report_never_leaks_addresses_or_body(self):
        msg = message(root=DISCLOSE + " PRIVATE_TEST_PHRASE")
        msg.add_attachment(forwarded(plain="HIDDEN_PRIVATE_PHRASE"))
        report = json.dumps(inspect(msg), sort_keys=True)
        for secret in ("PRIVATE_TEST_PHRASE", "HIDDEN_PRIVATE_PHRASE",
                       "sender@example.invalid", "nonexistent@example.invalid"):
            self.assertNotIn(secret, report)

    def test_30_original_six_issue_allocation_unchanged(self):
        self.assertEqual(len(ISSUES), 6)
        self.assertEqual([i["number"] for i in ISSUES if i["kind"] ==
                          "commercial-review-pending"], [3, 5])

    def test_31_no_outbound_transport_or_send_function(self):
        src = MODULE.read_text(encoding="utf-8")
        for bad in ("import requests", "import smtplib", "urlopen(", "sendmail("):
            self.assertNotIn(bad, src)

    def test_32_attached_headers_not_root_duplicates(self):
        msg = message()
        msg.add_attachment(forwarded())
        data = inspect(msg)
        self.assertEqual(data["duplicate_relevant_header_count"], 0)

    def test_33_second_plain_part_cannot_launder_disclosure(self):
        msg = message(root="No disclosure first.")
        msg.make_mixed()
        extra = EmailMessage()
        extra.set_content(DISCLOSE)
        msg.attach(extra)
        data = inspect(msg)
        self.assertIn("AMBIGUOUS_MULTIPLE_MIME_BODY_PARTS", data["holds"])
        self.assertFalse(data["commercial_disclosure_parity_across_mime_alternatives"])

    def test_34_forwarded_attachment_not_extra_body_variant(self):
        msg = message(root=DISCLOSE, html="<p>" + DISCLOSE + "</p>")
        msg.add_attachment(forwarded(plain="an unrelated attachment"))
        data = inspect(msg)
        self.assertEqual(data["top_level_text_plain_part_count"], 1)
        self.assertEqual(data["top_level_text_html_part_count"], 1)
        self.assertIn("ATTACHMENT_PRESENT_HUMAN_REVIEW", data["holds"])


if __name__ == "__main__":
    unittest.main()
