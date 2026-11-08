import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "r63-puysegur-letter"
MANIFEST = ROOT / "manifest.json"

class PuysegurOriginalEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (R / "source-audit.md").read_text(encoding="utf-8")
        cls.txt = (R / "issue02-offline-review.txt").read_text(encoding="utf-8")
        cls.html = (R / "issue02-offline-review.html").read_text(encoding="utf-8")
        cls.note = (R / "release-note.md").read_text(encoding="utf-8")
        cls.status = json.loads((R / "review-status.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_01_original_campaign_still_six(self):
        self.assertEqual(len(self.manifest["issues"]), 6)
    def test_02_original_four_two_mix(self):
        self.assertEqual([x["kind"] for x in self.manifest["issues"]].count("editorial"), 4)
        self.assertEqual([x["kind"] for x in self.manifest["issues"]].count("commercial-review-pending"), 2)
    def test_03_parent_release_unapproved(self):
        self.assertFalse(self.status["optional_copy_approved"])
        self.assertFalse(self.status["canonicals_edited"])
        self.assertTrue(all(x["release"]=="HOLD_UNSENT" for x in self.status["editions"]))
    def test_04_commercial_stays_hold(self):
        self.assertEqual([x["number"] for x in self.status["editions"] if x["merchant"]], [3,5])
        self.assertTrue(all(x["merchant"]=="HOLD_MERCHANT" for x in self.status["editions"] if x["merchant"]))
    def test_05_may4_is_attributed_not_proven(self):
        self.assertIn("4 May 1784", self.source)
        self.assertIn("8 May 1784", self.source)
        self.assertEqual(self.status["historical"]["may4_1784_event"], "reported_by_Puysegur_not_independently_verified")
    def test_06_two_timings_not_exact_outcomes(self):
        self.assertIn("five minutes", self.source)
        self.assertIn("half-quarter", self.source)
        self.assertIn("not independent clocks", self.source)
    def test_07_failed_case_in_record(self):
        self.assertIn("17-year-old", self.source)
        self.assertIn("seventeen-year-old", self.txt)
    def test_08_source_misread_risk_visible(self):
        self.assertIn("1754", self.source)
        self.assertFalse(self.status["historical"]["first_edition_pdf_page_image_read"])
    def test_09_one_editorial_cta(self):
        cta = "https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"
        self.assertIn(cta, self.txt)
        self.assertEqual(self.html.count('href="'+cta+'"'),1)
        self.assertNotIn("zen12.com",self.html.lower())
        self.assertNotIn("hypnosislive.com",self.html.lower())
        self.assertNotIn("affiliates.inspire3.com",self.html.lower())
    def test_10_source_links_present_in_both(self):
        for link in ["https://archive.org/details/mmoirespourservi00chas",
                     "https://www.circee.org/puysegur-memoires-pour-servir-a-l-histoire-du-magnetisme-animal-1784/",
                     "https://catalogue.bnf.fr/ark:/12148/cb31160297p"]:
            self.assertIn(link, self.source)
            self.assertIn(link, self.txt)
            self.assertIn(link, self.html)
    def test_11_both_formats_fail_closed(self):
        for content in (self.html,self.txt):
            self.assertIn("[[VALID_FINAL_VESTIGE_POSTAL_ADDRESS_REQUIRED]]", content)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", content)
            self.assertIn("UNSENT", content)
    def test_12_html_inert_and_accessible(self):
        lower=self.html.lower()
        self.assertIn('lang="en"',lower)
        self.assertIn('role="presentation"',lower)
        self.assertIn('name="viewport"',lower)
        for bad in ("<script", "<form", "<iframe", "tracking-pixel", "utm_source", "<img", "onload=", "javascript:"):
            self.assertNotIn(bad,lower)
    def test_13_subject_remains_canonical(self):
        subject = next(x["subject"] for x in self.manifest["issues"] if x["number"]==2)
        self.assertIn("Subject: "+subject,self.txt)
        self.assertIn("<title>"+subject+" — UNSENDABLE",self.html)
    def test_14_jetpack_preheader_not_claimed(self):
        self.assertIn("NOT a verified Jetpack-native field",self.txt)
        self.assertIn("Jetpack preheader support unverified",self.html)
    def test_15_readonly_wordpress_configuration(self):
        n=self.status["newsletter"]
        self.assertTrue(n["enabled"])
        self.assertFalse(n["email_new_posts_by_default"])
        self.assertEqual(n["email_content_format"],"excerpt")
        self.assertFalse(n["welcome_received_verified"])
        self.assertEqual(n["counts"],{"total":2,"confirmed":2,"unconfirmed":2,"suppressed":0})
    def test_16_realworld_gates_all_false(self):
        self.assertTrue(all(v is False for v in self.status["gates"].values()))
    def test_17_no_unverified_merchant_or_metrics(self):
        for s in (self.txt,self.html):
            for forbidden in ("$87.99","$24.44","100% focus","verified commission","click-through rate"):
                self.assertNotIn(forbidden,s)
    def test_18_source_note_consistent_with_copy(self):
        self.assertIn("The date is less mysterious",self.txt)
        self.assertIn("One patient, two different clocks",self.txt)
        self.assertIn("The date is less mysterious",self.html)
        self.assertIn("One patient, two different clocks",self.html)
    def test_19_no_false_sent_status(self):
        self.assertEqual(self.status["status"],"REVIEW_ONLY_ALL_HOLD_UNSENT")
        self.assertIn("No sending/testing/publishing",self.note)
    def test_20_no_changed_master_files(self):
        self.assertTrue((ROOT / "issues" / "02-before-hypnosis-had-a-name.md").exists())
        self.assertEqual(self.manifest["issues"][1]["publish_state"],"hold")

if __name__=="__main__":
    unittest.main()
