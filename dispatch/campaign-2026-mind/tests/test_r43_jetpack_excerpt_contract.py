"""R43 official provider excerpt-model reconciliation and adversarial source safety."""
import importlib.util
import json
import pathlib
import shutil
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "r43-jetpack-excerpt-contract" / "excerpt_contract.py"
SPEC = importlib.util.spec_from_file_location("r43_contract", MOD_PATH)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class ExcerptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.audit()
        cls.rows = cls.report["editions"]

    def test_01_six(self): self.assertEqual(len(self.rows), 6)
    def test_02_exact_numbers(self): self.assertEqual([r["number"] for r in self.rows], list(range(1, 7)))
    def test_03_four_editorial(self): self.assertEqual(sum(r["kind"] == "editorial" for r in self.rows), 4)
    def test_04_two_commercial(self): self.assertEqual(sum(r["kind"] == "commercial-review-pending" for r in self.rows), 2)
    def test_05_all_hold(self): self.assertTrue(all("HOLD" in r["release"] for r in self.rows))
    def test_06_two_merchant_holds(self): self.assertEqual([r["number"] for r in self.rows if r["release"] == "HOLD_MERCHANT_AND_UNSENT"], [3, 5])
    def test_07_no_sending(self): self.assertFalse(self.report["emails_sent_or_test_sent"])
    def test_08_no_posts(self): self.assertFalse(self.report["wordPress_posts_created"])
    def test_09_no_private_subscribers(self): self.assertFalse(self.report["raw_subscriber_data_accessed"])
    def test_10_no_eligibility_claim(self): self.assertIsNone(self.report["actual_eligible_recipient_count"])
    def test_11_no_email_claim(self): self.assertTrue(all(not r["actual_received_jetpack_email_verified"] for r in self.rows))
    def test_12_no_installed_excerpt(self): self.assertTrue(all(not r["optional_custom_excerpt_installed"] for r in self.rows))
    def test_13_no_native_preheader(self): self.assertTrue(all(not r["planned_preheader_native_verified"] for r in self.rows))
    def test_14_no_legal_claim(self): self.assertTrue(all(not r["legal_footer_and_optout_verified"] for r in self.rows))
    def test_15_no_final_approval(self): self.assertTrue(all(not r["founder_approved_to_send"] for r in self.rows))
    def test_16_model_length_chars(self): self.assertTrue(all(len(r["models"]["jetpack_documented_350_character_model"]) <= 350 for r in self.rows))
    def test_17_model_length_words(self): self.assertTrue(all(len(r["models"]["generic_wordpress_55_word_model"].split()) <= 55 for r in self.rows))
    def test_18_different_provider_models(self): self.assertTrue(any(r["models"]["jetpack_documented_350_character_model"] != r["models"]["generic_wordpress_55_word_model"] for r in self.rows))
    def test_19_official_jetpack_source(self): self.assertIn("jetpack.com/support/newsletter", self.report["sources"]["jetpack_specific"])
    def test_20_distinct_generic_source(self): self.assertIn("wordpress.com/support/excerpts", self.report["sources"]["wordpress_generic"])
    def test_21_raw_warning_detected(self): self.assertTrue(all(r["models"]["raw_copy_exposes_draft_banner"] for r in self.rows))
    def test_22_clean_story_no_warning(self): self.assertTrue(all(r["models"]["clean_story_has_no_draft_banner"] for r in self.rows))
    def test_23_comm_custom_disclosure_350(self): self.assertTrue(all(self.rows[n-1]["models"]["custom_excerpt_first_350_has_disclosure"] for n in (3, 5)))
    def test_24_editorial_no_merchant_url(self): self.assertTrue(all(not r["canonical_merchant_citation_urls"] for r in self.rows if r["kind"] == "editorial"))
    def test_25_issue_three_seller_routes_known(self): self.assertGreaterEqual(len(self.rows[2]["canonical_merchant_citation_urls"]), 2)
    def test_26_output_has_no_private_email(self): self.assertNotIn("@gmail.com", json.dumps(self.report))
    def test_27_no_earning_links(self): self.assertFalse(any("clickbank" in x.lower() for r in self.rows for x in r["canonical_merchant_citation_urls"]))
    def test_28_legacy_model_explicitly_not_inbox(self): self.assertIn("Neither model is a received email", self.report["interpretation"])
    def test_29_models_distinguish_direct_raw_copy(self): self.assertNotEqual(self.rows[0]["models"]["raw_markdown_mistake_350_character_model"], self.rows[0]["models"]["jetpack_documented_350_character_model"])
    def test_30_350_chars_not_350_words(self): self.assertLessEqual(len(self.rows[0]["models"]["jetpack_documented_350_character_model"]), 350)
    def test_31_missing_headers_fail(self):
        with self.assertRaises(ValueError): M.story_section("Story without a STOP header")
    def test_32_empty_custom_excerpt_fail(self):
        with self.assertRaises(ValueError): M.diagnostic_models("Story", "header", " ")
    def test_33_early_custom_disclosure_detection(self):
        v = M.diagnostic_models("story", "DO NOT PUBLISH OR EMAIL", "Here is the guide. Affiliate links may earn a commission.")
        self.assertTrue(v["custom_excerpt_first_350_has_disclosure"])
    def test_34_late_custom_disclosure_detection(self):
        v = M.diagnostic_models("story", "DO NOT PUBLISH OR EMAIL", "x"*365 + " commission")
        self.assertFalse(v["custom_excerpt_first_350_has_disclosure"])
    def test_35_fake_seller_host_does_not_count(self):
        self.assertEqual(M.merchant_links("https://zen12.com.evil.example/p"), [])
    def test_36_true_seller_host_counts(self):
        self.assertEqual(M.merchant_links("https://zen12.com/hnp"), ["https://zen12.com/hnp"])
    def test_37_markdown_link_label_survives(self):
        self.assertIn("the research", M.plain_preview("[the research](https://example.org/)"))
    def test_38_html_fabrication_not_in_report(self):
        self.assertNotIn("<img", json.dumps(self.report))
    def test_39_readonly_status(self): self.assertTrue(self.report["read_only"])
    def test_40_excerpt_configuration_is_not_permission(self): self.assertEqual(self.report["email_content_format_observed"], "excerpt")

    def corrupt(self, mutate):
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td)
            (p / "issues").mkdir(); (p / "delivery").mkdir()
            shutil.copy2(ROOT / "manifest.json", p / "manifest.json")
            shutil.copy2(ROOT / "delivery" / "wordpress_excerpt_copy.json", p / "delivery" / "wordpress_excerpt_copy.json")
            for name in M.MANUSCRIPTS.values():
                shutil.copy2(ROOT / "issues" / name, p / "issues" / name)
            mutate(p)
            with self.assertRaises(ValueError): M.audit(p)

    def test_41_mutated_release_is_rejected(self):
        def edit(p):
            q=p/"manifest.json";a=json.loads(q.read_text());a["issues"][0]["publish_state"]="publish";q.write_text(json.dumps(a))
        self.corrupt(edit)
    def test_42_mutated_kind_is_rejected(self):
        def edit(p):
            q=p/"manifest.json";a=json.loads(q.read_text());a["issues"][1]["kind"]="commercial-review-pending";q.write_text(json.dumps(a))
        self.corrupt(edit)
    def test_43_mutated_earning_link_is_rejected(self):
        def edit(p):
            q=p/"manifest.json";a=json.loads(q.read_text());a["issues"][2]["merchant_affiliate_url"]="https://invalid";q.write_text(json.dumps(a))
        self.corrupt(edit)
    def test_44_removed_postal_marker_is_rejected(self):
        def edit(p):
            q=p/"issues"/M.MANUSCRIPTS[1];q.write_text(q.read_text().replace(M.LEGAL_MARKERS[0],""))
        self.corrupt(edit)
    def test_45_disclosure_after_350_is_rejected(self):
        def edit(p):
            q=p/"delivery"/"wordpress_excerpt_copy.json";a=json.loads(q.read_text());a["entries"][2]["excerpt"]="a"*380+" commission";q.write_text(json.dumps(a))
        self.corrupt(edit)
    def test_46_drifted_subject_is_rejected(self):
        def edit(p):
            q=p/"manifest.json";a=json.loads(q.read_text());a["issues"][2]["subject"]="BUY NOW";q.write_text(json.dumps(a))
        self.corrupt(edit)
    def test_47_deleting_stop_marker_is_rejected(self):
        def edit(p):
            q=p/"issues"/M.MANUSCRIPTS[2];q.write_text(q.read_text().replace("DO NOT PUBLISH OR EMAIL",""))
        self.corrupt(edit)
    def test_48_editorial_seller_link_is_rejected(self):
        def edit(p):
            q=p/"issues"/M.MANUSCRIPTS[1];q.write_text(q.read_text().replace("\n---\n","\n---\nhttps://zen12.com/hnp\n",1))
        self.corrupt(edit)


if __name__ == "__main__":
    unittest.main()
