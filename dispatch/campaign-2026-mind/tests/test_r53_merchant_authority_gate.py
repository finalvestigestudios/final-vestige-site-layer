"""Adversarial checks for R53 only: a successful test NEVER authorizes emailing."""
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SRC = BASE / "r53-release-evidence"
spec = importlib.util.spec_from_file_location("r53_authority_gate", SRC / "merchant_authority_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def default_doc():
    return json.loads((SRC / "merchant_authority.json").read_text(encoding="utf-8"))

def sample_proof(product="zen12"):
    # Synthetic example only. Neither an actual document nor merchant permission.
    return {
        "product_key": product, "publisher": "Final Vestige Studios",
        "source_type": "direct_partner_written_confirmation",
        "evidence_ref": "FV-PRIVATE-A1B2C3D4",
        "scope_channels": ["website", "email"],
        "scope_products": [product],
        "partner_status": "approved",
        "affiliate_link_verified_privately": True,
        "creative_rights_checked": True,
        "offer_terms_checked": True,
        "valid_through": "2026-12-31",
        "human_reviewer_ref": "FV-PRIVATE-1234ABCD",
        "human_reviewed_date": "2026-11-01"
    }

class R53AuthorityTests(unittest.TestCase):
    def test_01_default_holds_sending(self):
        self.assertEqual(gate.audit_manifest(default_doc())["send_status"], "HOLD_UNSENT")

    def test_02_default_merchants_both_hold(self):
        self.assertTrue(all(v["merchant_status"]=="HOLD_MERCHANT" for v in gate.audit_manifest(default_doc())["merchant"].values()))

    def test_03_site_same_jetpack_one_list(self):
        doc=default_doc()
        self.assertEqual(doc["site"]["id"],256784396)
        self.assertTrue(doc["site"]["newsletter_enabled"])

    def test_04_new_post_default_is_off_but_manual_possible(self):
        site=default_doc()["site"]
        self.assertIs(site["new_post_email_default"],False)
        self.assertIs(site["individual_post_send_toggle_possible"],True)

    def test_05_welcome_configured_not_received(self):
        site=default_doc()["site"]
        self.assertIs(site["welcome_configured"],True)
        self.assertEqual(site["welcome_received"],"NOT_VERIFIED")

    def test_06_unreconciled_counts_not_sum(self):
        site=default_doc()["site"]
        self.assertEqual(site["subscriber_counters"],{"total":2,"confirmed":2,"unconfirmed":2})
        self.assertIsNone(gate.audit_manifest(default_doc())["confirmed_eligible_recipients"])

    def test_07_all_issues_hold_four_two(self):
        doc=default_doc()
        self.assertEqual(doc["canonical"]["editorial_issues"],[1,2,4,6])
        self.assertEqual(doc["canonical"]["commercial_issues"],[3,5])

    def test_08_no_wrong_offer_swapping(self):
        doc=default_doc();doc["offers"]["zen12"]["issue"]=5
        with self.assertRaises(ValueError):gate.audit_manifest(doc)

    def test_09_no_authorized_send_field(self):
        self.assertNotIn("APPROVED_TO_SEND",json.dumps(default_doc()))

    def test_10_normalized_official_sources(self):
        doc=default_doc()
        self.assertIn("https://zen12.com/hnp",doc["official_sources"])
        self.assertIn("https://hypnosislive.com/mental-skills/total-focus",doc["official_sources"])

    def test_11_only_opaque_proof_refs_not_earning_urls(self):
        raw=(SRC/"merchant_authority.json").read_text()
        self.assertNotIn("hop.clickbank.net",raw)
        self.assertNotIn("affiliate_id=",raw)
        self.assertIn('"proof": null',raw)

    def test_12_public_limitless_labs_is_not_approval(self):
        result=gate.evaluate_proof("zen12",dict(sample_proof(),source_type="public_promo_swipe"))
        self.assertIn("NOT_A_PARTNER_AUTHORITY_SOURCE",result["issues"])

    def test_13_consumer_purchase_email_is_not_approval(self):
        result=gate.evaluate_proof("total_focus",dict(sample_proof("total_focus"),source_type="customer_order_confirmation"))
        self.assertIn("NOT_A_PARTNER_AUTHORITY_SOURCE",result["issues"])

    def test_14_brand_email_is_not_channel_right(self):
        p=sample_proof();p["scope_channels"]=["website"]
        self.assertIn("EMAIL_CHANNEL_NOT_SPECIFICALLY_PERMITTED",gate.evaluate_proof("zen12",p)["issues"])

    def test_15_social_permission_is_not_email_permission(self):
        p=sample_proof();p["scope_channels"]=["social"]
        self.assertIn("EMAIL_CHANNEL_NOT_SPECIFICALLY_PERMITTED",gate.evaluate_proof("zen12",p)["issues"])

    def test_16_wrong_product_does_not_confer_approval(self):
        p=sample_proof();p["scope_products"]=["total_focus"]
        self.assertIn("PRODUCT_NOT_SPECIFICALLY_PERMITTED",gate.evaluate_proof("zen12",p)["issues"])

    def test_17_wrong_product_key_is_rejected(self):
        p=sample_proof("total_focus")
        self.assertIn("WRONG_PRODUCT",gate.evaluate_proof("zen12",p)["issues"])

    def test_18_wrong_publisher_is_rejected(self):
        p=sample_proof();p["publisher"]="Other Company"
        self.assertIn("WRONG_PUBLISHER",gate.evaluate_proof("zen12",p)["issues"])

    def test_19_missing_partner_status_rejected(self):
        p=sample_proof();p["partner_status"]="pending"
        self.assertIn("PARTNER_APPROVAL_NOT_ESTABLISHED",gate.evaluate_proof("zen12",p)["issues"])

    def test_20_evidence_ref_must_not_be_a_token_url(self):
        p=sample_proof();p["evidence_ref"]="https://partner.example/?token=SECRET"
        self.assertIn("MISSING_PRIVATE_EVIDENCE_REFERENCE",gate.evaluate_proof("zen12",p)["issues"])

    def test_21_human_reviewer_ref_required(self):
        p=sample_proof();p["human_reviewer_ref"]=None
        self.assertIn("HUMAN_REVIEW_REFERENCE_REQUIRED",gate.evaluate_proof("zen12",p)["issues"])

    def test_22_link_validation_cannot_be_skipped(self):
        p=sample_proof();p["affiliate_link_verified_privately"]=False
        self.assertIn("NOT_CHECKED:affiliate_link_verified_privately",gate.evaluate_proof("zen12",p)["issues"])

    def test_23_creative_rights_cannot_be_skipped(self):
        p=sample_proof();p["creative_rights_checked"]=False
        self.assertIn("NOT_CHECKED:creative_rights_checked",gate.evaluate_proof("zen12",p)["issues"])

    def test_24_terms_cannot_be_skipped(self):
        p=sample_proof();p["offer_terms_checked"]=False
        self.assertIn("NOT_CHECKED:offer_terms_checked",gate.evaluate_proof("zen12",p)["issues"])

    def test_25_expired_permission_rejected(self):
        p=sample_proof();p["valid_through"]="2026-10-31"
        self.assertIn("PERMISSION_EXPIRED",gate.evaluate_proof("zen12",p)["issues"])

    def test_26_future_human_review_rejected(self):
        p=sample_proof();p["human_reviewed_date"]="2026-12-01"
        self.assertIn("REVIEW_IN_FUTURE",gate.evaluate_proof("zen12",p)["issues"])

    def test_27_bad_date_rejected(self):
        p=sample_proof();p["valid_through"]="NOV/2026"
        self.assertIn("DATE_PROOF_INVALID",gate.evaluate_proof("zen12",p)["issues"])

    def test_28_unexpected_email_or_token_fields_rejected(self):
        p=sample_proof();p["subscriber_email"]="do-not-store"
        self.assertIn("UNEXPECTED_FIELDS",gate.evaluate_proof("zen12",p)["issues"])

    def test_29_all_values_well_shaped_still_manual_only(self):
        r=gate.evaluate_proof("zen12",sample_proof())
        self.assertEqual(r["merchant_status"],"MANUAL_AUTHORITY_REVIEW_REQUIRED")
        self.assertEqual(r["send_status"],"HOLD_UNSENT")

    def test_30_other_product_well_shaped_still_manual_only(self):
        r=gate.evaluate_proof("total_focus",sample_proof("total_focus"))
        self.assertEqual(r["merchant_status"],"MANUAL_AUTHORITY_REVIEW_REQUIRED")
        self.assertEqual(r["send_status"],"HOLD_UNSENT")

    def test_31_merchant_proof_injected_does_not_send(self):
        doc=default_doc()
        doc["offers"]["zen12"]["proof"]=sample_proof()
        doc["offers"]["zen12"]["partner_acceptance"]="VERIFIED_BY_HUMAN_REVIEWER"
        out=gate.audit_manifest(doc)
        self.assertEqual(out["send_status"],"HOLD_UNSENT")
        self.assertEqual(out["merchant"]["total_focus"]["merchant_status"],"HOLD_MERCHANT")

    def test_32_wrong_four_two_ratio_rejected(self):
        doc=default_doc();doc["canonical"]["editorial_issues"].append(3)
        with self.assertRaises(ValueError):gate.audit_manifest(doc)

    def test_33_send_status_mutation_rejected(self):
        doc=default_doc();doc["disposition"]="READY"
        with self.assertRaises(ValueError):gate.audit_manifest(doc)

    def test_34_unique_audience_mutation_rejected(self):
        doc=default_doc();doc["site"]["unique_consent_eligible"]=2
        with self.assertRaises(ValueError):gate.audit_manifest(doc)

    def test_35_never_emits_private_pii(self):
        output=json.dumps(gate.audit_manifest(default_doc()))
        self.assertNotIn("email_address",output)
        self.assertNotIn("affiliate_url",output)
        self.assertNotIn("subscriber_id",output)

    def test_36_missing_proof_property_rejected(self):
        p=sample_proof();del p["scope_products"]
        self.assertIn("MISSING_FIELDS:scope_products",gate.evaluate_proof("zen12",p)["issues"])

    def test_37_unknown_channel_rejected(self):
        p=sample_proof();p["scope_channels"]=["email","telepathy"]
        self.assertIn("EMAIL_CHANNEL_NOT_SPECIFICALLY_PERMITTED",gate.evaluate_proof("zen12",p)["issues"])

    def test_38_unknown_product_rejected(self):
        self.assertIn("UNKNOWN_PRODUCT",gate.evaluate_proof("limitless_labs",sample_proof())["issues"])

    def test_39_production_writes_remain_false(self):
        canon=default_doc()["canonical"]
        self.assertIs(canon["emails_sent_this_sprint"],False)
        self.assertIs(canon["emails_test_sent_this_sprint"],False)
        self.assertIs(canon["wordpress_modified_this_sprint"],False)

    def test_40_cli_source_exits_zero_but_holds(self):
        p=subprocess.run([sys.executable,str(SRC/"merchant_authority_gate.py"),str(SRC/"merchant_authority.json")],
                         capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(p.stdout)["send_status"],"HOLD_UNSENT")

    def test_41_cli_rejects_corrupt_file(self):
        p=subprocess.run([sys.executable,str(SRC/"merchant_authority_gate.py"),str(SRC/"does-not-exist.json")],
                         capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertEqual(json.loads(p.stdout)["send_status"],"HOLD_UNSENT")

    def test_42_canonical_manifest_held(self):
        manifest=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["mix"],{"editorial":4,"commercial_review_pending":2})
        self.assertTrue(all(x["publish_state"]=="hold" for x in manifest["issues"]))

if __name__=="__main__":
    unittest.main()
