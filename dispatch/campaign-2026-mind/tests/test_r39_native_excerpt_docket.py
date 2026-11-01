"""R39 exact-source fail-closed WordPress excerpt/sending-semantics tests.

All tests are read-only; adversarial cases mutate temporary copies, not campaign files.
"""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "r39-native-excerpt" / "native_excerpt_docket.py"
SPEC = importlib.util.spec_from_file_location("r39_native_excerpt_docket", SCRIPT)
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)
EVIDENCE = ROOT / "r39-native-excerpt" / "LIVE_READ_ONLY_EVIDENCE.json"


class NativeExcerptDocket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = D.build_docket()
        cls.entries = cls.report["six_issues"]

    def test_01_six_issues(self): self.assertEqual(len(self.entries), 6)
    def test_02_exact_order(self): self.assertEqual([x["number"] for x in self.entries], list(range(1, 7)))
    def test_03_editorial_mix(self): self.assertEqual(sum(x["kind"] == "editorial" for x in self.entries), 4)
    def test_04_commercial_mix(self): self.assertEqual(sum(x["kind"] == "commercial-review-pending" for x in self.entries), 2)
    def test_05_zero_sends(self): self.assertFalse(self.report["transmission_or_wordpress_write_performed"])
    def test_06_global_hold(self): self.assertTrue(self.report["all_six_hold"])
    def test_07_commercial_hold(self): self.assertTrue(self.report["commercial_03_and_05_hold"])
    def test_08_each_held(self): self.assertTrue(all(not x["approved_for_publication_or_email"] for x in self.entries))
    def test_09_no_native_eml(self): self.assertTrue(all(not x["actual_received_email_verified"] for x in self.entries))
    def test_10_no_installed_custom_excerpt(self): self.assertTrue(all(not x["custom_excerpt_placed_into_wordpress_post_verified"] for x in self.entries))
    def test_11_no_verified_preheader(self): self.assertTrue(all(not x["planned_preheader_native_setting_verified"] for x in self.entries))
    def test_12_raw_markdown_risk(self):
        self.assertTrue(all(x["raw_draft_warning_would_be_visible_if_pasted"] for x in self.entries))
    def test_13_first_55_story_not_metadata(self):
        self.assertTrue(all("DO NOT PUBLISH" not in x["default_55_word_story_simulation"] for x in self.entries))
    def test_14_model_not_received(self): self.assertEqual(self.report["model"], "R39_READ_ONLY_NOT_RECEIVED_EMAIL")
    def test_15_editorial_merchant_links_none(self):
        self.assertTrue(all(not x["direct_merchant_source_urls_in_canonical_body"] for x in self.entries if x["kind"] == "editorial"))
    def test_16_issue03_has_direct_seller_routes(self):
        self.assertEqual(len(self.entries[2]["direct_merchant_source_urls_in_canonical_body"]), 2)
    def test_17_issue05_has_no_direct_seller_route(self):
        self.assertEqual(self.entries[4]["direct_merchant_source_urls_in_canonical_body"], [])
    def test_18_both_commercial_default_snippets_lack_disclosure(self):
        self.assertFalse(self.entries[2]["commercial_disclosure_in_story_55_word_simulation"])
        self.assertFalse(self.entries[4]["commercial_disclosure_in_story_55_word_simulation"])
    def test_19_proposed_commercial_excerpts_disclose(self):
        self.assertTrue(self.entries[2]["commercial_disclosure_in_proposed_custom_excerpt"])
        self.assertTrue(self.entries[4]["commercial_disclosure_in_proposed_custom_excerpt"])
    def test_20_observation_time(self):
        self.assertEqual(self.report["wordpress_observed_utc"], "2026-11-01T08:32:17Z")
    def test_21_counters_nonadditive(self):
        self.assertIn("Non-additive", self.report["subscriber_count_interpretation"])
    def test_22_specific_offer_type(self):
        self.assertEqual([self.entries[2]["kind"],self.entries[4]["kind"]], ["commercial-review-pending"]*2)
    def test_23_seller_paths_not_affiliate(self):
        self.assertFalse(any("clickbank" in u for x in self.entries for u in x["direct_merchant_source_urls_in_canonical_body"]))
    def test_24_no_private_personal_data(self):
        s = json.dumps(self.report)
        self.assertNotIn("@gmail.com", s); self.assertNotIn("subscriber_email", s)
    def test_25_true_external_source_strings(self):
        d = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertIn("total-focus", d["commercial_evidence"]["hypnosis_total_focus"])
        self.assertIn("zen12.com", d["commercial_evidence"]["zen12_offer"])

    def replacement_test(self, change):
        with tempfile.TemporaryDirectory() as tmp:
            temp = pathlib.Path(tmp)
            (temp/"issues").mkdir(); (temp/"delivery").mkdir()
            for file in (ROOT/"issues").glob("*.md"): shutil.copy2(file, temp/"issues"/file.name)
            shutil.copy2(ROOT/"manifest.json", temp/"manifest.json")
            shutil.copy2(ROOT/"delivery"/"wordpress_excerpt_copy.json", temp/"delivery"/"wordpress_excerpt_copy.json")
            fresh = temp/"evidence.json"; shutil.copy2(EVIDENCE, fresh)
            change(temp, fresh)
            with self.assertRaises(ValueError): D.build_docket(temp, fresh)

    def test_26_reject_auto_send_change(self):
        def f(t,e):
            a=json.loads(e.read_text());a["authenticated_wordpress"]["email_new_posts_by_default"]=True;e.write_text(json.dumps(a))
        self.replacement_test(f)
    def test_27_reject_excerpt_mode_change(self):
        def f(t,e):
            a=json.loads(e.read_text());a["authenticated_wordpress"]["email_content_format"]="full";e.write_text(json.dumps(a))
        self.replacement_test(f)
    def test_28_reject_unreported_sends(self):
        def f(t,e):
            a=json.loads(e.read_text());a["authenticated_wordpress"]["recent_send_count"]=1;e.write_text(json.dumps(a))
        self.replacement_test(f)
    def test_29_reject_fabricated_proof(self):
        def f(t,e):
            a=json.loads(e.read_text());a["proofs"]["actual_delivered_newsletter_eml"]=True;e.write_text(json.dumps(a))
        self.replacement_test(f)
    def test_30_reject_count_drift(self):
        def f(t,e):
            a=json.loads(e.read_text());a["authenticated_wordpress"]["subscriber_counts"]["total"]=3;e.write_text(json.dumps(a))
        self.replacement_test(f)
    def test_31_reject_manifest_publication(self):
        def f(t,e):
            p=t/"manifest.json";a=json.loads(p.read_text());a["issues"][0]["publish_state"]="publish";p.write_text(json.dumps(a))
        self.replacement_test(f)
    def test_32_reject_subject_drift(self):
        def f(t,e):
            p=t/"manifest.json";a=json.loads(p.read_text());a["issues"][0]["subject"]="Special offer";p.write_text(json.dumps(a))
        self.replacement_test(f)
    def test_33_reject_missing_commercial_disclosure_in_custom_excerpt(self):
        def f(t,e):
            p=t/"delivery"/"wordpress_excerpt_copy.json";a=json.loads(p.read_text());a["entries"][2]["excerpt"]="Just buy the recording.";p.write_text(json.dumps(a))
        self.replacement_test(f)
    def test_34_reject_new_earning_link(self):
        def f(t,e):
            p=t/"issues"/"03-the-twelve-minute-question.md"
            p.write_text(p.read_text()+"\nhttps://hop.clickbank.net/not-authorized\n")
        self.replacement_test(f)
    def test_35_reject_missing_postal_marker(self):
        def f(t,e):
            p=t/"issues"/"01-the-mind-is-not-a-camera.md"
            p.write_text(p.read_text().replace("[[VALID_POSTAL_ADDRESS_REQUIRED]]",""))
        self.replacement_test(f)
    def test_36_reject_merchant_link_in_editorial_issue(self):
        def f(t,e):
            p=t/"issues"/"02-before-hypnosis-had-a-name.md"
            s=p.read_text();p.write_text(s.replace("\n---\n","\n---\nhttps://zen12.com/hnp\n",1))
        self.replacement_test(f)
    def test_37_reject_missing_header_separator(self):
        def f(t,e):
            p=t/"issues"/"06-the-evidence-log.md"
            p.write_text(p.read_text().replace("\n---\n","\n",1))
        self.replacement_test(f)
    def test_38_cli_summary(self):
        p=subprocess.run([sys.executable,str(SCRIPT)],capture_output=True,text=True,check=True)
        self.assertIn("ALL SIX HOLD_UNSENT",p.stdout)
        self.assertIn("03/05 HOLD_MERCHANT",p.stdout)


if __name__=="__main__": unittest.main()
