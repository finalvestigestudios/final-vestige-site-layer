"""R88 adversarial tests: evidence provenance must never fabricate metrics or unlock email."""
import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / "r88-measurement-proof"
SPEC = importlib.util.spec_from_file_location("r88_measure", HERE / "scorecard.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
BASE = json.loads((HERE / "snapshot.json").read_text(encoding="utf-8"))


class EvidenceScorecard(unittest.TestCase):
    def fresh(self):
        return copy.deepcopy(BASE)

    def invalid(self, fn):
        p = self.fresh()
        fn(p)
        with self.assertRaises(mod.UnsafeEvidence):
            mod.validate(p)

    def test_real_source_snapshot_valid_and_hard_holds(self):
        b = mod.scorecard(self.fresh())
        self.assertEqual(b["status"], "HOLD_UNSENT")
        self.assertTrue(b["counter_conflict"])
        self.assertEqual(b["audience"], "UNKNOWN")
        self.assertEqual([r["status"] for r in b["rows"]].count("HOLD_MERCHANT"), 2)

    def test_no_campaign_values_fabricated(self):
        for r in mod.scorecard(self.fresh())["rows"]:
            for k in ("recipients", "email_clicks", "guide_views", "affiliate_sales"):
                self.assertEqual(r[k], "UNKNOWN")

    def test_recipient_email_prohibited(self):
        self.invalid(lambda p: p.update({"private": "buyer@example.org"}))

    def test_private_sender_address_prohibited(self):
        self.invalid(lambda p: p.update({"sender": "owner@finalvestige.com"}))

    def test_tracking_parameters_prohibited(self):
        self.invalid(lambda p: p.update({"source_paths": {"newsletter": "utm_campaign=pilot", "followers": "ok"}}))

    def test_wrong_site_fails(self):
        self.invalid(lambda p: p.update({"site": "https://another.example"}))

    def test_wrong_schema_fails(self):
        self.invalid(lambda p: p.update({"schema_version": 2}))

    def test_not_send_approval_fails(self):
        self.invalid(lambda p: p.update({"report_type": "READY_TO_SEND"}))

    def test_unknown_eligible_is_not_zero(self):
        self.invalid(lambda p: p.update({"email_eligible_audience": 0}))

    def test_unknown_eligible_is_not_two(self):
        self.invalid(lambda p: p.update({"email_eligible_audience": 2}))

    def test_boolean_count_rejected(self):
        self.invalid(lambda p: p["followers"].update({"email": False}))

    def test_negative_count_rejected(self):
        self.invalid(lambda p: p["newsletter"].update({"count_total": -1}))

    def test_source_identifier_required(self):
        self.invalid(lambda p: p.update({"source_paths": {"newsletter": "yes"}}))

    def test_preserve_exact_original_mix(self):
        self.invalid(lambda p: p["issues"][2].update({"kind": "editorial"}))

    def test_no_seventh_issue(self):
        self.invalid(lambda p: p["issues"].append(copy.deepcopy(p["issues"][0])))

    def test_no_missing_issue(self):
        self.invalid(lambda p: p["issues"].pop())

    def test_no_merchant_link_activation(self):
        self.invalid(lambda p: p["issues"][2].update({"merchant_url": "https://vendor.example"}))

    def test_no_unpublished_guide_promoted(self):
        self.invalid(lambda p: p["issues"][4].update({"cta_state": "first_party_live"}))

    def test_auto_new_post_send_must_remain_off(self):
        self.invalid(lambda p: p["newsletter"].update({"new_post_default_send": True}))

    def test_no_fake_received_email(self):
        self.invalid(lambda p: p.update({"real_received_email_verified": True}))

    def test_no_fake_affiliate_acceptance(self):
        self.invalid(lambda p: p.update({"affiliate_email_permission_verified": True}))

    def test_no_fake_send_authorization(self):
        self.invalid(lambda p: p.update({"founder_send_approval": True}))

    def test_no_fake_tracking_activation(self):
        self.invalid(lambda p: p.update({"attribution_activated": True}))

    def test_no_unverified_revenue(self):
        self.invalid(lambda p: p["issues"][2]["metrics"].update({"affiliate_sales": {"value": 1}}))

    def test_wont_accept_boolean_observation(self):
        self.invalid(lambda p: p["issues"][0]["metrics"].update({"sent": {"value": True, "source": "jetpack_email_run", "proof_ref": "issue174#abcde", "observed_at": "2026-11-03T10:32:00Z"}}))

    def test_source_bound_metric_wont_accept_incorrect_provider(self):
        self.invalid(lambda p: p["issues"][0]["metrics"].update({"sent": {"value": 7, "source": "first_party_analytics", "proof_ref": "issue174#abcde", "observed_at": "2026-11-03T10:32:00Z"}}))

    def test_no_proofless_zero_counts(self):
        self.invalid(lambda p: p["issues"][0]["metrics"].update({"sent": {"value": 0, "source": "jetpack_email_run", "proof_ref": "", "observed_at": "2026-11-03T10:32:00Z"}}))

    def test_valid_proven_aggregate_below_five_suppressed(self):
        p = self.fresh()
        p["issues"][0]["metrics"]["recipients"] = {"value": 2, "source": "jetpack_email_run", "proof_ref": "issue174#proof-1", "observed_at": "2026-11-03T10:32:00Z"}
        self.assertEqual(mod.scorecard(p)["rows"][0]["recipients"], "SUPPRESSED (<5)")

    def test_valid_proven_aggregate_five_shown(self):
        p = self.fresh()
        p["issues"][0]["metrics"]["recipients"] = {"value": 5, "source": "jetpack_email_run", "proof_ref": "issue174#proof-1", "observed_at": "2026-11-03T10:32:00Z"}
        self.assertEqual(mod.scorecard(p)["rows"][0]["recipients"], "5")

    def test_no_inferred_sale_without_outbound_click(self):
        p = self.fresh()
        p["issues"][2]["metrics"]["affiliate_sales"] = {"value": 6, "source": "verified_partner_report", "proof_ref": "issue174#proof-1", "observed_at": "2026-11-03T10:32:00Z"}
        with self.assertRaises(mod.UnsafeEvidence):
            mod.scorecard(p)

    def test_html_static_no_form_or_merchant_link(self):
        page = mod.render_html(mod.scorecard(self.fresh()))
        self.assertIn("<caption>", page)
        self.assertIn("aria-label", page)
        self.assertNotIn("<form", page)
        self.assertNotIn("zen12.com", page)
        self.assertNotIn("hypnosislive.com", page)
        self.assertNotIn("<script", page)
        self.assertIn("HOLD_UNSENT", page)

    def test_text_mentions_no_ab_testing(self):
        t = mod.render_text(mod.scorecard(self.fresh()))
        self.assertIn("No A/B tests", t)
        self.assertIn("UNKNOWN", t)
        self.assertIn("HOLD_MERCHANT", t)

    def test_missing_wordpress_follower_breakdown_fails(self):
        self.invalid(lambda p: p["followers"].pop("wpcom"))

    def test_recent_posts_no_duplicate_ids(self):
        self.invalid(lambda p: p["newsletter"].update({"recent_post_ids_never_sent_opted_out": [1926]*5}))

    def test_lifetime_sent_unsupported(self):
        self.invalid(lambda p: p["newsletter"].update({"email_content_format": "full"}))

if __name__ == "__main__":
    unittest.main()
