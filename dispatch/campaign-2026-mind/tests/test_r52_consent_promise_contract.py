"""R52: real signup promise asymmetry and hard email-release holds (NO SEND)."""
import copy
import importlib.util
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "r52-consent-promise-contract"
SNAP = json.loads((PACK / "observations.json").read_text(encoding="utf-8"))
MAN = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
COPY = (PACK / "copy_options.md").read_text(encoding="utf-8")
README = (PACK / "README.md").read_text(encoding="utf-8")
HTML = (PACK / "review.html").read_text(encoding="utf-8")
SPEC = importlib.util.spec_from_file_location("r52_audit", PACK / "audit_consent_contract.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HTMLInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag.lower())
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href")


class R52PromiseContract(unittest.TestCase):
    def result(self, s=None, m=None):
        return MODULE.audit(copy.deepcopy(SNAP if s is None else s), copy.deepcopy(MAN if m is None else m))

    def test_01_actual_site_identity(self):
        self.assertEqual(SNAP["site_id"], 256784396)

    def test_02_snapshot_is_explicitly_read_only(self):
        self.assertIn("READ_ONLY", SNAP["type"])
        self.assertFalse(SNAP["sensitive_data_present"])

    def test_03_dispatch_real_page_id_and_published(self):
        self.assertEqual(SNAP["pages"]["dispatch"]["id"], 523)
        self.assertTrue(SNAP["pages"]["dispatch"]["published"])

    def test_04_focus_real_page_id_and_published(self):
        self.assertEqual(SNAP["pages"]["focus"]["id"], 1579)
        self.assertTrue(SNAP["pages"]["focus"]["published"])

    def test_05_standards_published_and_present(self):
        self.assertEqual(SNAP["pages"]["editorial_standards"]["id"], 17)
        self.assertTrue(SNAP["pages"]["editorial_standards"]["published"])

    def test_06_focus_already_contains_commission_notice(self):
        f = SNAP["pages"]["focus"]
        self.assertTrue(f["commission_notice_present"])
        self.assertIn("recommendations that earn us a commission", f["near_form_promise"])

    def test_07_dispatch_lacks_matching_notice(self):
        d = SNAP["pages"]["dispatch"]
        self.assertFalse(d["commission_notice_present"])
        self.assertIn("investigations and archive finds", d["near_form_promise"])

    def test_08_no_incorrect_claim_that_both_optins_lack_disclosure(self):
        self.assertNotEqual(SNAP["pages"]["dispatch"]["commission_notice_present"],
                            SNAP["pages"]["focus"]["commission_notice_present"])
        self.assertIn("same-list-opt-in-promise-asymmetry", self.result()["findings"])

    def test_09_welcome_current_promise_no_commission(self):
        self.assertFalse(SNAP["welcome"]["commission_notice_present"])
        self.assertIn("No daily flood", SNAP["welcome"]["closing"])

    def test_10_welcome_copy_configured_not_received(self):
        w = SNAP["welcome"]
        self.assertTrue(w["configured"])
        self.assertTrue(w["fieldbook_52_page_url_in_copy"])
        self.assertFalse(w["actual_receipt_verified"])

    def test_11_jetpack_not_new_provider(self):
        self.assertEqual(SNAP["newsletter"]["sender"], "Final Vestige")
        self.assertTrue(SNAP["newsletter"]["subscriptions"])

    def test_12_auto_send_off(self):
        self.assertIs(SNAP["newsletter"]["auto_new_post_emails"], False)

    def test_13_manual_send_caveat_present(self):
        self.assertIs(SNAP["newsletter"]["manual_per_post_email_possible"], True)
        self.assertIn("auto-email-default-off-does-not-preclude-manual-per-post-send",
                      self.result()["findings"])

    def test_14_excerpt_deliverability_uncertain(self):
        self.assertEqual(SNAP["newsletter"]["content_format"], "excerpt")
        self.assertIn("actual-excerpt-email-render-unverified", self.result()["hard_stops"])

    def test_15_counts_not_summed(self):
        self.assertEqual(SNAP["newsletter"]["counts"]["total"], 2)
        self.assertEqual(SNAP["newsletter"]["counts"]["confirmed"], 2)
        self.assertEqual(SNAP["newsletter"]["counts"]["unconfirmed"], 2)
        self.assertIn("nonadditive-counts-2-2-2-no-unique-audience-inference", self.result()["findings"])

    def test_16_no_unique_consent_claim(self):
        self.assertEqual(SNAP["newsletter"]["unique_consent_eligible"], "UNKNOWN")
        self.assertIn("unique-subscriber-eligibility-unverified", self.result()["hard_stops"])

    def test_17_recent_sends_no_lifetime_claim(self):
        self.assertEqual(SNAP["newsletter"]["recent_sends"], [])
        self.assertTrue(SNAP["newsletter"]["recent_sends_only_not_lifetime"])

    def test_18_physical_address_unverified(self):
        self.assertFalse(SNAP["newsletter"]["valid_publisher_postal_address_verified"])

    def test_19_unsubscribe_unverified_in_real_email(self):
        self.assertFalse(SNAP["newsletter"]["received_email_unsubscribe_verified"])

    def test_20_can_send_not_approval(self):
        self.assertTrue(SNAP["newsletter"]["can_send"])
        self.assertIn("provider-sendable-is-not-editorial-or-legal-authorization", self.result()["findings"])

    def test_21_original_four_two_mix(self):
        self.assertEqual([x["kind"] for x in MAN["issues"]], MODULE.EXPECTED_KIND)
        self.assertEqual(MAN["mix"], {"editorial": 4, "commercial_review_pending": 2})

    def test_22_six_original_manuscripts_untouched_manifest(self):
        self.assertEqual(len(MAN["issues"]), 6)
        self.assertTrue(all(i["publish_state"] == "hold" for i in MAN["issues"]))

    def test_23_all_merchant_urls_absent(self):
        self.assertTrue(all(i["merchant_affiliate_url"] is None for i in MAN["issues"]))

    def test_24_commercial_guide_ctas_still_disabled(self):
        self.assertIn("APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED", MAN["issues"][2]["editorial_cta"])
        self.assertIn("APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED", MAN["issues"][4]["editorial_cta"])

    def test_25_source_has_no_release_authority(self):
        r = self.result()
        self.assertFalse(r["ready_for_send"])
        self.assertEqual(r["release_decision"], "HOLD_UNSENT")
        self.assertEqual(r["commercial_03_05"], "HOLD_MERCHANT")

    def test_26_all_eight_proofs_explicitly_false(self):
        self.assertEqual(set(SNAP["proof_flags"]), set(MODULE.MANDATORY_PROOFS))
        self.assertTrue(all(v is False for v in SNAP["proof_flags"].values()))

    def test_27_mutation_approval_flags_cannot_auto_green(self):
        s = copy.deepcopy(SNAP)
        for k in s["proof_flags"]: s["proof_flags"][k] = True
        self.assertFalse(self.result(s=s)["ready_for_send"])
        self.assertIn("static-snapshot-never-authorizes-sending", self.result(s=s)["hard_stops"])

    def test_28_mutation_false_focus_disclosure_is_flagged(self):
        s = copy.deepcopy(SNAP)
        s["pages"]["focus"]["commission_notice_present"] = False
        self.assertIn("focus-commission-promise-missing-or-drifted", self.result(s=s)["hard_stops"])

    def test_29_mutation_focus_copy_loss_is_flagged(self):
        s = copy.deepcopy(SNAP)
        s["pages"]["focus"]["near_form_promise"] = "Subscribe now"
        self.assertIn("focus-commission-promise-missing-or-drifted", self.result(s=s)["hard_stops"])

    def test_30_mutation_commercial_send_unhold_detected(self):
        m = copy.deepcopy(MAN)
        m["issues"][2]["publish_state"] = "publish"
        self.assertIn("canonical-manifest-release-or-merchant-link-drift", self.result(m=m)["hard_stops"])

    def test_31_mutation_merchant_link_detected(self):
        m = copy.deepcopy(MAN)
        m["issues"][4]["merchant_affiliate_url"] = "https://example.invalid/x"
        self.assertIn("canonical-manifest-release-or-merchant-link-drift", self.result(m=m)["hard_stops"])

    def test_32_mutation_4to2_split_detected(self):
        m = copy.deepcopy(MAN)
        m["issues"][4]["kind"] = "editorial"
        self.assertIn("canonical-four-editorial-two-commercial-structure-drift", self.result(m=m)["hard_stops"])

    def test_33_mutation_proof_schema_detected(self):
        s = copy.deepcopy(SNAP)
        del s["proof_flags"]["native_mime"]
        self.assertIn("proof-schema-missing-or-extra", self.result(s=s)["hard_stops"])

    def test_34_mutation_sensitive_data_state_detected(self):
        s = copy.deepcopy(SNAP)
        s["sensitive_data_present"] = True
        self.assertIn("snapshot-sensitive-data-status-invalid", self.result(s=s)["hard_stops"])

    def test_35_mutation_release_status_detected(self):
        s = copy.deepcopy(SNAP)
        s["release_state"] = "READY"
        self.assertIn("snapshot-release-state-drift", self.result(s=s)["hard_stops"])

    def test_36_copy_proposes_near_form_notice_not_a_new_list(self):
        self.assertIn("near-form", COPY)
        self.assertIn("No purchase", COPY) if "No purchase" in COPY else self.assertIn("no purchase", COPY.lower())
        self.assertIn("single Jetpack", COPY)

    def test_37_copy_protects_existing_focus_disclosure(self):
        self.assertIn("Leave the existing prominent near-form commission notice intact", COPY)

    def test_38_copy_does_not_instruct_unapproved_installation(self):
        self.assertIn("NOT live edits", COPY)
        self.assertIn("Do NOT install", COPY)

    def test_39_board_is_accessible_static_html(self):
        p = HTMLInspector()
        p.feed(HTML); p.close()
        self.assertIn('lang="en"', HTML)
        self.assertIn('name="viewport"', HTML)
        self.assertIn('<main id="review">', HTML)
        self.assertIn('href="#review"', HTML)
        for forbidden in ("script","iframe","form","input","img","video"):
            self.assertNotIn(forbidden, p.tags)

    def test_40_board_has_no_active_affiliate_vendor_links(self):
        p = HTMLInspector(); p.feed(HTML)
        self.assertTrue(any(x.startswith("https://finalvestige.com/") for x in p.links))
        self.assertFalse(any(x.startswith(("https://zen12.com","https://hypnosislive.com",
                                           "https://inspire3.com")) for x in p.links))

    def test_41_board_labels_real_email_unverified(self):
        self.assertIn("NOT an email preview", HTML)
        self.assertIn("HOLD_UNSENT", HTML)

    def test_42_readme_cites_exact_companion_issues(self):
        self.assertIn("#174", README)
        self.assertIn("#171", README)
        self.assertIn("#175", README)
        self.assertIn("NOT", README)

    def test_43_no_fake_metrics_in_evidence(self):
        self.assertFalse(any(x in json.dumps(SNAP).lower() for x in
                             ("open_rate", "conversion_rate", "ab_winner", "clickthrough_rate")))

    def test_44_actual_standards_financial_relationships(self):
        self.assertIn("Financial relationships are disclosed", SNAP["pages"]["editorial_standards"]["commercial_rule"])

    def test_45_external_sources_are_linked(self):
        urls = SNAP["sources"]
        self.assertTrue(any("ftc.gov" in x for x in urls))
        self.assertTrue(any("wordpress.com/support" in x for x in urls))
        self.assertTrue(any("inspire3.com/ll/" in x for x in urls))
        self.assertTrue(any("hypnosislive.com/mental-skills/total-focus" in x for x in urls))

    def test_46_hard_hold_applies_even_on_all_true_proofs(self):
        s = copy.deepcopy(SNAP)
        for k in s["proof_flags"]: s["proof_flags"][k] = True
        s["newsletter"]["real_received_email_verified"] = True
        s["newsletter"]["received_email_unsubscribe_verified"] = True
        s["newsletter"]["valid_publisher_postal_address_verified"] = True
        s["welcome"]["actual_receipt_verified"] = True
        s["newsletter"]["unique_consent_eligible"] = "VERIFIED"
        self.assertFalse(self.result(s=s)["ready_for_send"])
        self.assertEqual(self.result(s=s)["release_decision"], "HOLD_UNSENT")

if __name__ == "__main__":
    unittest.main()
