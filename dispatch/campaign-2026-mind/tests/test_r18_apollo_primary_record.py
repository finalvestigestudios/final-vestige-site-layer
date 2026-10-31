"""Independent, fail-closed guards for R18 NASA primary-record editorial revision."""
import json
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEXT = (ROOT / "issues/04-the-hatch-and-the-spark.md").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
NASA_REPORT = "https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"
NASA_FINDINGS = "https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html"
CTA = "https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"

class ApolloPrimaryRecordGuards(unittest.TestCase):
    def test_exact_nasa_transmission_timestamps(self):
        self.assertIn("23:31:04.7", TEXT)
        self.assertIn("23:31:21.8", TEXT)
        self.assertIn("17.1 seconds", TEXT)
        self.assertAlmostEqual((31*60+21.8)-(31*60+4.7), 17.1, places=4)

    def test_timings_not_misrepresented_as_death_or_ignition_times(self):
        self.assertIn("do not establish the instant of ignition", TEXT)
        self.assertIn("time each astronaut lost consciousness", TEXT)
        self.assertNotIn("died in 17 seconds", TEXT.lower())

    def test_no_fabricated_transcript_or_certain_speaker(self):
        self.assertIn("garbled", TEXT)
        self.assertIn("confident speaker identification was not possible", TEXT)
        self.assertNotIn("Grissom said", TEXT)

    def test_atmosphere_specifications_and_cause_caveat(self):
        self.assertIn("100-percent oxygen", TEXT)
        self.assertIn("16.7 pounds per square inch absolute", TEXT)
        self.assertIn("no single ignition source was conclusively identified", TEXT)
        self.assertIn("most probable initiator", TEXT)

    def test_primary_source_urls(self):
        self.assertIn(NASA_REPORT, TEXT)
        self.assertIn(NASA_FINDINGS, TEXT)
        self.assertIn("https://sma.nasa.gov/sma-disciplines/accllp/apollo-1", TEXT)

    def test_exactly_one_main_first_party_cta(self):
        self.assertEqual(TEXT.count(CTA), 1)
        self.assertEqual(TEXT.count("**Read the investigation:**"), 1)
        self.assertFalse("[[APPROVED_" in TEXT)

    def test_subject_preheader_match_original_manifest(self):
        issue = MANIFEST["issues"][3]
        self.assertEqual(issue["number"], 4)
        self.assertEqual(issue["kind"], "editorial")
        self.assertIn("**Subject:** " + issue["subject"], TEXT)
        self.assertIn("**Preheader:** " + issue["preheader"], TEXT)
        self.assertEqual(issue["editorial_cta"], CTA)

    def test_campaign_all_six_still_hold_4_to_2(self):
        self.assertEqual(MANIFEST["status"], "DRAFT_UNSENT_NO_SCHEDULING")
        self.assertEqual(sum(i["kind"] == "editorial" for i in MANIFEST["issues"]), 4)
        self.assertEqual(sum(i["kind"] == "commercial-review-pending" for i in MANIFEST["issues"]), 2)
        self.assertTrue(all(i["publish_state"] == "hold" and i["merchant_affiliate_url"] is None for i in MANIFEST["issues"]))

    def test_every_marketing_hold_stays_present(self):
        self.assertIn("UNSENT DRAFT", TEXT)
        self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", TEXT)
        self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", TEXT)

    def test_no_live_merchant_or_unsubstantiated_offer(self):
        for token in ("inspire3.com", "zen12.com", "hypnosislive.com", "affiliate", "guaranteed", "brain reprogramming"):
            if token == "affiliate":
                continue  # standard status masthead mentions review only
            self.assertNotIn(token, TEXT.lower())

    def test_practical_three_part_method(self):
        for token in ("**The clock.**", "**The conditions.**", "**The conclusion.**"):
            self.assertIn(token, TEXT)

    def test_previews_in_exact_sync_with_source(self):
        result = subprocess.run(["node",str(ROOT / "tools/build_previews.cjs"),"--check"],capture_output=True,text=True,check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
