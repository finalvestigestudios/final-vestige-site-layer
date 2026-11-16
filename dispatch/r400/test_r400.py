# R400 offline reviewer acceptance — intentionally refuses release

from __future__ import annotations
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
ISSUE = (ROOT / "ISSUE04_APOLLO_SOURCED_OPTIONAL.md").read_text(encoding="utf-8")
HTML = (ROOT / "ISSUE04_APOLLO_SOURCED_OFFLINE.html").read_text(encoding="utf-8")
PLAIN = (ROOT / "ISSUE04_APOLLO_SOURCED_PLAIN.txt").read_text(encoding="utf-8")
LEDGER = json.loads((ROOT / "SOURCE_CLOCK_LEDGER.json").read_text(encoding="utf-8"))

class R400SourceOnlyTests(unittest.TestCase):
    def test_optional_not_adopted(self):
        self.assertIn("NOT ADOPTED", ISSUE)
        self.assertIn("UNSENT", ISSUE)
        self.assertIn("DO NOT SEND", HTML)
    def test_source_clocks_distinct(self):
        for word in ("fourteen","fifteen","seventeen"):
            self.assertIn(word, ISSUE.lower())
        self.assertIn("different starting points", ISSUE)
    def test_source_provenance(self):
        self.assertEqual(len(LEDGER["facts"]), 5)
        self.assertTrue(all(x["source"].startswith("https://") for x in LEDGER["facts"]))
        self.assertTrue(any("preliminary" in x["status"].lower() for x in LEDGER["facts"]))
    def test_one_primary_cta(self):
        target="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
        self.assertEqual(ISSUE.count("**Read the documented investigation:**"),1)
        self.assertEqual(HTML.count('href="'+target+'"'),1)
        self.assertIn("PRIMARY CTA", PLAIN)
    def test_email_safe_markup(self):
        self.assertIn('role="presentation"',HTML)
        self.assertIn('lang="en"',HTML)
        self.assertIn('name="viewport"',HTML)
        self.assertNotIn("<script",HTML)
        self.assertNotIn("<img",HTML)
        self.assertIn('display:none!important', HTML)
    def test_subject_truth(self):
        self.assertIn("**Subject:** Apollo 1 did not have a single cause",ISSUE)
        self.assertNotIn("Fourteen seconds.",HTML)
        self.assertLess(len("Apollo 1 did not have a single cause"),65)
    def test_no_merchant_leakage(self):
        for obj in (HTML,ISSUE,PLAIN):
            self.assertNotIn("https://zen12.com/",obj)
            self.assertNotIn("https://hypnosislive.com/",obj)
            self.assertNotIn("affiliate_url=",obj)
    def test_all_send_blocks_present(self):
        for obj in (HTML,ISSUE,PLAIN):
            self.assertIn("[[VALID_FV_POSTAL_ADDRESS_REQUIRED]]",obj)
            self.assertIn("[[JETPACK_RENDERED_UNSUBSCRIBE_REQUIRED]]",obj)
    def test_legal_footer_unverified(self):
        self.assertIn("not verified",HTML.lower())
    def test_alt_is_editorial(self):
        self.assertIn("no affiliate product promotion",HTML)
    def test_native_preview_not_claimed(self):
        self.assertIn("Native Jetpack preview",HTML)
    def test_no_misquoted_nasa_numbers(self):
        self.assertNotIn("everyone died in fourteen seconds",ISSUE.lower())
        self.assertNotIn("fourteen seconds was the duration",ISSUE.lower())
    def test_plain_html_consistency(self):
        self.assertIn("Apollo 1 did not have a single cause",HTML)
        self.assertIn("Apollo 1 did not have a single cause",PLAIN)
    def test_source_link_present(self):
        for url in ("https://www.nasa.gov/mission/apollo-1/","https://nssdc.gsfc.nasa.gov/planetary/lunar/apollo1info.html"):
            self.assertIn(url,ISSUE)
    def test_sender_and_no_fake_preheader_feature(self):
        self.assertIn("Final Vestige Studios",HTML)
        self.assertIn("Preheader:",ISSUE)
        self.assertNotIn("Jetpack has a custom preheader control",ISSUE)
    def test_offline_only(self):
        self.assertIn("OFFLINE REVIEW ONLY",HTML)
    def test_source_uncertainty(self):
        self.assertIn("not conclusively identified",ISSUE)
    def test_factual_source_scope(self):
        self.assertIn("1967",ISSUE)
        self.assertIn("Review Board", ISSUE)

if __name__ == "__main__":
    unittest.main()
