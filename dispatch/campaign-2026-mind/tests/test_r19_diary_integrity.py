"""R19: fail-closed, source-led checks for the unsent Issue 06 evidence-log close."""
import json
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEXT = (ROOT / "issues/06-the-evidence-log.md").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
CTA = "https://finalvestige.com/focus/"
BMJ = "https://www.bmj.com/content/324/7347/1193"
NIH = "https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety"


class DiaryIntegrityGuards(unittest.TestCase):
    def test_01_manifest_and_original_subject_still_match(self):
        issue = MANIFEST["issues"][5]
        self.assertEqual((issue["number"], issue["kind"]), (6, "editorial"))
        self.assertEqual(issue["editorial_cta"], CTA)
        self.assertIn("**Subject:** " + issue["subject"], TEXT)
        self.assertIn("**Preheader:** " + issue["preheader"], TEXT)

    def test_02_original_diary_study_is_specific(self):
        for phrase in ("published in 2002", "pain entries", "90 percent", "11 percent", "narrower timing window"):
            self.assertIn(phrase, TEXT)

    def test_03_study_is_not_misrepresented_as_focus_or_universal(self):
        self.assertIn("not** an experiment about meditation", TEXT)
        self.assertIn("not** an experiment", TEXT)
        self.assertNotIn("all diary keepers lie", TEXT.lower())
        self.assertNotIn("90 percent of everyone lies", TEXT.lower())

    def test_04_original_study_and_nih_source_links(self):
        self.assertEqual(TEXT.count(BMJ), 1)
        self.assertEqual(TEXT.count(NIH), 1)
        self.assertIn("mixed and methodologically varied", TEXT)

    def test_05_four_observation_prompts(self):
        for phrase in ("**When:**", "**What:**", "**Conditions:**", "**Next adjustment:**"):
            self.assertIn(phrase, TEXT)

    def test_06_absence_and_recall_uncertainty(self):
        self.assertIn("A missing entry is worth leaving missing", TEXT)
        self.assertIn("Don't backfill a precise time", TEXT)
        self.assertIn("explanation second", TEXT)

    def test_07_no_unwarranted_causal_inference(self):
        self.assertIn("seven-day personal log cannot settle", TEXT)
        self.assertIn("sleep, workload, expectations, chance", TEXT)
        self.assertNotIn("scientifically proves your attention improved", TEXT.lower())

    def test_08_one_primary_published_cta(self):
        self.assertEqual(TEXT.count(CTA), 1)
        self.assertEqual(TEXT.count("**Open the free Fieldbook:**"), 1)
        self.assertEqual(len(re.findall(r"\*\*Open the free Fieldbook:\*\*", TEXT)), 1)

    def test_09_no_seller_links_or_purchase_offer(self):
        low = TEXT.lower()
        for forbidden in ("inspire3.com", "zen12.com", "hypnosislive.com", "affiliate link", "buy now", "50% off"):
            self.assertNotIn(forbidden, low)

    def test_10_release_holds_and_footer_not_removed(self):
        for token in ("UNSENT DRAFT", "DO NOT PUBLISH OR EMAIL", "[[VALID_POSTAL_ADDRESS_REQUIRED]]", "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"):
            self.assertIn(token, TEXT)

    def test_11_original_six_issues_and_4_2_split_remain_held(self):
        self.assertEqual(len(MANIFEST["issues"]), 6)
        self.assertEqual(sum(i["kind"] == "editorial" for i in MANIFEST["issues"]), 4)
        self.assertEqual(sum(i["kind"] == "commercial-review-pending" for i in MANIFEST["issues"]), 2)
        self.assertTrue(all(i["publish_state"] == "hold" and i["merchant_affiliate_url"] is None for i in MANIFEST["issues"]))

    def test_12_no_claim_to_have_tested_audio_product(self):
        for phrase in ("we personally tried zen12", "our clinical trial", "guaranteed results", "zero adverse effects"):
            self.assertNotIn(phrase, TEXT.lower())

    def test_13_html_and_plaintext_snapshots_exactly_sync(self):
        cmd = ["node", str(ROOT / "tools/build_previews.cjs"), "--check"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_14_previews_are_review_only_and_no_remote_image(self):
        stem = "06-the-evidence-log"
        html = (ROOT / "previews" / (stem + ".html")).read_text(encoding="utf-8")
        txt = (ROOT / "previews" / (stem + ".txt")).read_text(encoding="utf-8")
        self.assertIn("NOT A SENT EMAIL", html)
        self.assertIn("UNSENT DRAFT", txt)
        self.assertNotIn("<img", html.lower())
        self.assertIn("VALID BUSINESS POSTAL ADDRESS REQUIRED", html)
        self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", txt)

    def test_15_excerpt_safe_without_dangerous_promises(self):
        body = TEXT.split("\n---\n")[1]
        opening = " ".join(body.split()[:55]).lower()
        self.assertIn("study", opening)
        self.assertNotIn("guaranteed", opening)
        self.assertNotIn("proven to", opening)


if __name__ == "__main__":
    unittest.main()
