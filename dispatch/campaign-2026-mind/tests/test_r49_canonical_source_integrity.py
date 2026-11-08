"""R49 regression and adversarial tests: canonical source of truth, no sends."""
import copy
import json
from pathlib import Path
from html import escape
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r49-cta-integrity"))
from cross_layer_gate import audit, load_and_audit

class CanonicalCrossLayerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.fixture = json.loads((ROOT / "readiness/fixtures/manifest_snapshot.json").read_text(encoding="utf-8"))
        cls.ledger = json.loads((ROOT / "readiness/canonical_cta_ledger.json").read_text(encoding="utf-8"))
        cls.board = (ROOT / "readiness/review_board.html").read_text(encoding="utf-8")
        cls.manuscripts = {
            x["number"]: (ROOT / "issues" / f"{x['number']:02d}-{x['slug']}.md").read_text(encoding="utf-8")
            for x in cls.manifest["issues"]
        }
        cls.routes = json.loads((ROOT / "r49-cta-integrity/verified_routes.json").read_text(encoding="utf-8"))

    def evaluate(self, manifest=None, fixture=None, ledger=None, manuscripts=None, board=None):
        return audit(
            manifest if manifest is not None else copy.deepcopy(self.manifest),
            fixture if fixture is not None else copy.deepcopy(self.fixture),
            ledger if ledger is not None else copy.deepcopy(self.ledger),
            manuscripts if manuscripts is not None else copy.deepcopy(self.manuscripts),
            board if board is not None else self.board,
        )

    def test_source_integrity_green_while_release_closed(self):
        self.assertEqual(load_and_audit()["source_errors"], [])
        self.assertFalse(load_and_audit()["send_authorized"])

    def test_all_six_manifest_entries_are_unchanged_holds(self):
        self.assertEqual([x["number"] for x in self.manifest["issues"]], list(range(1, 7)))
        self.assertTrue(all(x["publish_state"] == "hold" for x in self.manifest["issues"]))

    def test_four_editorial_two_commercial(self):
        self.assertEqual(self.manifest["mix"], {"editorial": 4, "commercial_review_pending": 2})
        self.assertEqual([x["number"] for x in self.manifest["issues"] if x["kind"] == "commercial-review-pending"], [3, 5])

    def test_fixture_is_field_for_field_copy_not_parallel_truth(self):
        for actual, fixture in zip(self.manifest["issues"], self.fixture["issues"]):
            self.assertEqual(actual, fixture)

    def test_ledger_targets_all_match_original_manifest(self):
        for original, row in zip(self.manifest["issues"], self.ledger["entries"]):
            self.assertEqual(original["editorial_cta"], row["cta_expected"])

    def test_correct_edition_one_source(self):
        self.assertEqual(self.manifest["issues"][0]["editorial_cta"], "https://finalvestige.com/the-missing-caption/")
        self.assertEqual(self.ledger["entries"][0]["source_urls"][0], "https://finalvestige.com/the-missing-caption/")
        self.assertIn("1122", self.ledger["entries"][0]["destination_status"])
        self.assertNotIn("Puységur", self.ledger["entries"][0]["source_titles"][0])

    def test_published_routes_only_for_editorials(self):
        self.assertEqual([r["edition"] for r in self.routes["destinations"]], list(range(1,7)))
        for row in self.routes["destinations"]:
            if row["edition"] in (1,2,4,6):
                self.assertEqual(row["status"], "PUBLISHED_VERIFIED_READ_ONLY")
                self.assertIsInstance(row["wordpress_id"], int)
            else:
                self.assertEqual(row["status"], "HOLD_UNPUBLISHED_GUIDE")
                self.assertIsNone(row["wordpress_id"])

    def test_no_commercial_warmup_is_claimed_live(self):
        for n in (3,5):
            self.assertTrue(self.manifest["issues"][n-1]["editorial_cta"].startswith("[["))
            self.assertIn("Blocked", self.ledger["entries"][n-1]["destination_status"])

    def test_review_board_is_source_consistent(self):
        self.assertEqual(self.board.count('class="card '), 6)
        for issue in self.manifest["issues"]:
            self.assertIn(escape(issue["preheader"], quote=True), self.board)

    def test_review_board_does_not_claim_approval(self):
        self.assertEqual(self.board.count("HELD — NOT SENT"), 6)
        self.assertNotIn("https://zen12.com", self.board)
        self.assertNotIn("https://hypnosislive.com", self.board)

    def test_observed_wordpress_is_privacy_safe(self):
        self.assertEqual(self.routes["newsletter"]["counters"], {"total":2, "confirmed":2, "unconfirmed":2})
        self.assertIsNone(self.routes["newsletter"]["verified_unique_eligible"])
        self.assertEqual(self.routes["newsletter"]["recent_sends"], [])
        self.assertFalse(self.routes["newsletter"]["zero_lifetime_sends_proven"])
        self.assertNotIn("@gmail.com", json.dumps(self.routes))

    def test_observed_settings_preserve_existing_stack(self):
        settings = self.routes["newsletter"]
        self.assertTrue(settings["subscriptions"])
        self.assertFalse(settings["email_new_posts_by_default"])
        self.assertEqual(settings["email_content_format"], "excerpt")
        self.assertEqual(settings["reply_to"], "no-reply")

    def test_no_real_received_preview_claim(self):
        for name in ("actual_received_email","actual_welcome_receipt","postal_address_verified","unsub_render_verified","merchant_email_rights_verified","final_founder_send_approval"):
            self.assertFalse(self.routes["release_attestations"][name])

    def test_mutated_fixture_preheader_is_caught(self):
        x=copy.deepcopy(self.fixture);x["issues"][0]["preheader"]="False preheader"
        self.assertIn("issue_1_fixture_preheader_drift",self.evaluate(fixture=x)["source_errors"])

    def test_mutated_fixture_cta_is_caught(self):
        x=copy.deepcopy(self.fixture);x["issues"][0]["editorial_cta"]="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"
        self.assertIn("issue_1_fixture_editorial_cta_drift",self.evaluate(fixture=x)["source_errors"])

    def test_mutated_ledger_is_caught(self):
        x=copy.deepcopy(self.ledger);x["entries"][0]["cta_expected"]="https://example.net/"
        self.assertIn("issue_1_ledger_cta_drift",self.evaluate(ledger=x)["source_errors"])

    def test_unauthorized_commercial_cta_is_caught(self):
        x=copy.deepcopy(self.manifest);x["issues"][2]["editorial_cta"]="https://zen12.com/hnp"
        self.assertIn("issue_3_guide_not_held",self.evaluate(manifest=x)["source_errors"])

    def test_premature_publish_is_caught(self):
        x=copy.deepcopy(self.manifest);x["issues"][0]["publish_state"]="publish"
        self.assertIn("issue_1_publication_or_affiliate_activation",self.evaluate(manifest=x)["source_errors"])

    def test_affiliate_link_activation_is_caught(self):
        x=copy.deepcopy(self.manifest);x["issues"][4]["merchant_affiliate_url"]="https://example.com/tracking"
        self.assertIn("issue_5_publication_or_affiliate_activation",self.evaluate(manifest=x)["source_errors"])

    def test_deceptive_subject_drift_is_caught(self):
        x=copy.deepcopy(self.manuscripts);x[1]=x[1].replace("**Subject:** The mind is not a camera", "**Subject:** Get rich instantly")
        self.assertIn("issue_1_manuscript_subject_drift",self.evaluate(manuscripts=x)["source_errors"])

    def test_preheader_drift_is_caught(self):
        x=copy.deepcopy(self.manuscripts);x[5]=x[5].replace(self.manifest["issues"][4]["preheader"],"fake preview")
        self.assertIn("issue_5_manuscript_preheader_drift",self.evaluate(manuscripts=x)["source_errors"])

    def test_misplaced_cta_is_caught(self):
        x=copy.deepcopy(self.manuscripts);x[6]=x[6].replace("https://finalvestige.com/focus/","https://example.com/")
        self.assertIn("issue_6_manuscript_primary_cta_drift",self.evaluate(manuscripts=x)["source_errors"])

    def test_missing_postal_token_is_caught(self):
        x=copy.deepcopy(self.manuscripts);x[3]=x[3].replace("[[VALID_POSTAL_ADDRESS_REQUIRED]]","123 Fake Road")
        self.assertIn("issue_3_missing_legal_hard_stop",self.evaluate(manuscripts=x)["source_errors"])

    def test_missing_unsubscribe_token_is_caught(self):
        x=copy.deepcopy(self.manuscripts);x[2]=x[2].replace("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]","unsubscribe soon")
        self.assertIn("issue_2_missing_legal_hard_stop",self.evaluate(manuscripts=x)["source_errors"])

    def test_missing_disclosure_is_caught(self):
        x=copy.deepcopy(self.manuscripts);x[5]=x[5].replace("Commercial disclosure:","General note:")
        self.assertIn("issue_5_missing_commercial_disclosure",self.evaluate(manuscripts=x)["source_errors"])

    def test_missing_draft_warning_is_caught(self):
        x=copy.deepcopy(self.manuscripts);x[1]=x[1].replace("STATUS: UNSENT DRAFT","READY")
        self.assertIn("issue_1_unsafe_draft_header",self.evaluate(manuscripts=x)["source_errors"])

    def test_board_mismatched_preheader_is_caught(self):
        bad=self.board.replace(self.manifest["issues"][0]["preheader"],"Old preview")
        self.assertIn("issue_1_reviewer_preheader_drift",self.evaluate(board=bad)["source_errors"])

    def test_board_mismatched_destination_is_caught(self):
        bad=self.board.replace(self.ledger["entries"][0]["destination_status"],"wrong destination")
        self.assertIn("issue_1_reviewer_destination_drift",self.evaluate(board=bad)["source_errors"])

    def test_wrong_six_order_is_caught(self):
        x=copy.deepcopy(self.ledger);x["entries"].reverse()
        self.assertIn("ledger_six_order",self.evaluate(ledger=x)["source_errors"])

    def test_mix_change_is_caught(self):
        x=copy.deepcopy(self.manifest);x["mix"]["editorial"]=5
        self.assertIn("mix_drift",self.evaluate(manifest=x)["source_errors"])

    def test_both_status_and_authorization_remain_hard_off(self):
        result=self.evaluate()
        self.assertEqual(result["status"],"HOLD_UNSENT")
        self.assertFalse(result["send_authorized"])
        self.assertFalse(result["founder_final_send_approval"])
        self.assertFalse(result["actual_received_jetpack_email_verified"])

if __name__ == "__main__":
    unittest.main()
