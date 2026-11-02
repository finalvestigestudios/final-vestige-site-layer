"""Redacted report rendering tests. Only synthetic MIME, no real subscriber data."""
from email.message import EmailMessage
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / "r70-received-mime"

def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

inspector = load("fv_r70_inspector", "inspect_received_eml.py")
renderer = load("fv_r70_renderer", "render_report.py")

def fake_report():
    m = EmailMessage()
    m["From"] = "Final Vestige <donotreply@wordpress.com>"
    m["To"] = "person123@example.invalid"
    m["Subject"] = "A synthetic inbox exercise"
    m.set_content("Final Vestige may earn a commission. This is synthetic, not a delivery receipt.")
    m.add_alternative(
        '<html lang="en"><body><p>Test only</p>'
        '<a href="https://newsletter.example.invalid/u/SENSITIVE_TOKEN">Unsubscribe</a></body></html>',
        subtype="html",
    )
    return inspector.audit_bytes(m.as_bytes(), edition="03")

class RendererSafetyTests(unittest.TestCase):
    def test_schema_accepted_without_unlock(self):
        r = renderer.clean(fake_report())
        self.assertEqual(r["edition"], "03")
        self.assertTrue(r["blockers"])

    def test_html_is_accessible_static_review(self):
        html = renderer.html_report(fake_report())
        for required in ('lang="en"', "viewport", "<th scope='row'>",
                         "aria-labelledby", "HOLD_UNSENT", "noindex,nofollow", "caption"):
            self.assertIn(required, html)
        self.assertIn("@media(max-width:560px)", html)

    def test_plaintext_is_useful_and_hold(self):
        body = renderer.text_report(fake_report())
        self.assertIn("ISSUE 03 | HOLD_UNSENT | SEND ALLOWED: NO", body)
        self.assertIn("UNRESOLVED REQUIREMENTS", body)
        self.assertIn("not a delivered Jetpack preview", body.lower())

    def test_no_script_tracking_form_or_remote_images(self):
        html = renderer.html_report(fake_report()).lower()
        for bad in ("<script", "<form", "<img ", "<iframe", "http-equiv=\"refresh\"",
                    "onload=", "<link rel=\"stylesheet\""):
            self.assertNotIn(bad, html)

    def test_rendered_report_contains_no_raw_token_recipient_header(self):
        html = renderer.html_report(fake_report())
        plain = renderer.text_report(fake_report())
        for sensitive in ("SENSITIVE_TOKEN", "person123", "donotreply@wordpress.com",
                          "A synthetic inbox exercise", "newsletter.example.invalid"):
            self.assertNotIn(sensitive, html)
            self.assertNotIn(sensitive, plain)

    def test_unknown_private_fields_are_ignored(self):
        sample = fake_report()
        sample["private_raw_body"] = "<script>alert('private')</script>"
        sample["recipient"] = "do.not.echo@example.invalid"
        html = renderer.html_report(sample)
        self.assertNotIn("do.not.echo", html)
        self.assertNotIn("alert", html)

    def test_reject_claimed_release_approval(self):
        sample = fake_report()
        sample["send_allowed"] = True
        with self.assertRaises(ValueError):
            renderer.html_report(sample)

    def test_reject_claimed_released_status(self):
        sample = fake_report()
        sample["release_status"] = "READY"
        with self.assertRaises(ValueError):
            renderer.text_report(sample)

    def test_reject_unknown_schema(self):
        sample = fake_report()
        sample["schema"] = "external/raw-email-v1"
        with self.assertRaises(ValueError):
            renderer.clean(sample)

    def test_reject_unknown_edition(self):
        sample = fake_report()
        sample["edition"] = "07"
        with self.assertRaises(ValueError):
            renderer.clean(sample)

    def test_reject_empty_or_forged_blockers(self):
        sample = fake_report()
        sample["blockers"] = []
        with self.assertRaises(ValueError):
            renderer.html_report(sample)
        sample["blockers"] = ["<img src='https://evil.example.invalid/token'>"]
        with self.assertRaises(ValueError):
            renderer.html_report(sample)

    def test_reject_bad_signal_values(self):
        sample = fake_report()
        sample["signals"]["subject_present"] = "private@example.invalid"
        with self.assertRaises(ValueError):
            renderer.html_report(sample)

    def test_reject_negative_link_count(self):
        sample = fake_report()
        sample["signals"]["html_links_count"] = -1
        with self.assertRaises(ValueError):
            renderer.clean(sample)

    def test_reject_string_link_count(self):
        sample = fake_report()
        sample["signals"]["html_links_count"] = "1"
        with self.assertRaises(ValueError):
            renderer.clean(sample)

    def test_rendered_html_and_plaintext_are_consistent(self):
        sample = fake_report()
        html, txt = renderer.html_report(sample), renderer.text_report(sample)
        self.assertEqual("HOLD_UNSENT" in html, "HOLD_UNSENT" in txt)
        self.assertEqual("ISSUE 03" in txt, True)
        self.assertGreater(html.count("<tr>"), 10)
        self.assertGreater(len(txt.splitlines()), 20)

    def test_human_checks_not_reported_as_real_evidence(self):
        html = renderer.html_report(fake_report()).lower()
        self.assertIn("not a received-mail screenshot", html)
        self.assertIn("functioning opt-out", html) if "functioning opt-out" in html else self.assertIn("validated unsubscribe", html)
        self.assertIn("independently establish actual receipt", html)

    def test_no_merchant_link_in_html(self):
        html = renderer.html_report(fake_report())
        self.assertNotIn("zen12.com", html)
        self.assertNotIn("hypnosislive.com", html)

if __name__ == "__main__":
    unittest.main()
