"""R40 adversarial native-post-field and WordPress read-only evidence tests.

These do not create WordPress drafts or send a single email. Synthetic
field-alignment PASS is NEVER release approval, legal compliance or inbox
rendering proof. All tests are safe to run in CI without credentials.
"""
import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
MOD = BASE / "r40-native-post-proof" / "native_post_field_gate.py"
SPEC = importlib.util.spec_from_file_location("r40_native_post_field_gate", MOD)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def fake_post(packet):
    return {
        "site": "finalvestige.com",
        "post_type": "post",
        "status": "draft",
        "title": {"raw": packet["post_title_required_as_native_subject"]},
        "excerpt": {"raw": packet["custom_excerpt_required"]},
        "content": {"raw": "<p>" + "An independently edited safe editorial paragraph. " * 4 +
                     "</p><p>Learn how to separate an observation from its explanation.</p>"},
        "send_this_post_to_subscribers": False,
        "publication_scheduled": False,
        "published": False,
        "sent": False,
        "approved": False,
        "scheduled": False,
    }


class ActualSourceIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = gate.packets()
        cls.report = gate.assessment()

    def test_six_present(self):
        self.assertEqual([x["number"] for x in self.items], [1,2,3,4,5,6])

    def test_four_two_split(self):
        self.assertEqual(sum(x["edition_release"] == "HOLD_UNSENT"
                             for x in self.items), 4)
        self.assertEqual(sum(x["edition_release"] == "HOLD_MERCHANT_AND_UNSENT"
                             for x in self.items), 2)

    def test_hold_on_every_packet(self):
        self.assertTrue(all(x["founder_final_send_approval"] is False for x in self.items))
        self.assertTrue(self.report["approved_for_any_send"] is False)

    def test_all_native_subjects_nonempty(self):
        self.assertTrue(all(len(x["post_title_required_as_native_subject"]) > 12
                            for x in self.items))

    def test_commercial_disclosures_present_in_excerpt(self):
        for x in self.items:
            if x["number"] in (3,5):
                self.assertIn("commission", x["custom_excerpt_required"].lower())
                self.assertIn("affiliate", x["custom_excerpt_required"].lower())

    def test_exact_expected_custom_excerpts_not_installed(self):
        self.assertTrue(all(x["custom_excerpt_not_installed"] for x in self.items))
        self.assertTrue(all(x["native_preview_verified"] is False for x in self.items))

    def test_no_tracking_link_activated(self):
        manifest = json.loads((BASE / "manifest.json").read_text())
        self.assertTrue(all(x["merchant_affiliate_url"] is None for x in manifest["issues"]))

    def test_two_merchant_guides_are_not_live(self):
        self.assertTrue(all(x["first_party_guide_live"] is False for x in self.items
                            if x["number"] in (3,5)))

    def test_no_native_preheader_control_claimed(self):
        self.assertTrue(all(x["planned_preheader_separate_jetpack_control_verified"] is False
                            for x in self.items))

    def test_read_only_snapshot_does_not_claim_audience(self):
        self.assertEqual(self.report["subscriber_counts"],
                         "NON_ADDITIVE_2_2_2_UNIQUE_ELIGIBLE_UNKNOWN")

    def test_detect_feature_image_and_date_first(self):
        self.assertIs(self.report["featured_image_top_of_email_enabled"], True)
        self.assertIs(self.report["post_date_byline_enabled"], True)

    def test_no_publish_job_in_report(self):
        self.assertEqual(self.report["publisher_action"], "NONE")


