"""R75 independent fail-closed tests. Uses only local synthetic/count-only data."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
R75 = ROOT / "r75-channel-consent-proof"
SPEC = importlib.util.spec_from_file_location("channel_proof_r75", R75 / "channel_proof.py")
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)

class R75Evidence(unittest.TestCase):
    def setUp(self):
        self.original = json.loads((R75 / "count_only_attestations.json").read_text(encoding="utf-8"))
        self.record = copy.deepcopy(self.original)

    def test_schema_is_pinned(self):
        self.assertEqual(self.record["schema"], "fv-dispatch-human-evidence-v1")

    def test_canonical_snapshot_is_not_four_people(self):
        s = self.record["snapshot"]
        self.assertEqual((s["total"], s["confirmed"], s["unconfirmed"], s["suppressed"]), (2, 2, 2, 0))
        self.assertIsNone(s["eligible_email_count"])

    def test_production_mode_is_off(self):
        s = self.record["snapshot"]
        self.assertTrue(s["newsletter_enabled"])
        self.assertFalse(s["new_post_auto_email"])
        self.assertEqual(s["content_format"], "excerpt")
        self.assertEqual(s["recent_send_count"], 0)

    def test_no_human_attestation_as_if_verified(self):
        self.assertTrue(all(v is False for v in self.record["attestations"].values()))
        self.assertTrue(all(v is False for obj in self.record["merchants"].values() for v in obj.values()))

    def test_all_six_are_held(self):
        states = proof.assess(self.record)["edition_states"]
        self.assertEqual(len(states), 6)
        self.assertEqual(sum(v == "HOLD_MERCHANT" for v in states.values()), 2)
        self.assertEqual(sum(v == "HOLD_UNSENT" for v in states.values()), 4)

    def test_merchant_slots_are_only_three_five(self):
        self.assertEqual(set(self.record["merchants"]), {"03", "05"})

    def test_releases_never_authorized(self):
        r = proof.assess(self.record)
        self.assertIs(r["send_allowed"], False)
        self.assertEqual(r["release_state"], "HOLD_UNSENT")

    def test_all_green_human_assertions_still_not_permission(self):
        r = self.record
        r["attestations"] = {k: True for k in r["attestations"]}
        r["snapshot"]["eligible_email_count"] = 2
        for merchant in r["merchants"].values():
            merchant.update({k: True for k in merchant})
        result = proof.assess(r)
        self.assertIs(result["send_allowed"], False)
        self.assertFalse(result["human_attestations_cryptographically_verified"])
        self.assertFalse(result["real_delivery_proven_by_program"])
        for slot in ("03", "05"):
            self.assertEqual(result["commercial_issues"][slot]["state"], "HOLD_MERCHANT")

    def test_email_eligibility_is_not_derived_from_confirmed(self):
        result = proof.assess(self.record)
        self.assertIsNone(result["subscribers"]["email_eligible"])
        self.assertIn("NONADDITIVE", result["subscribers"]["counter_interpretation"])

    def test_no_customer_or_unsubscribe_url_in_output(self):
        output = json.dumps(proof.assess(self.record))
        for sensitive in ("@", "mailto:", "List-Unsubscribe:", "utm_source=", "http://"):
            self.assertNotIn(sensitive, output)

    def test_missing_merchant_approval_records_explicit_blockers(self):
        for edition in ("03", "05"):
            pending = proof.assess(self.record)["commercial_issues"][edition]["unverified"]
            self.assertEqual(len(pending), 5)
            self.assertIn("EMAIL_CHANNEL_PERMISSION_SPECIFIC_TO_PRODUCT", pending)

    def test_missing_postal_and_unsubscribe_are_blockers(self):
        b = proof.assess(self.record)["common_blockers"]
        self.assertIn("PUBLISHER_POSTAL_NOT_VERIFIED", b)
        self.assertIn("UNSUBSCRIBE_FUNCTION_NOT_VERIFIED", b)

    def test_real_mime_and_native_preview_remain_unknown(self):
        b = proof.assess(self.record)["common_blockers"]
        self.assertIn("RECEIVED_JETPACK_EMAIL_NOT_VERIFIED", b)
        self.assertIn("NATIVE_EDITOR_PREVIEW_NOT_VERIFIED", b)

    def test_welcome_configured_is_not_receipt(self):
        self.assertTrue(self.record["snapshot"]["welcome_configured"])
        self.assertIn("FOCUS_WELCOME_RECEIPT_NOT_VERIFIED", proof.assess(self.record)["common_blockers"])

    def test_unknown_root_keys_rejected_even_if_pii(self):
        self.record["subscriber_email"] = "private-person@example.invalid"
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_unknown_snapshot_keys_rejected(self):
        self.record["snapshot"]["token"] = "private-link"
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_unknown_attestation_fields_rejected(self):
        self.record["attestations"]["source_inbox"] = "address@example.invalid"
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_unknown_merchant_fields_rejected(self):
        self.record["merchants"]["03"]["affiliate_url"] = "https://merchant.example/secret"
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_merchant_06_rejected(self):
        self.record["merchants"]["06"] = dict(self.record["merchants"]["03"])
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_bool_as_count_rejected(self):
        self.record["snapshot"]["total"] = True
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_eligible_above_total_rejected(self):
        self.record["snapshot"]["eligible_email_count"] = 4
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_negative_count_rejected(self):
        self.record["snapshot"]["unconfirmed"] = -1
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_bad_format_rejected(self):
        self.record["snapshot"]["content_format"] = "send-full-on-publish"
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_bad_time_rejected(self):
        self.record["snapshot"]["captured_utc"] = "tomorrow"
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_string_attestation_rejected(self):
        self.record["attestations"]["final_founder_campaign_approval"] = "true"
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_invalid_merchant_approval_rejected(self):
        self.record["merchants"]["05"]["partner_account_acceptance"] = 1
        with self.assertRaises(proof.InvalidEvidence):
            proof.assess(self.record)

    def test_render_html_accessible_and_no_active_links(self):
        h = proof.html_board(proof.assess(self.record))
        for mark in ('lang="en"', 'name="viewport"', '<main>', '<h1>', '<ol', 'HOLD_UNSENT', 'HOLD_MERCHANT'):
            self.assertIn(mark, h)
        for risky in ('<script', '<form', '<iframe', 'href=', '<img', '<button'):
            self.assertNotIn(risky, h.lower())

    def test_render_text_hard_stop(self):
        t = proof.plaintext(proof.assess(self.record))
        self.assertIn("HOLD_UNSENT", t)
        self.assertIn("HOLD_MERCHANT", t)
        self.assertIn("not four", t.lower()) if "not four" in t.lower() else self.assertIn("NONADDITIVE", t)

    def test_no_cross_issue_paid_approval_spillover(self):
        self.record["merchants"]["03"] = {k: True for k in self.record["merchants"]["03"]}
        p = proof.assess(self.record)["commercial_issues"]
        self.assertEqual(p["03"]["unverified"], [])
        self.assertEqual(len(p["05"]["unverified"]), 5)
        self.assertEqual(p["03"]["state"], "HOLD_MERCHANT")

    def test_cli_generates_only_redacted_safe_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            f = Path(folder) / "snapshot.json"
            f.write_text(json.dumps(self.record), encoding="utf-8")
            dest = Path(folder) / "out"
            run = subprocess.run([sys.executable, str(R75 / "channel_proof.py"),
                                  "--input", str(f), "--output-dir", str(dest)],
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(sorted(p.name for p in dest.iterdir()),
                             ["channel-review.html", "channel-summary.json", "channel-summary.txt"])
            self.assertIn("HOLD_UNSENT", (dest / "channel-summary.txt").read_text())
            self.assertIs(json.loads((dest / "channel-summary.json").read_text())["send_allowed"], False)

    def test_cli_rejects_pii_without_echo(self):
        self.record["extra"] = "victim@example.invalid"
        with tempfile.TemporaryDirectory() as folder:
            f = Path(folder) / "sensitive.json"
            f.write_text(json.dumps(self.record), encoding="utf-8")
            run = subprocess.run([sys.executable, str(R75 / "channel_proof.py"),
                                  "--input", str(f), "--output-dir", str(Path(folder) / "out")],
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 2)
            self.assertNotIn("victim", run.stdout + run.stderr)
            self.assertNotIn("@", run.stdout + run.stderr)

    def test_user_approval_required_regardless_of_lint(self):
        output = proof.assess(self.record)
        self.assertIn("FINAL_FOUNDER_APPROVAL_NOT_EVIDENCED", output["common_blockers"])
        self.assertIs(output["send_allowed"], False)

if __name__ == "__main__":
    unittest.main()
