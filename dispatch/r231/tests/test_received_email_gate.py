"""Synthetic-only email fixtures. No live recipients, URLs or sends."""
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from received_email_gate import HOLD, MAX_EML_BYTES, inspect_received_email

ADDRESS = "Final Vestige Studios, Example Suite 200, Exampletown, CA 00000"
SUBJECT = "The mind is not a camera"

def fixture(*, subject=SUBJECT, text=True, html=True, address=ADDRESS,
            optout=True, header=True, date=True, sender=True, placeholder=False):
    msg = EmailMessage()
    if sender: msg["From"] = "Test Publisher <publisher@example.invalid>"
    msg["To"] = "TEST RECIPIENT <person@example.invalid>"
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain="example.invalid")
    if date: msg["Date"] = formatdate(localtime=False, usegmt=True)
    if header: msg["List-Unsubscribe"] = "<https://example.invalid/unsubscribe/test-token>"
    if optout:
        opt = "Unsubscribe: https://example.invalid/unsubscribe/test-token"
        link = '<a href="https://example.invalid/unsubscribe/test-token">Unsubscribe</a>'
    else:
        opt, link = "", ""
    token = "[[VALID_POSTAL_ADDRESS_REQUIRED]]" if placeholder else address
    if text:
        msg.set_content("Body. " + token + " " + opt)
    if html:
        html_body = "<html><body><p>Body. " + token + "</p>" + link + "</body></html>"
        if text: msg.add_alternative(html_body, subtype="html")
        else: msg.set_content(html_body, subtype="html")
    return msg.as_bytes()

class Gate(unittest.TestCase):
    def check(self, raw=None, **kw):
        return inspect_received_email(fixture() if raw is None else raw,
                  expected_subject=SUBJECT, verified_publisher_address=ADDRESS, **kw)

    def test_synthetic_candidate_always_hold(self):
        r=self.check(); self.assertEqual(r["state"],HOLD)
        self.assertEqual(r["proof_level"],"OFFLINE_BYTES_ONLY")
    def test_candidate_has_no_offline_failures(self):
        self.assertEqual(self.check()["blockers"],[])
    def test_never_claims_delivered(self):
        self.assertNotIn("PASS_SEND",json.dumps(self.check()))
    def test_no_email_address_leak(self):
        self.assertNotIn("person@example.invalid",json.dumps(self.check()))
    def test_no_publisher_address_leak(self):
        self.assertNotIn(ADDRESS,json.dumps(self.check()))
    def test_no_token_leak(self):
        self.assertNotIn("test-token",json.dumps(self.check()))
    def test_no_tracking_message_id(self):
        self.assertNotIn("@example.invalid",json.dumps(self.check()))
    def test_missing_raw(self):
        self.assertIn("EML_MISSING",self.check(b"")["blockers"][0])
    def test_excessive_raw(self):
        self.assertIn("EXCEEDS_LIMIT",self.check(b"x"*(MAX_EML_BYTES+1))["blockers"][0])
    def test_not_bytes(self):
        self.assertTrue(self.check("not bytes")["blockers"])
    def test_subject_mismatch(self):
        self.assertFalse(self.check(fixture(subject="Fake urgency"))["checks"]["subject_exactly_matches_reviewed_copy"])
    def test_missing_sender(self):
        self.assertFalse(self.check(fixture(sender=False))["checks"]["has_sender_header"])
    def test_missing_date(self):
        self.assertFalse(self.check(fixture(date=False))["checks"]["has_date_header"])
    def test_only_html_warns(self):
        self.assertFalse(self.check(fixture(text=False))["checks"]["has_text_plain"])
    def test_only_text_warns(self):
        self.assertFalse(self.check(fixture(html=False))["checks"]["has_text_html"])
    def test_no_postal_evidence(self):
        self.assertFalse(self.check(fixture(address="Nothing applicable"))["checks"]["verified_publisher_address_visible"])
    def test_no_auto_address_ownership(self):
        self.assertFalse(inspect_received_email(fixture(), expected_subject=SUBJECT,
             verified_publisher_address="Automattic, 60 29th Street, San Francisco, CA 94110")["checks"]["verified_publisher_address_visible"])
    def test_placeholders_fail(self):
        self.assertFalse(self.check(fixture(placeholder=True))["checks"]["no_placeholder_tokens_in_visible_copy"])
    def test_no_unsub_fails(self):
        r=self.check(fixture(optout=False,header=False));self.assertFalse(r["checks"]["syntactic_optout_candidate"])
    def test_only_list_header_is_syntactic_not_functional(self):
        r=self.check(fixture(optout=False,header=True));self.assertTrue(r["checks"]["syntactic_optout_candidate"])
        self.assertIn("Live unsubscribe operation and opt-out suppression after request",r["manual_checks_required"])
    def test_only_body_unsub_is_syntactic(self):
        self.assertTrue(self.check(fixture(optout=True,header=False))["checks"]["syntactic_optout_candidate"])
    def test_never_clears_affiliate(self):
        self.assertTrue(any("Affiliate acceptance" in x for x in self.check()["manual_checks_required"]))
    def test_never_clears_founder(self):
        self.assertTrue(any("Founder final" in x for x in self.check()["manual_checks_required"]))
    def test_even_all_green_candidate_hold(self):
        r=self.check();self.assertTrue(all(v for k,v in r["checks"].items() if k not in ["contains_header_defects","has_one_click_header_claim"]))
        self.assertEqual(r["state"],HOLD)

if __name__=="__main__": unittest.main()
