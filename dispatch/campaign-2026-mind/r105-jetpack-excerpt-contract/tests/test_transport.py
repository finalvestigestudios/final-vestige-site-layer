"""Tests for the R105 offline transport safety contract; no sends or network."""
import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from audit_transport import inspect
BASE = json.loads(pathlib.Path(__file__).resolve().parents[1].joinpath("transport_contract.json").read_text(encoding="utf-8"))

class TransportContractTests(unittest.TestCase):
    def test_original_contract_valid_but_unsent(self):
        self.assertEqual(inspect(BASE), [])
    def test_six_issues(self):
        x = copy.deepcopy(BASE); x["issues"].pop()
        self.assertTrue(inspect(x))
    def test_original_sha_locked(self):
        x = copy.deepcopy(BASE); x["source_pr_175_exact_sha"] = "0"*40
        self.assertTrue(inspect(x))
    def test_source_manifest_blob_locked(self):
        x = copy.deepcopy(BASE); x["source_manifest_blob"] = "0"*40
        self.assertTrue(inspect(x))
    def test_no_transport_approval(self):
        x = copy.deepcopy(BASE); x["transport_choice"] = "SEND"
        self.assertTrue(inspect(x))
    def test_zero_claims_not_faked(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["eligible_recipients"] = 4
        self.assertTrue(inspect(x))
    def test_one_count_change_fails(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["newsletter_unconfirmed"] = 0
        self.assertTrue(inspect(x))
    def test_follower_not_inferred(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["jetpack_email_followers"] = 2
        self.assertTrue(inspect(x))
    def test_auto_send_cannot_activate(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["default_post_email_enabled"] = True
        self.assertTrue(inspect(x))
    def test_full_body_not_assumed(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["content_format"] = "full"
        self.assertTrue(inspect(x))
    def test_actual_received_email_not_fabricated(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["actual_received_campaign_email_verified"] = True
        self.assertTrue(inspect(x))
    def test_postal_address_not_fabricated(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["footer_address_verified"] = True
        self.assertTrue(inspect(x))
    def test_unsubscribe_not_fabricated(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["unsubscribe_operation_verified"] = True
        self.assertTrue(inspect(x))
    def test_human_approval_not_fabricated(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["final_founder_send_approval"] = True
        self.assertTrue(inspect(x))
    def test_offer_cta_cannot_activate(self):
        x = copy.deepcopy(BASE); x["issues"][2]["affiliate_url"] = "https://merchant.example/a"
        self.assertTrue(inspect(x))
    def test_guide_not_invented(self):
        x = copy.deepcopy(BASE); x["issues"][4]["warmup_guide_live"] = True
        self.assertTrue(inspect(x))
    def test_email_permission_not_invented(self):
        x = copy.deepcopy(BASE); x["issues"][2]["approved_email_permission"] = True
        self.assertTrue(inspect(x))
    def test_4_2_mix_fixed(self):
        x = copy.deepcopy(BASE); x["issues"][2]["kind"] = "editorial"
        self.assertTrue(inspect(x))
    def test_subject_exact(self):
        x = copy.deepcopy(BASE); x["issues"][0]["subject"] = "Guaranteed results today"
        self.assertTrue(inspect(x))
    def test_preheader_exact(self):
        x = copy.deepcopy(BASE); x["issues"][1]["preheader"] = "Different"
        self.assertTrue(inspect(x))
    def test_missing_cta_in_default_snippet_kept_visible(self):
        x = copy.deepcopy(BASE); x["issues"][0]["natural_first55_loses_primary_cta"] = False
        self.assertTrue(inspect(x))
    def test_missing_disclosure_in_default_snippet_visible(self):
        x = copy.deepcopy(BASE); x["issues"][2]["natural_first55_loses_commercial_disclosure"] = False
        self.assertTrue(inspect(x))
    def test_no_affiliate_urls_in_excerpt(self):
        x = copy.deepcopy(BASE); x["issues"][2]["proposed_custom_excerpt"] += " https://seller.example/"
        self.assertTrue(inspect(x))
    def test_no_html_in_excerpt(self):
        x = copy.deepcopy(BASE); x["issues"][1]["proposed_custom_excerpt"] += " <a>foo</a>"
        self.assertTrue(inspect(x))
    def test_no_claim_of_proven_effect(self):
        x = copy.deepcopy(BASE); x["issues"][4]["proposed_custom_excerpt"] += " clinically proven"
        self.assertTrue(inspect(x))
    def test_no_pii(self):
        x = copy.deepcopy(BASE); x["issues"][1]["proposed_custom_excerpt"] += " subscriber@example.com"
        self.assertTrue(inspect(x))
    def test_count_types_not_coerced(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["newsletter_confirmed"] = True
        self.assertTrue(inspect(x))
    def test_privacy_permission_not_invented(self):
        x = copy.deepcopy(BASE); x["privacy_aggregate_only_reporting"] = "APPROVED"
        self.assertTrue(inspect(x))
    def test_unapproved_email_edition_not_released(self):
        x = copy.deepcopy(BASE); x["issues"][0]["status"] = "READY"
        self.assertTrue(inspect(x))
    def test_welcome_receipt_not_assumed(self):
        x = copy.deepcopy(BASE); x["transport_evidence"]["welcome_actual_receipt_verified"] = True
        self.assertTrue(inspect(x))

if __name__ == "__main__":
    unittest.main()