class SanitizedFieldAlignment(unittest.TestCase):
    def setUp(self):
        self.issue = gate.packets()[0]
        self.good = fake_post(self.issue)

    def failures(self, candidate):
        return gate.audit_manual_post_snapshot(self.issue, candidate)["checks_failed"]

    def test_synthetic_fields_pass_only_alignment(self):
        result = gate.audit_manual_post_snapshot(self.issue, self.good)
        self.assertEqual(result["field_alignment"], "PASS_REVIEW_FIELDS_ONLY")
        self.assertEqual(result["authorization"], "HOLD_UNSENT")
        self.assertEqual(result["legal_footer_and_functional_unsubscribe"], "UNVERIFIED")

    def test_wrong_site_fails(self):
        p = copy.deepcopy(self.good)
        p["site"] = "attacker.example"
        self.assertIn("wrong_site", self.failures(p))

    def test_page_instead_of_post_fails(self):
        p = copy.deepcopy(self.good); p["post_type"] = "page"
        self.assertIn("wrong_post_type", self.failures(p))

    def test_published_state_fails(self):
        p = copy.deepcopy(self.good); p["status"] = "publish"
        self.assertIn("not_a_draft", self.failures(p))

    def test_false_subject_fails(self):
        p = copy.deepcopy(self.good); p["title"] = "A secret hypnotic breakthrough"
        self.assertIn("subject_drift", self.failures(p))

    def test_empty_excerpt_fails(self):
        p = copy.deepcopy(self.good); p["excerpt"] = ""
        self.assertIn("custom_excerpt_missing_or_drifted", self.failures(p))

    def test_tampered_excerpt_fails(self):
        p = copy.deepcopy(self.good); p["excerpt"]["raw"] += " EXTRA"
        self.assertIn("custom_excerpt_missing_or_drifted", self.failures(p))

    def test_short_body_fails(self):
        p = copy.deepcopy(self.good); p["content"] = "<p>Short.</p>"
        self.assertIn("empty_post_body", self.failures(p))

    def test_internal_draft_warning_exposure_fails(self):
        p = copy.deepcopy(self.good); p["content"]["raw"] += " DO NOT PUBLISH OR EMAIL"
        self.assertIn("internal_editor_markers_exposed", self.failures(p))

    def test_postal_placeholder_exposure_fails(self):
        p = copy.deepcopy(self.good); p["content"]["raw"] += "[[VALID_POSTAL_ADDRESS_REQUIRED]]"
        self.assertIn("internal_editor_markers_exposed", self.failures(p))

    def test_direct_zen12_checkout_fails(self):
        p = copy.deepcopy(self.good)
        p["content"]["raw"] += '<a href="https://zen12.com/getstarted?x=y">Seller page</a>'
        self.assertIn("direct_seller_route_bypass", self.failures(p))

    def test_subdomain_seller_fails(self):
        p = copy.deepcopy(self.good)
        p["content"]["raw"] += "<a href='https://promo.hypnosislive.com/cart'>Check out</a>"
        self.assertIn("direct_seller_route_bypass", self.failures(p))

    def test_unapproved_affiliate_host_fails(self):
        p = copy.deepcopy(self.good)
        p["content"]["raw"] += " https://hop.clickbank.net/anything"
        self.assertIn("earning_link_not_authorized", self.failures(p))

    def test_email_send_toggle_true_fails(self):
        p = copy.deepcopy(self.good); p["send_this_post_to_subscribers"] = True
        self.assertIn("newsletter_toggle_must_remain_off", self.failures(p))

    def test_unknown_send_toggle_fails(self):
        p = copy.deepcopy(self.good); del p["send_this_post_to_subscribers"]
        self.assertIn("newsletter_toggle_must_remain_off", self.failures(p))

    def test_future_scheduled_post_fails(self):
        p = copy.deepcopy(self.good); p["publication_scheduled"] = True
        self.assertIn("scheduled_post_not_allowed", self.failures(p))

    def test_false_release_metadata_fails(self):
        for flag in gate.UNAUTHORIZED_CMS_FLAGS:
            p = copy.deepcopy(self.good); p[flag] = True
            self.assertIn("unauthorized_" + flag, self.failures(p))

    def test_mailto_token_fails(self):
        p = copy.deepcopy(self.good)
        p["content"]["raw"] += '<a href="mailto:private@example.org?subject=abc">Contact</a>'
        self.assertIn("personally_addressed_link_or_token", self.failures(p))

    def test_rendered_dict_title_accepted_but_not_proof(self):
        p = copy.deepcopy(self.good)
        p["title"] = {"rendered": self.issue["post_title_required_as_native_subject"]}
        result = gate.audit_manual_post_snapshot(self.issue, p)
        self.assertEqual(result["field_alignment"], "PASS_REVIEW_FIELDS_ONLY")
        self.assertEqual(result["native_inbox_and_welcome"], "UNVERIFIED")


class AdversarialRealSource(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copy(BASE / "manifest.json", self.root / "manifest.json")
        (self.root / "delivery").mkdir()
        shutil.copy(BASE / "delivery" / "wordpress_excerpt_copy.json",
                    self.root / "delivery" / "wordpress_excerpt_copy.json")
        shutil.copytree(BASE / "issues", self.root / "issues")
        self.evidence = self.root / "evidence.json"
        shutil.copy(gate.EVIDENCE, self.evidence)

    def mutate_json(self, path, fn):
        data = json.loads(path.read_text(encoding="utf-8"))
        fn(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def expect_reject(self):
        with self.assertRaises(ValueError):
            gate.packets(self.root, self.evidence)

    def test_incorrect_merchandise_mix_fails(self):
        self.mutate_json(self.root / "manifest.json",
                         lambda o: o["issues"][2].update(kind="editorial"))
        self.expect_reject()

    def test_new_post_auto_email_on_fails(self):
        self.mutate_json(self.evidence,
                         lambda o: o["wordpress"].update(email_new_posts_by_default=True))
        self.expect_reject()

    def test_positive_external_attestation_fails(self):
        self.mutate_json(self.evidence,
                         lambda o: o["external_release_proofs"].update(
                             real_received_jetpack_email=True))
        self.expect_reject()

    def test_subject_mismatch_fails(self):
        self.mutate_json(self.root / "manifest.json",
                         lambda o: o["issues"][0].update(subject="Unverified miracle"))
        self.expect_reject()

    def test_forged_merchant_link_fails(self):
        self.mutate_json(self.root / "manifest.json",
                         lambda o: o["issues"][2].update(
                             merchant_affiliate_url="https://hop.clickbank.net/token"))
        self.expect_reject()

    def test_leaky_affiliate_excerpt_fails(self):
        self.mutate_json(self.root / "delivery" / "wordpress_excerpt_copy.json",
                         lambda o: o["entries"][2].update(
                             excerpt="Read https://zen12.com/getstarted " + "hello " * 45))
        self.expect_reject()

    def test_missing_disclosure_fails(self):
        self.mutate_json(self.root / "delivery" / "wordpress_excerpt_copy.json",
                         lambda o: o["entries"][4].update(
                             excerpt="Focus and audio claims. " * 15))
        self.expect_reject()

    def test_missing_hardstop_marker_fails(self):
        path = self.root / "issues" / gate.ISSUES[1]
        path.write_text(path.read_text().replace("DO NOT PUBLISH OR EMAIL", "READY TO SEND"))
        self.expect_reject()

    def test_inconsistent_subscriber_counter_fails(self):
        self.mutate_json(self.evidence,
                         lambda o: o["wordpress"]["subscriber_counts"].update(total=4))
        self.expect_reject()

    def test_false_publication_approval_fails(self):
        self.mutate_json(self.root / "manifest.json",
                         lambda o: o["issues"][0].update(publish_state="publish"))
        self.expect_reject()


if __name__ == "__main__":
    unittest.main()
