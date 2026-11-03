"""R82 native parity compares only explicit editor observations; never grants send."""
import importlib.util
import json
from pathlib import Path
import unittest
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "r82-native-draft-parity"
MODULE_PATH = DIR / "compare_draft.py"
spec = importlib.util.spec_from_file_location("r82_comparator", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class R82DraftParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = json.loads((DIR/"EXPECTED.json").read_text(encoding="utf-8"))
        cls.observed = json.loads((DIR/"OBSERVATIONS.json").read_text(encoding="utf-8"))
        cls.candidates = json.loads((ROOT/"r81-transport-truth/ISSUE-CARDS.json").read_text(encoding="utf-8"))
        cls.instructions = (DIR/"README.md").read_text(encoding="utf-8")
        cls.decision = (DIR/"RELEASE-DECISION.md").read_text(encoding="utf-8")

    def synthetic(self, issue="01"):
        c = next(p for p in self.expected["expected_posts"] if p["issue"]==issue)
        return {"site":"https://finalvestige.com","observed_drafts":[{
            "issue":issue, "status":"draft", "title":c["editor_title"],
            "custom_excerpt":c["editor_custom_excerpt"],
            "send_to_subscribers":False, "scheduled_for":None,
            "primary_cta_url":c["primary_cta_url"], "affiliate_urls":[]}]}

    def test_empty_observations_are_real_and_no_drafts_claimed(self):
        self.assertEqual(self.observed["observed_drafts"],[])
    def test_all_hold_without_observations(self):
        r=module.compare(self.expected,self.observed)
        self.assertEqual(r["observed_drafts"],0)
        self.assertTrue(all(q["status"]=="HOLD_UNSENT" for q in r["outcomes"]))
    def test_six_exact_ids(self):
        self.assertEqual([c["issue"] for c in self.expected["expected_posts"]],list(module.IDS))
    def test_exact_four_two(self):
        self.assertEqual([c["issue"] for c in self.expected["expected_posts"] if c["allocation"]=="commercial_reserved"],["03","05"])
    def test_subject_excerpt_equal_exact_r81_source(self):
        for c, p in zip(self.candidates["cards"],self.expected["expected_posts"]):
            self.assertEqual((c["subject"],c["excerpt"],c["destination"]),(p["editor_title"],p["editor_custom_excerpt"],p["primary_cta_url"]))
    def test_editorial_synthetic_structural_only(self):
        x=module.compare(self.expected,self.synthetic())
        self.assertTrue(x["outcomes"][0]["structure_matches"])
        self.assertEqual(x["status"],"HOLD_UNSENT")
    def test_commercial_perfect_simulation_still_hold(self):
        x=module.compare(self.expected,self.synthetic("03"))
        row=x["outcomes"][2]
        self.assertTrue(row["structure_matches"])
        self.assertIn("MERCHANT_EMAIL_RIGHTS_AND_GUIDE_UNVERIFIED",row["blockers"])
    def test_no_green_release_field(self):
        self.assertFalse(self.expected["release_clearance"])
        self.assertFalse(module.compare(self.expected,self.synthetic())["founder_final_send_approval"])
    def test_wrong_subject_blocked(self):
        x=self.synthetic();x["observed_drafts"][0]["title"]="Guaranteed results"
        self.assertIn("NATIVE_TITLE_NOT_EQUAL_TO_CANDIDATE",module.compare(self.expected,x)["outcomes"][0]["blockers"])
    def test_missing_excerpt_blocked(self):
        x=self.synthetic();x["observed_drafts"][0]["custom_excerpt"]=None
        self.assertIn("NATIVE_EXCERPT_NOT_EQUAL_TO_CANDIDATE",module.compare(self.expected,x)["outcomes"][0]["blockers"])
    def test_send_true_blocked(self):
        x=self.synthetic();x["observed_drafts"][0]["send_to_subscribers"]=True
        self.assertIn("POST_EMAIL_TOGGLE_NOT_PROVEN_OFF",module.compare(self.expected,x)["outcomes"][0]["blockers"])
    def test_send_unknown_blocked(self):
        x=self.synthetic();x["observed_drafts"][0]["send_to_subscribers"]=None
        self.assertIn("POST_EMAIL_TOGGLE_NOT_PROVEN_OFF",module.compare(self.expected,x)["outcomes"][0]["blockers"])
    def test_scheduled_blocked(self):
        x=self.synthetic();x["observed_drafts"][0]["scheduled_for"]="2026-11-10"
        self.assertIn("SCHEDULED_OR_SCHEDULE_UNKNOWN",module.compare(self.expected,x)["outcomes"][0]["blockers"])
    def test_unknown_schedule_blocked(self):
        x=self.synthetic();x["observed_drafts"][0]["scheduled_for"]="UNKNOWN"
        self.assertIn("SCHEDULED_OR_SCHEDULE_UNKNOWN",module.compare(self.expected,x)["outcomes"][0]["blockers"])
    def test_published_status_blocked(self):
        x=self.synthetic();x["observed_drafts"][0]["status"]="publish"
        self.assertIn("NOT_NONPUBLISHED_DRAFT",module.compare(self.expected,x)["outcomes"][0]["blockers"])
    def test_external_cta_blocked(self):
        x=self.synthetic();x["observed_drafts"][0]["primary_cta_url"]="https://zen12.com/hnp"
        self.assertIn("FIRST_PARTY_EDITORIAL_CTA_MISMATCH",module.compare(self.expected,x)["outcomes"][0]["blockers"])
    def test_merchant_primary_cta_blocked(self):
        x=self.synthetic("03");x["observed_drafts"][0]["primary_cta_url"]="https://finalvestige.com/mind/zen12-guide/"
        self.assertIn("UNPUBLISHED_COMMERCIAL_GUIDE_LINK_PRESENT",module.compare(self.expected,x)["outcomes"][2]["blockers"])
    def test_merchant_affiliate_urls_blocked(self):
        x=self.synthetic("05");x["observed_drafts"][0]["affiliate_urls"]=["https://example.net/?affiliate=SECRET"]
        self.assertIn("AFFILIATE_URLS_NOT_ALLOWED",module.compare(self.expected,x)["outcomes"][4]["blockers"])
    def test_redacts_any_unexpected_email_field(self):
        x=self.synthetic();x["observed_drafts"][0]["subscriber_email"]="secret@example.com"
        with self.assertRaisesRegex(ValueError,"observation fields invalid"):
            module.compare(self.expected,x)
    def test_rejects_unexpected_top_level_tokens(self):
        x=self.synthetic();x["private_unsubscribe_url"]="https://host/token"
        with self.assertRaises(ValueError): module.compare(self.expected,x)
    def test_duplicate_issue_rejected(self):
        x=self.synthetic();x["observed_drafts"].append(deepcopy(x["observed_drafts"][0]))
        with self.assertRaises(ValueError): module.compare(self.expected,x)
    def test_invalid_toggle_type_rejected(self):
        x=self.synthetic();x["observed_drafts"][0]["send_to_subscribers"]="false"
        with self.assertRaises(ValueError): module.compare(self.expected,x)
    def test_missing_field_rejected(self):
        x=self.synthetic();del x["observed_drafts"][0]["custom_excerpt"]
        with self.assertRaises(ValueError): module.compare(self.expected,x)
    def test_invalid_site_rejected(self):
        x=self.synthetic();x["site"]="https://fake.example"
        with self.assertRaises(ValueError): module.compare(self.expected,x)
    def test_source_mutation_fails(self):
        x=deepcopy(self.expected);x["release_clearance"]=True
        with self.assertRaises(ValueError): module.compare(x,self.observed)
    def test_merchant_mix_mutation_fails(self):
        x=deepcopy(self.expected);x["expected_posts"][2]["allocation"]="editorial"
        with self.assertRaises(ValueError): module.compare(x,self.observed)
    def test_no_private_addresses_in_package(self):
        s=self.decision+self.instructions+(DIR/"EXPECTED.json").read_text(encoding="utf-8")
        self.assertNotIn("secret@example.com",s)
        self.assertNotIn("utm_source=",s)
    def test_copy_is_visible_as_only_proposed(self):
        self.assertIn("NOT an approval",self.decision)
        self.assertIn("optional",self.instructions)
    def test_distinguishes_native_preview_from_received_mail(self):
        self.assertIn("Send test email",self.instructions)
        self.assertIn("actual Jetpack-delivered email",self.instructions)
    def test_offline_mode_and_no_exports(self):
        self.assertIn("No WordPress modification",self.instructions)
        self.assertNotIn("smtplib",MODULE_PATH.read_text(encoding="utf-8"))
    def test_policy_remains_four_two(self):
        self.assertEqual(self.expected["allocation"]["editorial"],["01","02","04","06"])
        self.assertEqual(self.expected["allocation"]["commercial_reserved"],["03","05"])
    def test_real_world_unknown_cannot_be_optimistically_zero(self):
        self.assertEqual(module.compare(self.expected,self.observed)["recipient_eligibility"],"UNKNOWN")
    def test_fails_on_bad_affiliate_field_type(self):
        x=self.synthetic();x["observed_drafts"][0]["affiliate_urls"]=None
        # Unknown link state is not accepted as an empty proved list.
        self.assertIn("AFFILIATE_URLS_NOT_ALLOWED",module.compare(self.expected,x)["outcomes"][0]["blockers"])

if __name__ == "__main__": unittest.main()
