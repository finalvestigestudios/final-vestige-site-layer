"""19 adversarial offline checks: aggregate subscriber counts never authorize a send."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "audience_guard.py"
spec = importlib.util.spec_from_file_location("audience_guard", MODULE)
audience = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audience)
BASE = {
    "subscribers": {
        "total": 2, "confirmed": 2, "unconfirmed": 2,
        "suppressed": 0, "paid": 0, "imported_last_24h": 0,
    },
    "recent_sends": [],
    "settings": {
        "subscriptions": True, "email_new_posts_by_default": False,
        "email_content_format": "excerpt",
    },
}


class WordPressSubscriberCountSafety(unittest.TestCase):
    def test_observed_2_2_2_is_not_arithmetic_contradiction(self):
        x = audience.interpret(BASE)
        self.assertEqual(x["counter_interpretation"], "CONSISTENT_WITH_DOCUMENTED_WP_BUCKETS")
        self.assertEqual(x["total_reported"], 2)
        self.assertEqual(x["unconfirmed_not_in_total"], 2)

    def test_unconfirmed_are_never_added_to_confirmed_total(self):
        x = audience.interpret(BASE)
        self.assertEqual(x["maximum_possible_confirmed_email_recipients"], 2)
        self.assertNotEqual(x["maximum_possible_confirmed_email_recipients"], 4)

    def test_eligible_unknown_and_hold_even_with_positive_count(self):
        x = audience.interpret(BASE)
        self.assertIsNone(x["actual_email_eligible_recipients"])
        self.assertEqual(x["release_decision"], "HOLD_UNSENT")
        self.assertFalse(x["founder_send_approval_verified"])

    def test_zero_confirmed_positive_pending_is_consistent(self):
        x = copy.deepcopy(BASE)
        x["subscribers"].update(total=0, confirmed=0, unconfirmed=21)
        self.assertEqual(audience.interpret(x)["counter_interpretation"], "CONSISTENT_WITH_DOCUMENTED_WP_BUCKETS")

    def test_confirmed_more_than_total_requires_private_reconciliation(self):
        x = copy.deepcopy(BASE)
        x["subscribers"].update(total=1, confirmed=2)
        self.assertEqual(audience.interpret(x)["counter_interpretation"], "REQUIRES_PRIVATE_RECONCILIATION")

    def test_suppressed_does_not_silently_reduce_or_grant_eligibility(self):
        x = copy.deepcopy(BASE)
        x["subscribers"]["suppressed"] = 1
        self.assertIsNone(audience.interpret(x)["actual_email_eligible_recipients"])

    def test_all_zero_counts_still_hold(self):
        x = copy.deepcopy(BASE)
        x["subscribers"] = {k: 0 for k in x["subscribers"]}
        self.assertEqual(audience.interpret(x)["release_decision"], "HOLD_UNSENT")

    def test_autosend_enabled_does_not_grant_authority(self):
        x = copy.deepcopy(BASE)
        x["settings"]["email_new_posts_by_default"] = True
        self.assertEqual(audience.interpret(x)["release_decision"], "HOLD_UNSENT")

    def test_mail_format_full_does_not_prove_delivery(self):
        x = copy.deepcopy(BASE)
        x["settings"]["email_content_format"] = "full"
        self.assertFalse(audience.interpret(x)["full_received_email_verified"])

    def test_report_sends_without_content_or_identity(self):
        x = copy.deepcopy(BASE)
        x["recent_sends"] = [{"recipient": "PRIVATE@example.com", "subject": "PRIVATE"}]
        result = audience.interpret(x)
        self.assertFalse(result["no_recent_sends_reported"])
        self.assertNotIn("PRIVATE", json.dumps(result))

    def test_unknown_subscriber_pii_fields_are_never_echoed(self):
        x = copy.deepcopy(BASE)
        x["subscribers"]["email_address"] = "PRIVATE@example.com"
        x["subscriber_details"] = [{"name": "PRIVATE NAME"}]
        self.assertNotIn("PRIVATE", json.dumps(audience.interpret(x)))

    def test_user_claimed_approvals_are_ignored(self):
        x = copy.deepcopy(BASE)
        x.update(founder_send_approval_verified=True, real_unsubscribe_and_sender_postal_verified=True)
        z = audience.interpret(x)
        self.assertFalse(z["founder_send_approval_verified"])
        self.assertFalse(z["real_unsubscribe_and_sender_postal_verified"])

    def test_pending_not_counted_even_if_100000(self):
        x = copy.deepcopy(BASE)
        x["subscribers"]["unconfirmed"] = 100000
        self.assertEqual(audience.interpret(x)["maximum_possible_confirmed_email_recipients"], 2)

    def test_invalid_counts_rejected(self):
        for v in (-1, 1.5, "2", True, None, {}, [], 2**63/1.):
            with self.subTest(v=repr(v)):
                x = copy.deepcopy(BASE)
                x["subscribers"]["unconfirmed"] = v
                with self.assertRaises(ValueError):
                    audience.interpret(x)

    def test_missing_each_count_rejected(self):
        for key in audience.COUNT_KEYS:
            with self.subTest(key=key):
                x = copy.deepcopy(BASE)
                del x["subscribers"][key]
                with self.assertRaises(ValueError):
                    audience.interpret(x)

    def test_invalid_settings_rejected(self):
        for value in (None, "true", 1, False):
            with self.subTest(value=value):
                x = copy.deepcopy(BASE)
                x["settings"]["email_content_format"] = value
                with self.assertRaises(ValueError):
                    audience.interpret(x)

    def test_invalid_bool_flags_rejected(self):
        for k in ("subscriptions", "email_new_posts_by_default"):
            for value in (None, 1, 0, "false", "true"):
                with self.subTest(k=k, value=value):
                    x = copy.deepcopy(BASE)
                    x["settings"][k] = value
                    with self.assertRaises(ValueError):
                        audience.interpret(x)

    def test_invalid_snapshot_types_rejected(self):
        for x in (None, [], 1, "text", {"subscribers": "oops"}, {"subscribers": BASE["subscribers"], "settings": []}):
            with self.subTest(value=repr(x)):
                with self.assertRaises(ValueError):
                    audience.interpret(x)

    def test_sends_must_be_array(self):
        x = copy.deepcopy(BASE)
        x["recent_sends"] = "none"
        with self.assertRaises(ValueError):
            audience.interpret(x)


if __name__ == "__main__":
    unittest.main()
