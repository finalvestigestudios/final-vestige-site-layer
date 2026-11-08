"""R94: exact original manuscript and R92 excerpt field handoff safety tests."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "r94-native-editor-handoff" / "editor_map.py"
SPEC = importlib.util.spec_from_file_location("fv_dispatch_r94", FILE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class NativeFieldMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.master = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.candidates = json.loads((ROOT / "r92-excerpt-mode-truth" / "candidate_excerpts.json").read_text(encoding="utf-8"))

    def build(self):
        return MOD.build(copy.deepcopy(self.master), copy.deepcopy(self.candidates))

    def test_passes_true_immutable_source_and_six_fields(self):
        out = self.build()
        self.assertEqual([p["edition"] for p in out["entries"]], [1,2,3,4,5,6])
        self.assertEqual(out["merchant_issue_numbers"], [3, 5])
        self.assertEqual([x["purpose"].startswith("editorial") for x in out["entries"]].count(True), 4)

    def test_every_preview_remains_unsent_and_not_api_ready(self):
        o = self.build()
        self.assertTrue(o["these_are_editor_notes_not_valid_wp_api_payloads"])
        self.assertFalse(o["founder_final_campaign_approval"])
        for issue in o["entries"]:
            self.assertEqual(issue["release_decision"], "HOLD_UNSENT")
            self.assertTrue(issue["must_leave_send_to_subscribers_off"])
            self.assertFalse(issue["is_wordpress_api_payload"])
            self.assertFalse(issue["is_authorized_to_send_test_or_real_email"])
            self.assertFalse(issue["is_authorized_to_create_wordpress_draft"])
            self.assertIsNone(issue["publisher_post_permalink"])
            self.assertIsNone(issue["custom_inbox_preheader"])
            self.assertIsNone(issue["affiliate_tracking_url"])

    def test_post_title_subject_and_native_read_more_are_not_confused(self):
        o = self.build()
        self.assertTrue(o["inbox_subject_is_based_on_post_title"])
        self.assertTrue(o["campaign_preheaders_are_editing_candidates_not_confirmed_inbox_fields"])
        for issue in o["entries"]:
            self.assertEqual(issue["native_inbox_read_more_target"], "future WordPress post permalink; NOT the source URL")
            self.assertIsNone(issue["publisher_post_permalink"])
            self.assertIsNotNone(issue["canonical_original_subject"])

    def test_only_editorial_issues_may_have_current_firstparty_research(self):
        for issue in self.build()["entries"]:
            if issue["edition"] in (3, 5):
                self.assertIsNone(issue["source_article_for_post_body_only"])
            else:
                self.assertTrue(MOD.verified_first_party(issue["source_article_for_post_body_only"]))

    def test_master_sha_drift_fails(self):
        d = copy.deepcopy(self.candidates)
        d["master_sha"] = "0"*40
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_unknown_list_is_not_fake_zero(self):
        d = copy.deepcopy(self.candidates)
        d["settings_snapshot"]["eligible_email_recipients"] = 0
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_new_post_default_flip_fails(self):
        d = copy.deepcopy(self.candidates)
        d["settings_snapshot"]["email_new_posts_by_default"] = True
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_release_state_flip_fails(self):
        d = copy.deepcopy(self.candidates)
        d["campaign_state"] = "READY"
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_full_mode_change_fails(self):
        d = copy.deepcopy(self.candidates)
        d["settings_snapshot"]["email_content_format"] = "full"
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_preheader_support_cannot_be_fabricated(self):
        d = copy.deepcopy(self.candidates)
        d["native_wordpress_expectation"]["custom_preheader_control_verified"] = True
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_received_mime_cannot_be_fabricated(self):
        d = copy.deepcopy(self.candidates)
        d["native_wordpress_expectation"]["actual_mime_verified"] = True
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_merchant_activation_fails(self):
        for n in [2, 4]:
            d = copy.deepcopy(self.candidates)
            d["issues"][n]["active_affiliate_url"] = "https://merchant.example/earn"
            with self.subTest(edition=n+1), self.assertRaises(MOD.ContractError):
                MOD.build(self.master, d)

    def test_guide_url_before_approval_fails(self):
        for n in [2, 4]:
            d = copy.deepcopy(self.candidates)
            d["issues"][n]["approved_guide_url"] = "https://finalvestige.com/not-live/"
            with self.subTest(edition=n+1), self.assertRaises(MOD.ContractError):
                MOD.build(self.master, d)

    def test_disclosure_must_lead_commercial_excerpt(self):
        for n in [2, 4]:
            d = copy.deepcopy(self.candidates)
            d["issues"][n]["excerpt_text"] = "Try a product. " + d["issues"][n]["excerpt_text"]
            with self.subTest(edition=n+1), self.assertRaises(MOD.ContractError):
                MOD.build(self.master, d)

    def test_commercial_disclosure_cannot_be_removed(self):
        d = copy.deepcopy(self.candidates)
        d["issues"][2]["commercial_note"] = None
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_no_unauthorized_guide_in_commercial_post(self):
        d = copy.deepcopy(self.candidates)
        d["issues"][4]["editorial_source_url"] = "https://finalvestige.com/placeholder/"
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_post_title_malformed_fails(self):
        d = copy.deepcopy(self.candidates)
        d["issues"][0]["subject_candidate"] = "Not approved\nHidden"
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_no_placeholder_token_leaks_to_excerpt(self):
        d = copy.deepcopy(self.candidates)
        d["issues"][0]["excerpt_text"] += "[[VALID_POSTAL_ADDRESS_REQUIRED]]"
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_no_merchant_link_in_excerpt(self):
        d = copy.deepcopy(self.candidates)
        d["issues"][0]["excerpt_text"] += " https://zen12.com/hnp"
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_editorial_cta_must_be_real_firstparty_https(self):
        bad = ["http://finalvestige.com/a", "https://finalvestige.com.evil.org/a",
               "https://user@finalvestige.com/a", "https://finalvestige.com/a?utm_source=dispatch",
               "https://finalvestige.com:444/a", "https://evil.org/"]
        for val in bad:
            with self.subTest(url=val):
                d = copy.deepcopy(self.candidates)
                d["issues"][0]["editorial_source_url"] = val
                with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_duplicate_or_wrong_issue_order_fails(self):
        d = copy.deepcopy(self.candidates)
        d["issues"][3]["number"] = 3
        with self.assertRaises(MOD.ContractError): MOD.build(self.master, d)

    def test_master_kind_changes_fail(self):
        m = copy.deepcopy(self.master)
        m["issues"][2]["kind"] = "editorial"
        with self.assertRaises(MOD.ContractError): MOD.build(m, self.candidates)

    def test_original_manuscript_path_must_exist(self):
        for n, p in MOD.SOURCE_FILES.items():
            self.assertTrue((ROOT / p).is_file(), (n,p))

    def test_no_email_client_side_effect_imports(self):
        source = FILE.read_text(encoding="utf-8")
        for risky in ("import requests", "import smtplib", "import urllib.request", "api.wordpress.com", "send_message(", "post("):
            self.assertNotIn(risky, source)

if __name__ == "__main__":
    unittest.main()
