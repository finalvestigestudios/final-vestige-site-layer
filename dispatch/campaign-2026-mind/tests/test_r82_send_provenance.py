"""R82: native Python adversarial checks for exact live aggregate send-state evidence.

No recipient identity, test email, network request, or publication occurs.
Run: python -m unittest discover -s dispatch/campaign-2026-mind/tests -p test_r82_send_provenance.py -v
"""
import copy
import importlib.util
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parents[1] / "r82-send-provenance"
spec = importlib.util.spec_from_file_location("fv_r82_verifier", HERE / "verifier.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class R82ProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((HERE / "SNAPSHOT.json").read_text(encoding="utf-8"))
        cls.text = (HERE / "README.md").read_text(encoding="utf-8")
        cls.preview = (HERE / "REVIEW.html").read_text(encoding="utf-8")
        cls.plain = (HERE / "REVIEW.txt").read_text(encoding="utf-8")

    def mutate(self, fn):
        item = copy.deepcopy(self.original)
        fn(item)
        with self.assertRaises(ValueError):
            mod.summarize(item)

    def test_exact_snapshot_valid(self):
        self.assertTrue(mod.validate(self.original))

    def test_declared_no_send(self):
        summary = mod.summarize(self.original)
        self.assertEqual(summary["status"], "HOLD_UNSENT")
        self.assertEqual(summary["release"], "NO_SEND_NO_TEST_SEND_NO_PUBLISH_NO_WORDPRESS_CHANGES")

    def test_only_returned_rows(self):
        summary = mod.summarize(self.original)
        self.assertEqual(summary["returned_recent_records"], 5)
        self.assertEqual(summary["records_unequivocally_never_sent_opted_out"], 5)
        self.assertEqual(summary["dispatched_in_these_returned_records"], 0)

    def test_not_sitewide_zero(self):
        self.assertTrue(mod.summarize(self.original)["all_time_sends"].startswith("UNKNOWN"))

    def test_no_recipient_inference(self):
        self.assertTrue(mod.summarize(self.original)["actual_email_eligible_recipients"].startswith("UNKNOWN"))

    def test_cannot_infer_delivery_from_ability(self):
        self.assertFalse(mod.summarize(self.original)["site_can_send_means_delivery"])

    def test_welcome_config_is_not_receipt(self):
        self.assertFalse(mod.summarize(self.original)["configured_welcome_means_received"])

    def test_no_private_data_in_preview(self):
        combined = self.preview + self.plain + self.text
        self.assertNotRegex(combined, r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
        self.assertNotIn("utm_source=", combined)
        self.assertNotIn("aff_id=", combined)

    def test_reject_extra_personal_field(self):
        self.mutate(lambda s: s.update(subscriber_email="someone@example.test"))

    def test_reject_private_address_in_title(self):
        self.mutate(lambda s: s["recent_send_records"][0].update(title="Notifies person@example.test"))

    def test_reject_token_in_title(self):
        self.mutate(lambda s: s["recent_send_records"][0].update(title="https://example.test/?token=secret"))

    def test_reject_wrong_campaign_state(self):
        self.mutate(lambda s: s.update(campaign_status="APPROVED_SEND"))

    def test_reject_wrong_source_identity(self):
        self.mutate(lambda s: s.update(original_master_pr=49))

    def test_reject_attempt_to_verify_postal_address_by_edit(self):
        self.mutate(lambda s: s["shared_gates"].update(founder_postal_address_verified=True))

    def test_reject_attempt_to_authorize_merchant(self):
        self.mutate(lambda s: s["commercial_gates"].update(zen12_email_permission=True))

    def test_reject_direct_send_attestation(self):
        self.mutate(lambda s: s["shared_gates"].update(final_founder_send_approval=True))

    def test_reject_deliverable_audience_inference(self):
        self.mutate(lambda s: s.update(deliverable_audience=2))

    def test_reject_boolean_as_count(self):
        self.mutate(lambda s: s["newsletter_counters"].update(total=True))

    def test_reject_added_count_categories(self):
        self.mutate(lambda s: s["newsletter_counters"].update(imported=9))

    def test_reject_follower_classification_change(self):
        self.mutate(lambda s: s["follower_counters"].update(email=2, wpcom=0))

    def test_reject_new_status_claiming_sent(self):
        self.mutate(lambda s: s["recent_send_records"][0].update(status="sent"))

    def test_reject_dispatch_timestamp(self):
        self.mutate(lambda s: s["recent_send_records"][0].update(dispatched_at="2026-11-03T05:00:00+00:00"))

    def test_reject_numeric_zero_for_unknown_count(self):
        self.mutate(lambda s: s["recent_send_records"][0]["counts"].update(recipients=0))

    def test_reject_false_reason(self):
        self.mutate(lambda s: s["recent_send_records"][0].update(reason="No subscribers"))

    def test_reject_duplicate_post_id(self):
        self.mutate(lambda s: s["recent_send_records"][1].update(post_id=1926))

    def test_reject_missing_returned_row(self):
        self.mutate(lambda s: s.update(recent_send_records=s["recent_send_records"][:4]))

    def test_reject_out_of_order_timestamps(self):
        self.mutate(lambda s: s["recent_send_records"][0].update(scheduled_for="2026-11-03T04:46:00+00:00"))

    def test_reject_future_timestamp(self):
        self.mutate(lambda s: s["recent_send_records"][0].update(scheduled_for="2026-11-04T04:54:10+00:00"))

    def test_reject_naive_timestamp(self):
        self.mutate(lambda s: s.update(snapshot_as_of_utc="2026-11-03T05:03:04"))

    def test_reject_new_site(self):
        self.mutate(lambda s: s.update(site="https://attacker.example.test"))

    def test_reject_auto_email_toggle(self):
        self.mutate(lambda s: s["newsletter"].update(email_new_posts_by_default=True))

    def test_reject_excerpts_changed_to_full(self):
        self.mutate(lambda s: s["newsletter"].update(email_content_format="full"))

    def test_reject_claim_welcome_received(self):
        self.mutate(lambda s: s["newsletter"].update(actual_welcome_receipt_verified=True))

    def test_reject_schema_tampering(self):
        self.mutate(lambda s: s.update(schema_version="future"))

    def test_no_mail_capability_in_software(self):
        program = (HERE / "verifier.py").read_text(encoding="utf-8")
        self.assertNotIn("smtplib", program)
        self.assertNotIn("requests.", program)
        self.assertNotIn("urllib.request", program)
        self.assertNotIn("subprocess", program)
        self.assertNotIn("os.system", program)

    def test_review_is_accessible_and_noninteractive(self):
        self.assertIn('lang="en"', self.preview)
        self.assertIn('name="viewport"', self.preview)
        self.assertIn('href="#main"', self.preview)
        for forbidden in ("<script", "<form", "<iframe", "<img", "mailto:", "https://zen12.com/hnp?"):
            self.assertNotIn(forbidden, self.preview.lower())

    def test_policy_audit_contains_essential_gates(self):
        for term in ("HOLD_UNSENT", "HOLD_MERCHANT", "CAN-SPAM",
                     "real received email", "postal address", "subscriber",
                     "not all-time", "Issue #174", "Issue #171"):
            self.assertIn(term.lower(), self.text.lower())

    def test_source_paths_preserve_original_campaign(self):
        self.assertEqual(self.original["original_master_pr"], 175)
        self.assertEqual(self.original["stack_parent_pr"], 721)
        self.assertEqual(self.original["commercial_gates"]["zen12_email_permission"], False)
        self.assertEqual(self.original["commercial_gates"]["total_focus_email_permission"], False)


if __name__ == "__main__":
    unittest.main()
