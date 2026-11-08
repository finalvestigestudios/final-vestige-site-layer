"""End-to-end local synthetic preview generation; never contacts real addresses."""
import importlib.util
from pathlib import Path
import tempfile
import json
import unittest

ROOT = Path(__file__).resolve().parents[1] / "r70-received-mime"
spec = importlib.util.spec_from_file_location("fv_r70_synthetic_preview", ROOT / "make_synthetic_preview.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

class SyntheticPipelineTests(unittest.TestCase):
    def run_generator(self):
        temp = tempfile.TemporaryDirectory()
        try:
            files = gen.generate(Path(temp.name))
            outputs = {k: path.read_text(encoding="utf-8") for k, path in files.items()}
            names = {k: path.name for k, path in files.items()}
            return outputs, names
        finally:
            temp.cleanup()

    def test_all_three_preview_formats_created(self):
        outputs, names = self.run_generator()
        self.assertEqual(set(outputs), {"html", "text", "json"})
        self.assertEqual(names["html"], "synthetic-review.html")
        self.assertIn("<!doctype html>", outputs["html"])

    def test_json_stays_fail_closed(self):
        outputs, _ = self.run_generator()
        data = json.loads(outputs["json"])
        self.assertEqual(data["edition"], "03")
        self.assertFalse(data["send_allowed"])
        self.assertEqual(data["release_status"], "HOLD_UNSENT")

    def test_real_format_checks_do_not_mean_send_approval(self):
        outputs, _ = self.run_generator()
        data = json.loads(outputs["json"])
        self.assertTrue(data["signals"]["subject_matches_selected_copy"])
        self.assertTrue(data["signals"]["postal_text_matches_private_publisher_reference"])
        self.assertTrue(data["signals"]["unsubscribe_labeled_https_link_present"])
        self.assertTrue(data["signals"]["commercial_disclosure_within_first_55_visible_words"])
        self.assertIn("OPT_OUT_REACHABILITY_AND_SUCCESS_REQUIRE_AUTHORIZED_HUMAN_TEST", data["blockers"])

    def test_no_real_email_address_or_token_in_any_report(self):
        outputs, _ = self.run_generator()
        joined = "\n".join(outputs.values())
        for prohibited in ("nobody@example.invalid", "donotreply@wordpress.com",
                           "FAKE_NOOP", "optout.example.invalid", gen.FAKE_POSTAL):
            self.assertNotIn(prohibited, joined)

    def test_html_declares_synthetic_not_jetpack_preview(self):
        outputs, _ = self.run_generator()
        self.assertIn("HOLD_UNSENT", outputs["html"])
        self.assertIn("synthetic fixtures", outputs["html"].lower())
        self.assertIn('name="robots"', outputs["html"])

    def test_plaintext_is_redacted_and_reviewable(self):
        outputs, _ = self.run_generator()
        txt = outputs["text"]
        self.assertIn("SYNTHETIC", gen.FAKE_SUBJECT)
        self.assertIn("ISSUE 03", txt)
        self.assertIn("SEND ALLOWED: NO", txt)
        self.assertNotIn(gen.FAKE_SUBJECT, txt)

    def test_no_network_or_mail_server_imports(self):
        code = (ROOT / "make_synthetic_preview.py").read_text(encoding="utf-8")
        for prohibited in ("smtplib", "requests", "urllib.request", "http.client",
                           "send_message(", "sendmail("):
            self.assertNotIn(prohibited, code)

    def test_no_eml_file_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            gen.generate(Path(directory))
            self.assertFalse(list(Path(directory).glob("*.eml")))

if __name__ == "__main__":
    unittest.main()
