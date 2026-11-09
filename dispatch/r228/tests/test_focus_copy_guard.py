import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from focus_copy_guard import audit, safe_help_copy

class CopyChecks(unittest.TestCase):
    def test_detects_actual_live_wording(self):
        self.assertFalse(audit('Open this page in Safari or Chrome and sign up again.').passes)
    def test_detects_second_form_instruction(self):
        self.assertFalse(audit('Enter your email again to open your PDF.').passes)
    def test_detects_resubscribe(self):
        self.assertFalse(audit('Subscribe again now.').passes)
    def test_detects_false_conversion(self):
        self.assertFalse(audit('Downloading the file makes you a confirmed subscriber.').passes)
    def test_accepts_clear_help_copy(self):
        self.assertTrue(audit(safe_help_copy()).passes)
    def test_says_no_repeat_and_not_confirmation(self):
        t=safe_help_copy().lower()
        self.assertIn('do not enter your email again',t)
        self.assertIn('not proof',t)
    def test_accepts_valid_factual_explanation(self):
        self.assertTrue(audit('Existing verified WordPress.com users may skip a separate confirmation email.').passes)
    def test_malicious_url_is_inert_text(self):
        self.assertTrue(audit('https://finalvestige.com/?subscribe=pending').passes)
    def test_non_string_rejected(self):
        with self.assertRaises(TypeError): audit(None)
    def test_not_overbroad_download_note(self):
        self.assertTrue(audit('Download the PDF from the existing welcome email.').passes)

if __name__=='__main__': unittest.main()
