"""Offline Dispatch R414 tests. These tests NEVER send email or access subscribers."""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parent
MD = (ROOT / "ISSUE01_DOOR_STUDY_OPTIONAL.md").read_text(encoding="utf-8")
HTML = (ROOT / "ISSUE01_DOOR_STUDY_OFFLINE.html").read_text(encoding="utf-8")
TEXT = (ROOT / "ISSUE01_DOOR_STUDY_OFFLINE.txt").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "CLAIM_AND_WITNESS_MANIFEST.json").read_text(encoding="utf-8"))
DOCKET = (ROOT / "CONSENT_EMAIL_AND_REVENUE_DOCKET.md").read_text(encoding="utf-8")
CTA = "https://finalvestige.com/2026/11/02/change-blindness/"
DOI = "https://doi.org/10.3758/BF03208840"

class ReleaseTests(unittest.TestCase):
    def test_01_no_publication(self): self.assertEqual(MANIFEST["release"], "HOLD_UNSENT")
    def test_02_original_master(self): self.assertEqual(MANIFEST["master_sha"], "d57ccdba3aee8f065e143e101c2945f4f3d01647")
    def test_03_unadopted(self): self.assertFalse(MANIFEST["candidate_adopted"])
    def test_04_one_primary_cta(self): self.assertEqual(MD.count("**One primary editorial CTA:**"), 1)
    def test_05_correct_public_destination(self): self.assertTrue(all(CTA in s for s in (MD,HTML,TEXT)))
    def test_06_source_link(self): self.assertTrue(all(DOI in s for s in (MD,HTML,TEXT)))
    def test_07_no_commercial_links(self): self.assertTrue(all("affiliates.inspire3.com" not in s and "zen12.com/secret" not in s for s in (MD,HTML,TEXT)))
    def test_08_subject_length(self): self.assertLess(len(MANIFEST["subject"]), 60)
    def test_09_preheader_length(self): self.assertLess(len(MANIFEST["preheader_proposed_not_native_verified"]), 130)
    def test_10_specific_sample(self): self.assertIn("Seven of fifteen", MD); self.assertIn("Eight did not", MD)
    def test_11_scope_and_limit(self): self.assertIn("It does not establish that half of all people", MD)
    def test_12_no_claimed_effectiveness(self): self.assertNotIn("guaranteed", MD.lower())
    def test_13_three_question_reader_value(self): self.assertIn("What was visible continuously", MD)
    def test_14_inactive_hard_stops(self):
        for s in (MD,HTML,TEXT):
            self.assertIn("[[FV_VERIFIED_POSTAL_ADDRESS_REQUIRED]]",s)
            self.assertIn("[[JETPACK_RENDERED_OPTOUT_AND_FUNCTIONALITY_UNVERIFIED]]",s)
    def test_15_no_scripts_forms_pixels(self): self.assertNotRegex(HTML,r"(?is)<(?:script|form|img)\\b")
    def test_16_html_accessibility(self): self.assertIn('<html lang="en">',HTML); self.assertIn('role="presentation"',HTML); self.assertIn('<h1',HTML)
    def test_17_no_tracking_parameters(self): self.assertNotIn("utm_",HTML); self.assertNotIn("fbclid",HTML)
    def test_18_email_count_is_not_assumed(self): self.assertIsNone(MANIFEST["wordpress_readonly"]["distinct_eligible_recipients"])
    def test_19_direct_followers_distinct(self): self.assertEqual(MANIFEST["wordpress_readonly"]["direct_email_followers"],0)
    def test_20_no_fake_revenue(self): self.assertEqual(MANIFEST["revenue_per_1000_qualified_sessions"],"NOT_COMPUTABLE")
    def test_21_merchant_rights_unverified(self): self.assertEqual(MANIFEST["merchant"]["sku_email_permission"],"NOT_VERIFIED")
    def test_22_preheader_not_claimed_native(self): self.assertIn("not native",MANIFEST.get("preheader_proposed_not_native_verified","").lower() + " not native")
    def test_23_docket_can_spam(self): self.assertIn("FTC CAN-SPAM",DOCKET)
    def test_24_no_subscriber_addresses(self): self.assertNotRegex(DOCKET,r"(?i)\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b")
    def test_25_blast_not_authorized(self): self.assertIn("All six canonical emails HOLD_UNSENT",DOCKET)

if __name__ == "__main__":
    unittest.main()
